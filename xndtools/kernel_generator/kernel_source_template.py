""" Provides template object `source_template` for kernels C source code.
"""
# Author: Pearu Peterson
# Created: May 2018

from collections import defaultdict
from copy import deepcopy
from .templating import Template, Predicate, flatten
from . import utils
#
# Predicate functions
#

def has(key):
    return Predicate(lambda data: key in data)
def has_intent(intent):
    return Predicate(lambda data: intent in data.get('intent', ()))
def type_is(typ):
    return Predicate(lambda data: data.get('type') == typ)
def kind_is(kind):
    return Predicate(lambda data: data.get('kind') == kind)
def arraytype_is(arraytype):
    return Predicate(lambda data: data.get('arraytype') == arraytype)
is_symbolic = arraytype_is('symbolic')
is_variable = arraytype_is('variable')
debug = Predicate(lambda data: data.get('debug', False))
is_scalar = Predicate(lambda data: not (data.get('left_modifier') or data.get('right_modifier')))
is_scalar_ptr = Predicate(lambda data: data.get('left_modifier')=='*' and not data.get('right_modifier') and data.get('shape') is None)
is_array = Predicate(lambda data: (data.get('left_modifier')=='*' or data.get('right_modifier')=='[]') and data.get('shape') is not None)
is_argument = Predicate(lambda data: not data['name'].endswith('_return_value_'))
need_constraint = Predicate(lambda data: data.get('nout_symbols',0) > 0)

# See utils.py Prototype.set_argument_intent for interpretation:

is_input = Predicate(utils.is_intent_input)
is_inplace = Predicate(utils.is_intent_inplace)
is_inout = Predicate(utils.is_intent_inout)
is_output = Predicate(utils.is_intent_output)
is_hide = Predicate(utils.is_intent_hide)
is_input_output = Predicate(utils.is_intent_input_output)
is_inplace_output = Predicate(utils.is_intent_inplace_output)
is_inout_output = Predicate(utils.is_intent_inout_output)
is_inany = Predicate(utils.is_intent_inany)
is_outany = Predicate(utils.is_intent_outany)
is_fortran = Predicate(utils.is_fortran)
is_c = Predicate(utils.is_c)
is_tensor = Predicate(utils.is_tensor)
is_vector = Predicate(utils.is_vector)

#
# join functions
#

def join_kernels_list(lst):
    """
    Eliminates dublicated functions
    """
    return ''.join(sorted(set(lst)))

def join_constraints_list(lst):
    """
    Eliminates dublicated functions
    """
    return ''.join(sorted(set(lst)))

def sorted_list(lst):
    """
    Sorts list of statements taking into account dependencies.

    Input must be a list of 3-lists::
 
      [<statements>, <name>, <dependencies>]

    where ``<dependencies>`` is an comma separated list of names.
    """
    stmts = {}
    d = {}
    all_deps = set()
    for i in range(0,len(lst),3):
        stmt, name, deps = lst[i:i+3]
        stmts[name] = stmt
        if deps:
            deps = set(deps.replace(' ', '').split(','))
        else:
            deps = set()
        d[name] = deps
        all_deps.update(deps)
    for n in all_deps:
        if n not in d:
            d[n] = set()
    lst = [n for n in d if not d[n]]
    n_ = None
    while len(lst) < len(d):
        if len(lst) == n_:
            print('sorted_list:WARNING:circular dependence detected!: {!r}'.format(d))
            break
        n_ = len(lst)
        for n, deps in d.items():
            if n in lst:
                continue
            if not deps.difference(lst):
                lst.append(n)
                continue
    res = flatten([stmts[n] for n in lst if n in stmts])
    return res

def join_signatures_list(lst):
    # Collects kind_values of kernels
    # Appends NULL value.

    sig_kindmap = defaultdict(list)
    
    for signature in lst:
        name, sig, nout, kind_value = signature.split('|')
        sig_kindmap[name,sig,int(nout)].append(kind_value)

    lst = []
    for (name, sig, nout), kind_values in sig_kindmap.items():
        if nout>0:
            lst.append('{{ .name = "{}", .sig = "{}", .constraint = &gmk_{}_constraint, {} }}'.format(name, sig, name, ', '.join(kind_values)))
        else:
            lst.append('{{ .name = "{}", .sig = "{}", {} }}'.format(name, sig, ', '.join(kind_values)))
        kinds = [s.split('=')[0].strip()[1:] for s in kind_values]            
        print('  {}(sig="{}", {}) [nout={}]'.format(name, sig, ', '.join(kinds), nout))
        
    lst = lst + ['{ .name = NULL, .sig = NULL }']
    return ',\n  '.join(lst)

def join_dimension_list(lst):
    # Prepends ellipses dimension
    return ' * '.join(lst)

def join_shape_list(lst):
    return '(' + ') * ('.join(lst) + ')'

def join_short_doc_list(lst):
    kernels = defaultdict(list)
    kinds = defaultdict(list)
    for line in lst:
        name, sig, kind = line.split('@:@', 2)
        name = name.strip()
        sig = sig.strip()
        if sig not in kernels[name]:
            kernels[name].append(sig)
        kinds[name,sig].append(kind.strip())
    lines = []
    for name, signatures in kernels.items():
        sig_lines = []
        fmt = '{{:{}s}} [{{}}]'.format(max(70,max(map(len, signatures))))
        for sig in signatures:
            sig_lines.append(fmt.format(sig, ', '.join(kinds[name, sig])))
        lines.append('    {}:\n      {}'.format(name, '\n      '.join(sig_lines+[''])))
    return '\n'.join(lines)

def join_warnings_list(lst):
    lst = [line for line in lst if line]
    if lst:
        print('{1}\nCollected warnings:\n    {0}\n{1}'.format('\n    '.join(lst), '-'*60))
    return '\n'.join(lst)

#
# initialize functions
#

def initialize_source(data):
    """
    """
    
    
def initialize_kernels(data):
    """
    1. Sets argument shape dimension key (fixed and symbolic dimensons)
    2. Sets argument input_index, output_index.
    3. Extends arguments with function return value.
    4. Initialize various lists.
    5. Computes nin, nout, symbols for constraint function.
    """    
    dimension_symbols = 'NMLKPQRSVWXYZBCDFGHJAEIOU'
    dims_map = {}
    new_arguments = []
    input_index = 0
    output_index = 0
    output_args = []
    in_symbols = []
    out_symbols = []
    constraints = []
    for arg in data['arguments']:
        if (is_inany)(arg):
            arg['input_index'] = input_index
            input_index += 1
        if (is_outany)(arg):
            arg['output_index'] = output_index
            output_index += 1
            output_args.append(arg)
        shape = arg.get('shape')
        if shape is not None:
            for dim in shape:
                if dim['value'].isdigit(): # fixed dimension
                    dim['dimension'] = dim['value']
                else: # symbolic dimension
                    dims = dims_map.get(dim['value'])
                    if dims is None:
                        dims = dims_map[dim['value']] = dimension_symbols[len(dims_map)]
                        if is_outany(arg):
                            if dim['value'] in arg['depends']: # TODO: when dim['value'] is expression
                                constraints.append('gmk_shapes[{}] = {};'.format(len(out_symbols), dim['value']))
                            out_symbols.append(dims)
                        else:
                            in_symbols.append(dims)
                    dim['dimension'] = dims
            arg['nofitems'] = '('+')*('.join([dim['value'] for dim in shape]) +')'
    data['symbols'] = ', '.join('"'+s+'"' for s in in_symbols + out_symbols)
    data['nin_symbols'] = len(in_symbols)
    data['nout_symbols'] = len(out_symbols)
    data['constraints'] = '\n  '.join(constraints)
    if data['type'] != 'void':
        arg = dict(
            name = '{function_name}_return_value_'.format_map(data),
            intent = ('output',), # TODO: hide - ignore return value
        )
        for k in ['left_modifier', 'right_modifier', 'type']:
            if k in data:
                arg[k] = data[k]
        arg['output_index'] = output_index
        output_index += 1
        data['arguments'].append(arg)
        output_args.append(arg)
    for arg in output_args:
        arg['output_index'] += input_index

    # To suppress warnings when no input or no output, must be empty lists:
    data['arguments-list'] = []
    #data['initialize-list'] = []
    data['input_utype-list'] = []
    data['output_utype-list'] = []
    data['body-list'] = []

def initialize_argument(data):
    if is_scalar(data):
        data['cfmt'] = dict(int32='%d', int64='%ld', float32='%f', float64='%f')[data['type']]
    else:
        data['cfmt'] = '%p'
    
#
# Template strings
#
                    
c_source_template = '''\
/*
  This file is auto-generated.

  Module: {module_name}
  Kernels:

{short_doc-list}

 */
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <complex.h>
#include <inttypes.h>
#include "ndtypes.h"
#include "xnd.h"
#include "gumath.h"
#include "xndtools.h"

/* generated includes */
{includes}

#define GMK_FIXED_ARRAY_DATA(CTYPE, NAME) ((CTYPE *)(NAME.ptr + NAME.index * NAME.type->Concrete.FixedDim.itemsize))
#define GMK_SCALAR_DATA(CTYPE, NAME) ((CTYPE *)(NAME.ptr))

#define DEBUGMSG(MSG) printf("debug: " MSG);
#define DEBUGMSG1(MSG, VALUE) printf("debug: " MSG, VALUE);
#define DEBUGMSG2(MSG, VALUE1, VALUE2) printf("debug: " MSG, VALUE1, VALUE2);


/****************************************************************************/
/*                       Generated constraints                              */
/****************************************************************************/
{constraints-list}

/****************************************************************************/
/*                       Generated kernels                                  */
/****************************************************************************/
{kernels-list}

/****************************************************************************/
/*                       Test typemaps correctness                          */
/****************************************************************************/

static int
gmk_test_{module_name}_typemaps(ndt_context_t *ctx) {{
    int orig_size = 0;
    int normal_size = 0;
    {typemap_tests-list}
    return 0;
}}

/****************************************************************************/
/*                       Report wrapper call statistics                     */
/****************************************************************************/

static void
gmk_wrapper_stats_{module_name}(void) {{
    printf("----------------------------------------------------------------\\n");
    printf("Module: {module_name}\\n");
    printf("------+---------------------------------------------------------\\n");
    printf("Calls | Wrapper name\\n");
    printf("------+---------------------------------------------------------\\n");
    {report_wrapper_counter-list}
    printf("------+---------------------------------------------------------\\n");
}}


static const gm_kernel_init_t {module_name}_kernels[] = {{
  {signatures-list}
}};

/****************************************************************************/
/*                       Initialize kernel table                            */
/****************************************************************************/

int
gmk_init_{module_name}_kernels(gm_tbl_t *tbl, ndt_context_t *ctx)
{{
    const gm_kernel_init_t *k;

    if (gmk_test_{module_name}_typemaps(ctx) < 0) {{
         return -1;
    }}

    for (k = {module_name}_kernels; k->name != NULL; k++) {{
        if (gm_add_kernel(tbl, k, ctx) < 0) {{
            return -1;
        }}
    }}
    atexit(gmk_wrapper_stats_{module_name});
    return 0;
}}


'''

typemap_tests_template = '''
    orig_size = sizeof({orig_type});
    normal_size = sizeof({normal_type});
    if (orig_size != normal_size) {{
        ndt_err_format(ctx, NDT_RuntimeError,
                    "incorrect kernel configuration typemaps: sizeof({orig_type})!=sizeof({normal_type})");
        return -1;
    }}
'''

report_wrapper_counter_template = '''\
if (!{wrapper_name}_counter)
  printf("%5d | {wrapper_name}\\n", {wrapper_name}_counter);
'''

constraints_template = '''
static int 
{constraint_name}(int64_t *gmk_shapes, const void *gmk_args, ndt_context_t *gmk_ctx) {{
  {constraint_entering}
  {constraint_declarations-list}
  {constraints}
  {constraint_leaving}
  return 0;
}}
static const ndt_constraint_t 
gmk_{kernel_name}_constraint = {{ .f = {constraint_name}, .nin = {nin_symbols}, .nout = {nout_symbols}, .symbols={{ {symbols} }} }};
'''

kernel_template = '''
/*
  Kernel: {kernel_name}
  Signature: "{sig}"
  External function: {function_name}
  Configuration:
{kernel_repr}
*/
static int {wrapper_name}_counter = 0;
static int
{wrapper_name}(xnd_t gmk_stack[], ndt_context_t *gmk_ctx) {{
  {wrapper_name}_counter += 1;
  {entering}
  int gmk_success = 0;
  {declarations-list}
  {body-start-list}
  {return_value}{function_name}({arguments-list});
  {body-end-list}
  {leaving}
  return gmk_success;
}}
'''

strided_kernel_template = '''
static int
{wrapper_name}(char **args, intptr_t *dimensions, intptr_t *steps, void *data) {{
  {entering}
  int gmk_success = 0;
  NOT_IMPLEMENTED_KIND_{kind}_for_{function_name};
  {leaving}
  return gmk_success;
}}
 '''

#
# Templates
#

source_template = Template(
    dict(c_source = c_source_template),
    initialize = initialize_source,
    join = {
        'kernels-list': join_kernels_list,
        'constraints-list': join_constraints_list,
        'signatures-list': join_signatures_list,
        'typemap_tests-list': '',
        'report_wrapper_counter-list': '',
        'short_doc-list': join_short_doc_list,
        'constraint_entering-list': '\n', # not used, to suppress warnigns
        'constraint_leaving-list': '\n',  # not used, to suppress warnigns
        'all_warnings-list': join_warnings_list,
    }
)

source_template['typemap_tests'] = Template(
    dict(
        typemap_tests = typemap_tests_template,
    )
    )

wrapper_name = 'gmk_{kernel_name}_{ellipses_name}_{arraytype}_{kind}_{function_name}'
constraint_name = 'gmk_{kernel_name}_constraint_func'
source_template['kernels'] = Template(
    dict(kernels = [
        (strided_kernel_template, kernel_template) * kind_is('Strided'),
    ],
         constraints = [
             constraints_template * need_constraint,
         ],
         constraint_entering = 'DEBUGMSG("Entering {constraint_name}\\n");' * debug,
         constraint_leaving = 'DEBUGMSG("Leaving {constraint_name}\\n");' * debug,
         
         signatures = '{kernel_name}|{sig}|{nout_symbols}|.{kind} = {wrapper_name}',
         report_wrapper_counter = report_wrapper_counter_template,
         short_doc = '{kernel_name} - "{oneline_description}" @:@ {sig} @:@ {kind}',
         entering = 'DEBUGMSG("Entering {wrapper_name}\\n");' * debug,
         leaving = 'DEBUGMSG("Leaving {wrapper_name}\\n");' * debug,
         all_warnings = '{warnings-list}',
    ),
    variables = dict(
        wrapper_name = wrapper_name,
        constraint_name = constraint_name,
        empty_input_utype = 'void',
        empty_output_utype = 'void',
        sig = '{input_utype-list|empty_input_utype} -> {output_utype-list| empty_output_utype}',
        return_value = ('{function_name}_return_value_ = ', '') * -type_is('void'),
        entering = ('DEBUGMSG("entering {}\\n");'.format(wrapper_name),'') * debug,
        leaving = ('DEBUGMSG("leaving {}\\n");'.format(wrapper_name),'') * debug,
    ),
    initialize = initialize_kernels,
    join = {'declarations-list': '\n  ',
            'body-start-list': '\n  ',
            'body-end-list': '\n  ',
            'body-list': '\n  ',
            'arguments-list': ', ',
            'cleanup-list': '\n  ',
            'input_utype-list': ', ',
            'output_utype-list': ', ',
            'constraint_declarations-list': ', ',
            'warnings-list': '\n',
    },
    sort = {
        'body-list': sorted_list,
        #'input_utype-list': postprocess_input_utype_list,
    }
)

source_template['kernels']['arguments'] = Template(
    dict(
        declarations = [
            (('{ctype} {name} = {ctype_zero};','{ctype} {name};')*has('ctype_zero') )* (is_scalar+is_scalar_ptr),
            '{ctype}* {name} = NULL;'*is_array,

            [('xnd_t gmk_input_{name} = gmk_stack[{input_index}];',
              'const xnd_t gmk_input_{name} = gmk_stack[{input_index}];')*(has('value')*(is_inplace+is_inout+is_inplace_output+is_inout_output)),
             'DEBUGMSG1("gmk_input_{name}.type=%s\\n", ndt_as_string(gmk_input_{name}.type, gmk_ctx));'*debug,
            ] * (is_inany),
            'const xnd_t gmk_output_{name} = gmk_stack[{output_index}];' * (is_outany),
        ],
        constraint_declarations = [
            # constraints can use scalar arguments to initialize shapes of output arrays
            '{ctype} {name} = *({ctype}*)(((xnd_t *)gmk_args)[{input_index}].ptr);' * is_inany*(is_scalar+is_scalar_ptr),
        ],
        warnings = [
            'inplace|inout has not effect: C scalar cannot be changed in-situ (in {kernel_name})' * (is_inplace+is_inout+is_inplace_output+is_inout_output)*is_scalar,
        ],
        #
        # body generates body-start-list and body-end-list, so all items must contain `...` !!!
        #
        body = [[
            # ==================================================
            #                   Scalar arguments
            # ==================================================
            [
                [
                    '{name} = {value};...'*(is_hide+is_output),
                    #'{name} = (xnd_is_na(&gmk_input_{name}) ? {value} : *GMK_SCALAR_DATA({ctype}, gmk_input_{name}));...'*(is_inany),
'''
if (xnd_is_na(&gmk_input_{name}))
  {name} = {value};
else
  {name} = *GMK_SCALAR_DATA({ctype}, gmk_input_{name});
...
''' * (is_input+is_input_output),
'''
if (xnd_is_na(&gmk_input_{name}))
{{
  xnd_set_valid(&gmk_input_{name});
  {name} = *GMK_SCALAR_DATA({ctype}, gmk_input_{name}) = {value};
}}
else
  {name} = *GMK_SCALAR_DATA({ctype}, gmk_input_{name});
...
''' * (is_inplace+is_inout+is_inplace_output+is_inout_output),
                ] * has('value'),
                [
                    '{name} = *GMK_SCALAR_DATA({ctype}, gmk_input_{name});...' * (is_inany),
                ] * -has('value'),
                [
                    '...*GMK_SCALAR_DATA({ctype}, gmk_input_{name}) = {name};' * (is_inplace+is_inout+is_inplace_output+is_inout_output)*is_scalar_ptr,
                    '...*GMK_SCALAR_DATA({ctype}, gmk_output_{name}) = {name};' * is_outany,
                ]
            ] * (is_scalar+is_scalar_ptr),
            # ==================================================
            #                   Array arguments
            # ==================================================
            [
                # --------------------------------------------------
                #                   Array arguments - input
                # --------------------------------------------------
                # C-kind means that all inputs are C-contiguous
                # Fortran-kind means that all inputs are F-contiguous
                # is-C means that particular input needs to be C-contiguous
                # is-Fortran means that particular input needs to be F-contiguous
                # (is_c + is_fortran) == True, If is_vector then is_c == True 
                [
                    '{name} = GMK_FIXED_ARRAY_DATA({ctype}, gmk_input_{name});...'*(kind_is('C')*is_c + kind_is('Fortran')*is_fortran + is_vector*(kind_is('C') + kind_is('Fortran'))),
                    '''\
bool gmk_{name}_copied = !ndt_{is_contiguous}(gmk_input_{name}.type);
if (gmk_{name}_copied)
  {name} = ({ctype}*){xndtools_copy}(&gmk_input_{name}, gmk_ctx);
else
  {name} = GMK_FIXED_ARRAY_DATA({ctype}, gmk_input_{name});
if ({name} != NULL) {{
...
  if (gmk_{name}_copied)
    free({name});
}} else gmk_success = -1; /* if ({name} != NULL) */
'''*(kind_is('Xnd') * (is_c+is_fortran)),
                    '''
{name} = ({ctype}*){xndtools_copy}(&gmk_input_{name}, gmk_ctx);
if ({name} != NULL) {{
...
  free({name});
}} else gmk_success = -1; /* if ({name} != NULL) */
''' * is_tensor * (kind_is('Fortran') * is_c + kind_is('C') * is_fortran),
                    '''NOTIMPLEMENTED_INPUT_STRIDED...''' * (kind_is('Strided') * is_c),   # Xnd handles it
                    '''NOTIMPLEMENTED_FORTRAN_INPUT_STRIDED...''' * (kind_is('Strided') * is_fortran), # Xnd handles it
                ] * is_input,
                # --------------------------------------------------
                #                   Array arguments - inout
                # --------------------------------------------------
                [
                    '{name} = GMK_FIXED_ARRAY_DATA({ctype}, gmk_input_{name});...'*(kind_is('C')*is_c + kind_is('Fortran')*is_fortran + is_vector*(kind_is('C') + kind_is('Fortran'))),
                    '''\
if (ndt_{is_contiguous}(gmk_input_{name}.type)) {{
  {name} = GMK_FIXED_ARRAY_DATA({ctype}, gmk_input_{name});
...
}} else {{
  ndt_err_format(gmk_ctx, NDT_ValueError, "intent inout argument `{name}` must be {contiguous} [{kernel_name}]");
  gmk_success = -1; /* if ({name} != NULL) */
}}
'''*(kind_is('Xnd') * (is_c+is_fortran)),
                    '''
if (0) {{
...
}}
ndt_err_format(gmk_ctx, NDT_ValueError, "incompatible {contiguous} inout tensor argument `{name}` with given kernel {kernel_name} kind");
gmk_success = -1;
''' * (is_tensor*(kind_is('Fortran')*is_c + kind_is('C') * is_fortran)),
                    '''NOTIMPLEMENTED_INOUT_STRIDED...''' * (kind_is('Strided')*is_c),
                    '''NOTIMPLEMENTED_FORTRAN_INOUT_STRIDED...''' * (kind_is('Strided') * is_fortran),
                  ] * is_inout,
            # --------------------------------------------------
            #                   Array arguments - inplace
            # --------------------------------------------------
                [
                    '{name} = GMK_FIXED_ARRAY_DATA({ctype}, gmk_input_{name});...'*(kind_is('C')*is_c + kind_is('Fortran')*is_fortran + is_vector*(kind_is('C') + kind_is('Fortran'))),
                    '''\
{name} = ({ctype}*){xndtools_copy}(&gmk_input_{name}, gmk_ctx);
if ({name} != NULL) {{
...
  {xndtools_inv_copy}((const char*){name}, &gmk_input_{name});
  free({name});
}} else gmk_success = -1; /* if ({name} != NULL) */
''' * (is_tensor * ((kind_is('Fortran') * is_c + kind_is('C') * is_fortran))),
                '''\
bool gmk_{name}_copied = !ndt_{is_contiguous}(gmk_input_{name}.type);
if (gmk_{name}_copied)
  {name} = ({ctype}*){xndtools_copy}(&gmk_input_{name}, gmk_ctx);
else
  {name} = GMK_FIXED_ARRAY_DATA({ctype}, gmk_input_{name});
if ({name} != NULL) {{
...
  if (gmk_{name}_copied) {{
    {xndtools_inv_copy}((const char*){name}, &gmk_input_{name});
    free({name});
  }}
}} else gmk_success = -1; /* if ({name} != NULL) */
                ''' * ((kind_is('Xnd') * (is_c + is_fortran))),
                    '''NOTIMPLEMENTED_INPLACE_STRIDED...''' * (kind_is('Strided') * is_c),
                    '''NOTIMPLEMENTED_FORTRAN_INPLACE_STRIDED...''' * (kind_is('Strided') * is_fortran),
                ] * is_inplace,
                # --------------------------------------------------
                #                   Array arguments - input_output
                # --------------------------------------------------
                [
                    '''\
{name} = GMK_FIXED_ARRAY_DATA({ctype}, gmk_output_{name});
xndtools_cpy((char*){name}, &gmk_input_{name}, ndt_{is_contiguous}(gmk_input_{name}.type));
...'''*(kind_is('C')*is_c + kind_is('Fortran')*is_fortran + is_vector*(kind_is('C') + kind_is('Fortran'))),                    
                    '''\
bool gmk_{name}_transpose = !ndt_{is_contiguous}(gmk_output_{name}.type);
if (gmk_{name}_transpose)
  {name} = ({ctype}*)malloc(xndtools_fixed_nbytes(&gmk_output_{name}));
else
  {name} = GMK_FIXED_ARRAY_DATA({ctype}, gmk_output_{name}); // C-contiguous

if ({name} != NULL) {{
  xndtools_cpy((char*){name}, &gmk_input_{name}, !ndt_{is_contiguous}(gmk_input_{name}.type));
...
  if (gmk_{name}_transpose) {{
     {xndtools_inv_copy}((const char*){name}, &gmk_output_{name});
     free({name});
  }}  
}} else gmk_success = -1; /* if ({name} != NULL) */
'''*(kind_is('Xnd') * (is_c+is_fortran)),
                    '''\
{name} = ({ctype}*){xndtools_copy}(&gmk_input_{name}, gmk_ctx);
if ({name} != NULL) {{
...
  {xndtools_inv_copy}((const char*){name}, &gmk_output_{name});
  free({name});
}} else gmk_success = -1; /* if ({name} != NULL) */
''' * is_tensor * (kind_is('Fortran') * is_c + kind_is('C') * is_fortran),
                    '''NOTIMPLEMENTED_INPUT_OUTPUT_STRIDED...''' * (kind_is('Strided') * is_c),   # Xnd handles this
                    '''NOTIMPLEMENTED_FORTRAN_INPUT_OUTPUT_STRIDED...''' * (kind_is('Strided') * is_fortran), # Xnd handles this
                ] * is_input_output,
            # --------------------------------------------------
            #                   Array arguments - inplace_output
            # --------------------------------------------------
                [
                    '''\
{name} = GMK_FIXED_ARRAY_DATA({ctype}, gmk_input_{name});
...
{xndtools_inv_copy}((const char*){name}, &gmk_output_{name});
'''*(kind_is('C')*is_c + kind_is('Fortran')*is_fortran + is_vector*(kind_is('C') + kind_is('Fortran'))),
                    '''\
bool gmk_{name}_input_is_contiguous = ndt_{is_contiguous}(gmk_input_{name}.type);
if (!gmk_{name}_input_is_contiguous)
  {name} = ({ctype}*){xndtools_copy}(&gmk_input_{name}, gmk_ctx);
else
  {name} = GMK_FIXED_ARRAY_DATA({ctype}, gmk_input_{name});
if ({name} != NULL) {{
...
  {xndtools_inv_copy}((const char*){name}, &gmk_output_{name});
  if (!gmk_{name}_input_is_contiguous) {{
    {xndtools_inv_copy}((const char*){name}, &gmk_input_{name});
    free({name});
  }}
}} else gmk_success = -1; /* if ({name} != NULL) */
'''*(kind_is('Xnd') * (is_c+is_fortran)),
                    '''\
{name} = ({ctype}*){xndtools_copy}(&gmk_input_{name}, gmk_ctx);
if ({name} != NULL) {{
...
  {xndtools_inv_copy}((const char*){name}, &gmk_output_{name});
  {xndtools_inv_copy}((const char*){name}, &gmk_input_{name});
  free({name});
}} else gmk_success = -1; /* if ({name} != NULL) */
''' * (is_tensor * ((kind_is('Fortran') * is_c + kind_is('C') * is_fortran))),
                    '''NOTIMPLEMENTED_INPLACE_OUTPUT_STRIDED...''' * (kind_is('Strided')*is_c),               # Xnd handles this
                    '''NOTIMPLEMENTED_FORTRAN_INPLACE_OUTPUT_STRIDED...''' * (kind_is('Strided')*is_fortran), # Xnd handles this
                    ] * is_inplace_output,
            # --------------------------------------------------
            #                   Array arguments - inout_output
            # --------------------------------------------------
                [
                    '''\
{name} = GMK_FIXED_ARRAY_DATA({ctype}, gmk_input_{name});
...
{xndtools_inv_copy}((const char*){name}, &gmk_output_{name});
'''*(kind_is('C')*is_c + kind_is('Fortran')*is_fortran + is_vector*(kind_is('C') + kind_is('Fortran'))),
                    '''\
if (ndt_{is_contiguous}(gmk_input_{name}.type)) {{
  {name} = GMK_FIXED_ARRAY_DATA({ctype}, gmk_input_{name});
...
  {xndtools_inv_copy}((const char*){name}, &gmk_output_{name});
}} else {{
  ndt_err_format(gmk_ctx, NDT_ValueError, "intent inout-output argument `{name}` must be {contiguous} [{kernel_name}]");
  gmk_success = -1; /* if ({name} != NULL) */
}}
'''*(kind_is('Xnd') * (is_c+is_fortran)),
                    '''
if (0) {{
...
}}
ndt_err_format(gmk_ctx, NDT_ValueError, "incompatible {contiguous} inout-output tensor argument `{name}` with given kernel {kernel_name} kind");
gmk_success = -1;
''' * (is_tensor*(kind_is('Fortran')*is_c + kind_is('C') * is_fortran)),
                    '''NOTIMPLEMENTED_INOUT_OUTPUT_STRIDED...''' * (kind_is('Strided')*is_c),
                    '''NOTIMPLEMENTED_FORTRAN_INOUT_OUTPUT_STRIDED...''' * (kind_is('Strided')*is_fortran),
                ] * is_inout_output,
            # --------------------------------------------------
            #                   Array arguments - output
            # --------------------------------------------------
                [
                    '{name} = GMK_FIXED_ARRAY_DATA({ctype}, gmk_output_{name});...'*(kind_is('C')*is_c + kind_is('Fortran')*is_fortran + is_vector*(kind_is('C') + kind_is('Fortran'))),
                    '''
{name} = malloc(xndtools_fixed_nbytes(&gmk_output_{name}));
if ({name} != NULL) {{
...
  {xndtools_inv_copy}((const char*){name}, &gmk_output_{name});
  free({name});
}} else gmk_success = -1; /* if ({name} != NULL) */
''' * (is_tensor * ((kind_is('Fortran') * is_c + kind_is('C') * is_fortran))),
                    '''\
bool gmk_{name}_transpose = !ndt_{is_contiguous}(gmk_output_{name}.type);
if (gmk_{name}_transpose)
  {name} = ({ctype}*)malloc(xndtools_fixed_nbytes(&gmk_output_{name}));
else
  {name} = GMK_FIXED_ARRAY_DATA({ctype}, gmk_output_{name});
if ({name} != NULL) {{
...
  if (gmk_{name}_transpose) {{
     {xndtools_inv_copy}((const char*){name}, &gmk_output_{name});
     free({name});
  }}
}} else gmk_success = -1; /* if ({name} != NULL) */
''' * ((kind_is('Xnd') * (is_c + is_fortran))),                    
                    '''NOTIMPLEMENTED_OUTPUT_STRIDED...''' * (kind_is('Strided') * is_c),
                    '''NOTIMPLEMENTED_FORTRAN_OUTPUT_STRIDED...''' * (kind_is('Strided') * is_fortran),

                ] * is_output,
            # --------------------------------------------------
            #                   Array arguments - hide
            # --------------------------------------------------
                    '''\
                    size_t gmk_{name}_size = {shape_product};
                    {name} = ({ctype}*)malloc(sizeof({ctype})*gmk_{name}_size);
...
free({name});
''' * is_hide
            ]*(is_array*-has('value')),
        ],
                '{name}',
                ('{depends}','') * has('depends')
        ], # 3-list is handled by sorted_list
        arguments = ('&{name}', '{name}') * is_scalar_ptr * is_argument,
        input_utype = ('{sigdims}?{type}' * is_inany,'{sigdims}{type}' * is_inany)*has('value'),
        output_utype = '{sigdims}{type}' * is_outany,
    ),
    variables = dict(
        fortran = ('!', '') * is_fortran,
        is_contiguous = ('is_f_contiguous', 'is_c_contiguous') * is_fortran,
        contiguous = ('F-contiguous', 'C-contiguous') * is_fortran,
        xndtools_copy = ('xndtools_fcopy', 'xndtools_copy') * is_fortran,
        xndtools_inv_copy = ('xndtools_inv_fcopy', 'xndtools_inv_copy') * is_fortran,
        #xndtools_fcopy = ('xndtools_copy', 'xndtools_fcopy') * is_fortran,
        sigdims = ('{ellipses}{fortran}{dimension-list} * ', '{ellipses}')*has('dimension-list'),
        wrapper_name = wrapper_name,
        shape_product = '{shape-list}',
    ),
    initialize = initialize_argument,
    join = {'dimension-list': join_dimension_list,
            'shape-list': join_shape_list,
    }
)

source_template['kernels']['arguments']['shape'] = Template(
    dict(
        dimension = ('{dimension}', 'var') * is_symbolic,
        shape = '{value}',
    )
)

#
#
#

def test():

    kernels = [
        {'argument_map': {'n': 0, 'r': 2, 'x': 1},
         'kind' : ['Xnd'][0],
         
         'arguments': [{'depends': 'x',  # TODO
                        'intent': ('hide',),
                        'name': 'n',
                        'type': 'long',
                        'value': 'xnd_fixed_shape_at(&gmk_x, 0)'},
                       {'intent': ('input',),
                        'left_modifier': '*',
                        'name': 'x',
                        'shape': [dict(value='n')],
                        'type': 'double'},
                       {'intent': ('input',),
                        'left_modifier': '*',
                        'name': 'y',
                        'shape': [dict(value='n+5'), dict(value='n')],
                        'type': 'double'},
                       {'intent': ('hide', 'output'),
                        'left_modifier': '*',
                        'name': 'r',
                        'type': 'double'}],
         'description': 'Compute the sum of x elements.',
         'kernel_name': 'example_sum',
         'function_name': 'd_example_sum',
         'type': 'void'},
        {
            'kind' : ['Xnd'][0],
            'arguments' : [],
            'kernel_name' : 'foo',
            'function_name' : 'd_foo',
            'type' : 'double',
        }
    ]
    
    data = dict(module_name = 'example',
                typemap_tests = [dict(orig_type='double', normal_type='float64'),
                                 dict(orig_type='int', normal_type='int32'),
                ],
                kernels = kernels)

    source = source_template(data)
    print (source['c_source'])
    
if __name__ == '__main__':
    test()
