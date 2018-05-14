""" Provides: generate_kernel, get_module_data.
"""
# Author: Pearu Peterson
# Created: April 2018

import os
from copy import deepcopy
from .readers import PrototypeReader, load_kernel_config
from .utils import NormalizedTypeMap, split_expression
from .kernel_source_template import source_template

def apply_typemap(prototype, typemap, typemap_tests):
    orig_type = prototype['type']
    prototype['type'] = normal_type = typemap(orig_type)
    prototype['ctype'] = c_type = normal_type + '_t'
    if orig_type != normal_type:
        typemap_tests.add((orig_type, c_type))
    
    for arg in prototype['arguments']:
        orig_type = arg['type']
        arg['type'] = normal_type = typemap(orig_type)
        arg['ctype'] = c_type = normal_type + '_t'
        if orig_type != normal_type:
            typemap_tests.add((orig_type, c_type))
    
def generate_kernel(config_file,
                    target_file = None,
                    source_dir = ''):
    data = get_module_data(config_file)
    source = source_template(data)
    if target_file is None:
        target_file = os.path.join(source_dir, '{module_name}-kernels.c'.format(**data))
    f = open(target_file, 'w')
    f.write(source['c_source'])
    f.close()
    print('Created {!r}'.format(target_file))

    return dict(config_file = config_file,
                sources = [target_file] + data['sources'])

def get_module_data(config_file, package=None):
    config = load_kernel_config(config_file)
    reader = PrototypeReader()    
    current_module = None
    include_dirs = []
    sources = []
    kernels = []
    typemap_tests = set()
    
    default_kinds_value = 'Xnd' # TODO: move to command line options
    default_vectorize_value = 'false'  # TODO: move to command line options
    
    for section in config.sections():
        if section.startswith('MODULE'):
            assert current_module is None
            module_name = section.split(None, 1)[1]
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

            default_kinds = split_expression(current_module.get('kinds', default_kinds_value))
            default_vectorize = split_expression(current_module.get('vectorize', default_vectorize_value))
                
        elif section.startswith('KERNEL'):
            f = config[section]
            if f.get('skip', None):
                #print ('skipping', section)
                continue
            kernel_name = section.split(maxsplit=1)[1].strip()
            description = f.get('description','').strip()

            prototypes = reader(f['prototypes'])
            kinds = split_expression(f.get('kinds', ''))
            vectorize = split_expression(f.get('vectorize', ''))
            
            # set argument intents
            input_arguments = split_expression(f.get('input_arguments', ''))
            output_arguments = split_expression(f.get('output_arguments', ''))
            inplace_arguments = split_expression(f.get('inplace_arguments', ''))
            hide_arguments = split_expression(f.get('hide_arguments', ''))
                    
            # resolve argument shapes
            shape_map = {}
            
            for name_shape in split_expression(f.get('dimension', '')):
                i = name_shape.index('(')
                if i==-1 or name_shape[-1] !=')':
                    print('cannot determine shape from {!r}. IGNORING.'.format(name_shape))
                    continue
                name = name_shape[:i].strip()
                shape = [a.strip() for a in name_shape[i+1:-1].split(',')]
                shape_map[name] = shape

            # propagate prototypes to kernels
            for prototype in prototypes:
                prototype['kernel_name'] = kernel_name
                prototype['description'] = description
                prototype['function_name'] = prototype.pop('name')

                apply_typemap(prototype, typemap, typemap_tests)
                
                for name in input_arguments:
                    prototype.set_argument_intent(name, 'input')
                for name in inplace_arguments:
                    prototype.set_argument_intent(name, 'inplace')
                for name in output_arguments:
                    prototype.set_argument_intent(name, 'output')
                for name in hide_arguments:
                    prototype.set_argument_intent(name, 'hide')
                for name, shape in shape_map.items():
                    prototype.set_argument_shape(name, shape)

                for kind in kinds or default_kinds:
                    for vectorized in vectorize or default_vectorize:
                        kernel = deepcopy(prototype)
                        kernel['kind'] = kind
                        kernel['vectorized'] = vectorized
                        kernels.append(kernel)

    l = []
    for h in current_module.get('includes','').split():
        h = h.strip()
        if h:
            l.append('#include "{}"'.format(h))
            
    module_data = dict(
        module_name = module_name,
        includes = '\n'.join(l),
        #header_code = current_module.get('header_code', ''),
        include_dirs = include_dirs,
        sources = sources,
        kernels = kernels,
        typemap_tests = list([dict(orig_type=o[0], normal_type=o[1]) for o in typemap_tests]),
    )

    return module_data
