""" Provides: get_module_data, generate_kernel.
"""
# Author: Pearu Peterson
# Created: April 2018

import os
import pprint
from collections import defaultdict
from .readers import PrototypeReader, load_kernel_config
from .utils import NormalizedTypeMap, split_expression

kernels_template = '''
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <complex.h>
#include <inttypes.h>
#include "ndtypes.h"
#include "xnd.h"
#include "gumath.h"

/* generated includes */
{includes}

/* generated header code */
{header_code}

/* generated kernel functions code */
{kernel_functions}

static const gm_kernel_init_t {modulename}_kernels[] = {{
/* generated signatures */
    {kernel_signatures}
}};

/****************************************************************************/
/*                       Initialize kernel table                            */
/****************************************************************************/

int
gmk_init_{modulename}_kernels(ndt_context_t *ctx)
{{
    const gm_kernel_init_t *k;

    for (k = {modulename}_kernels; k->name != NULL; k++) {{
        if (gm_add_kernel(k, ctx) < 0) {{
            return -1;
        }}
    }}

    return 0;
}}
'''

signature_template = '''{{ .name = "{functionname}", .sig = "{sig}", .vectorize = false, .{kind} = {wrappername} }}'''

kernel_template = '''
/*
 * {functionname}.
 *
 * Signature:
 *   "{sig}"
 *
 */
static int
{wrappername}(xnd_t gmk_stack[], ndt_context_t *gmk_ctx)
{{

    {declarations}
    {pre_call_code}
    {call}
    {returns}
    {post_call_code}

    return 0;
}}

'''

def get_module_data(config_file, package=None):
    config = load_kernel_config(config_file)

    reader = PrototypeReader()    
    current_module = None
    include_dirs = []
    sources = []
    kernel_functions = []
    kernel_signatures = []
    for section in config.sections():
        if section.startswith('MODULE'):
            assert current_module is None
            modulename = section.split(None, 1)[1]
            current_module = config[section]

            typemap = NormalizedTypeMap()
            for line in current_module.get('typemaps', '').splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                left, right = line.split(':', 1)
                typemap[left.strip()] = right.strip()

            for line in current_module.get('include_dirs', '').splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                include_dirs.append(line)

            for line in current_module.get('sources', '').splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                sources.append(line)
                
        elif section.startswith('FUNCTION'):
            f = config[section]
            if f.get('skip', None):
                #print ('skipping', section)
                continue
            functionname = section.split(maxsplit=1)[1].strip()
            description = f.get('description','')

            prototypes = reader(f['prototypes'])

            # set argument intents
            input_arguments = split_expression(f.get('input_arguments', ''))
            output_arguments = split_expression(f.get('output_arguments', ''))
            inplace_arguments = split_expression(f.get('inplace_arguments', ''))
            hide_arguments = split_expression(f.get('hide_arguments', ''))
            print(functionname, input_arguments, inplace_arguments, output_arguments, hide_arguments)
            for name in input_arguments:
                for prototype in prototypes:
                    prototype.set_argument_intent(name, 'input')
            for name in inplace_arguments:
                for prototype in prototypes:
                    prototype.set_argument_intent(name, 'inplace')
            for name in output_arguments:
                for prototype in prototypes:
                    prototype.set_argument_intent(name, 'output')
            for name in hide_arguments:
                for prototype in prototypes:
                    prototype.set_argument_intent(name, 'hide')
                    
            # resolve argument shapes
            for name_shape in [a.strip() for a in f.get('dimension', '').split(',') if a]:
                i = name_shape.index('(')
                if i==-1 or name_shape[-1] !=')':
                    print('cannot determine shape from {!r}. IGNORING.'.format(name_shape))
                    continue
                name = name_shape[:i].strip()
                shape = [a.strip() for a in name_shape[i+1:-1].split(',')]
                for prototype in prototypes:
                    prototype.set_argument_shape(name, shape)


            class Counter:
                def __init__(self):
                    self._counter = 0
                def __iadd__(self, other):
                    self._counter += other
                def __str__(self):
                    return str(self._counter)
            
            for i, prototype in enumerate(prototypes):
                if not i:
                    from pprint import pprint
                    pprint(prototype)
                    
                initializations = defaultdict(list)
                declarations = defaultdict(list)
                xnd_declarations = []
                call_arguments = []
                debug_initializations = []
                return_statements = []
                input_counter = Counter()
                output_counter = Counter()
                def declare(arg, counter):
                    ctype = arg['type']
                    name = arg['name']
                    value = arg.get('value', '')
                    params = dict(name=name,
                                  index=counter,
                                  ctype=ctype,
                                  value = value,
                    )
                    if arg.is_scalar_ptr or arg.is_scalar:
                        r1 = 'const xnd_t gmk_{name} = gmk_stack[{index}];'
                        r2 = '{ctype} {name};'
                    elif arg.is_array:
                        r1 = 'const xnd_t gmk_{name} = gmk_stack[{index}];'
                        r2 = '{ctype} *{name} = NULL;'
                    else:
                        raise NotImplementedError(repr(arg))

                    if counter is not None: # input,inplace,output has counters
                        if value:
                            if arg.is_scalar_ptr or arg.is_scalar:
                                r3 = '{name} = (xnd_is_na(&gmk_{name}) ? {value} : *(({ctype} *)gmk_{name}.ptr));'
                            elif arg.is_array:
                                r3 = '{name} = (xnd_is_na(&gmk_{name}) ? {value} : (({ctype} *)gmk_{name}.ptr));'
                            else:
                                raise NotImplementedError(repr(arg))
                        else:
                            if arg.is_scalar_ptr or arg.is_scalar:
                                r3 = '{name} = *(({ctype} *)gmk_{name}.ptr);'
                            elif arg.is_array:
                                r3 = '{name} = (({ctype} *)gmk_{name}.ptr);'
                            else:
                                raise NotImplementedError(repr(arg))
                        if arg.is_scalar_ptr and arg.is_intent_hide_output:
                            return_statements.append('*(({ctype} *)gmk_{name}.ptr) = {name};'.format(**params))
                        xnd_declarations.append(r1.format(**params))
                        counter += 1
                    else:
                        if value:
                            r3 = '{name} = {value};'

                        else:
                            r3 = ''
                            print('WARNING: {name!r} is uninitialized.'.format(**params))
                    if arg.is_scalar_ptr or arg.is_scalar:
                        debug_initializations.append('printf("{name}=%d\\n", {name});'.format(**params))
                    declarations[name].append(r2.format(**params))
                    initializations[name].append(r3.format(**params))
                    
                    if arg.is_scalar_ptr:
                        call_arguments.append('&{name}'.format(**params))
                    elif arg.is_scalar or arg.is_array:
                        call_arguments.append('{name}'.format(**params))
                    else:
                        raise NotImplementedError(repr(arg))
                        
                call_args = []
                initialize_args = []
                ndtype_arg_list = []
                ndtype_ret_list = []

                
                for arg in prototype['arguments']:
                    name = arg['name']
                    sigtype = typemap(arg['type'])
                    shape = arg.get('shape')
                    prefix = '... * '
                    #prefix = ''
                    if shape is not None:
                        shape = [d.upper() for d in shape]
                        prefix += ' * '.join(shape) + ' * '
                    if arg.is_intent_input:
                        ndtype_arg_list.append('{}{}'.format(prefix, sigtype))
                        declare(arg, input_counter)
                    elif arg.is_intent_inplace:
                        ndtype_arg_list.append('{}{}'.format(prefix, sigtype))
                        declare(arg, input_counter)
                    elif arg.is_intent_output and 0:
                        ndtype_ret_list.append('{}{}'.format(prefix, sigtype))
                    elif arg.is_intent_hide:
                        declare(arg, None)
                    elif arg.is_intent_hide_output:
                        ndtype_ret_list.append('{}{}'.format(prefix, sigtype))
                        declare(arg, input_counter)
                    else:
                        raise NotImplemented('arg intent={!r}'.arg.get('intent'))                    
                    if arg.is_scalar:
                        if arg.is_intent_input:
                            pass
                        elif arg.is_intent_inplace:
                            pass
                        elif arg.is_intent_output:
                            pass
                        elif arg.is_intent_hide:
                            pass
                        elif arg.is_intent_hide_output:
                            pass
                        else:
                            raise NotImplemented('arg intent={!r}'.arg.get('intent'))
                    elif arg.is_scalar_ptr:
                        if arg.is_intent_input:
                            pass
                        elif arg.is_intent_inplace:
                            pass
                        elif arg.is_intent_output and 0: # this is input and output, not supported by ndtypes/gumath
                            pass
                        elif arg.is_intent_hide:
                            pass
                        elif arg.is_intent_hide_output:
                            pass
                        else:
                            raise NotImplemented('arg intent={!r}'.arg.get('intent'))
                    elif arg.is_array:
                        if arg.is_intent_input:
                            pass
                        elif arg.is_intent_inplace:
                            pass
                        elif arg.is_intent_output:
                            pass
                        elif arg.is_intent_hide:
                            pass
                        elif arg.is_intent_hide_output:
                            pass
                        else:
                            raise NotImplemented('arg intent={!r}'.arg.get('intent'))
                    else:
                        print ('arg={!r}'.format(arg))
                        raise NotImplementedError('arg is not scalar|scalar_ptr|array')
                    continue

                decl_statements = []
                init_statements = []
                for n in prototype.get_sorted_arguments():
                    decl_statements.extend(declarations[n])
                    init_statements.extend(initializations[n])
                #debug_initializations = [] # disable debug statements
                declarations = '\n    '.join(xnd_declarations + [''] + decl_statements + [''] + init_statements + [''] + debug_initializations)

                call_name = prototype['name']
                
                call_args = ', '.join(call_arguments)
                if prototype['type'] == 'void':
                    call = '{}({});'.format(call_name, call_args)
                else:
                    call = '*({} *)out.ptr = {}({});'.format(prototype['type'],call_name, call_args)
                
                sig = '{} -> {}'.format(', '.join(ndtype_arg_list), ', '.join(ndtype_ret_list or ['void']))
                kind = 'Xnd' # C, Fortran, Strided, Xnd
                kernel_data = dict(
                    kind = kind,
                    functionname = functionname,
                    wrappername = 'gmk_fixed_{}_{}_{}_{}'.format(kind, modulename, functionname, call_name),
                    pre_loop_code = f.get('pre_loop_code',''),
                    pre_call_code = f.get('pre_call_code',''),
                    declarations = declarations,
                    returns = '\n    '.join(return_statements),
                    post_call_code = f.get('post_call_code',''),
                    post_loop_code = f.get('post_loop_code',''),
                    call = call,
                    sig = sig,
                )
                kernel_signatures.append(signature_template.format(**kernel_data))
                kernel_functions.append(kernel_template.format(**kernel_data))



    kernel_signatures.append('{ .name = NULL, .sig = NULL }')
    l = []
    for h in current_module.get('includes','').split():
        h = h.strip()
        if h:
            l.append('#include "{}"'.format(h))

    if package is None:
        fullname = modulename
        extmodulename = modulename
    else:
        fullname = package + '.' + modulename
        extmodulename = package + '_' + modulename
            
    module_data = dict(
        fullname = fullname,
        modulename = modulename,
        extmodulename = extmodulename,
        includes = '\n'.join(l),
        header_code = current_module.get('header_code', ''),
        include_dirs = include_dirs,
        sources = sources,
        kernel_functions = '\n'.join(kernel_functions),
        kernel_signatures = ',\n    '.join(kernel_signatures),
    )

    return module_data

def generate_kernel(config_file,
                    target_file = None,
                    source_dir = ''):
    module_data = get_module_data(config_file)
    kernels_source = kernels_template.format(**module_data)
    if target_file is None:
        target_file = os.path.join(source_dir, '{modulename}-kernels.c'.format(**module_data))
    f = open(target_file, 'w')
    f.write(kernels_source)
    f.close()
    print('Created {!r}'.format(target_file))

    return dict(config_file = config_file,
                sources = [target_file] + module_data['sources'])

    

