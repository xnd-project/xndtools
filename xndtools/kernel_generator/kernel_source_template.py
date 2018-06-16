""" Provides template object `source_template` for kernels C source code.
"""
# Author: Pearu Peterson
# Created: May 2018

from collections import defaultdict
from copy import deepcopy
from .templating import Template, Predicate, flatten

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
is_array = Predicate(lambda data: data.get('left_modifier')=='*' and data.get('shape') is not None)
is_argument = Predicate(lambda data: not data['name'].endswith('_return_value_'))
is_input = has_intent('input')
#is_hide = -is_input
is_output = has_intent('output')


#
# join functions
#

def join_kernels_list(lst):
    """
    Eliminates dublicated functions
    """
    return ''.join(set(lst))

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
        name, sig, kind_value = signature.split('|', 3)
        sig_kindmap[name,sig].append(kind_value)

    lst = []
    for (name, sig), kind_values in sig_kindmap.items():
        lst.append('{{ .name = "{}", .sig = "{}", {} }}'.format(name, sig, ', '.join(kind_values)))
        kinds = [s.split('=')[0].strip()[1:] for s in kind_values]            
        print('  {}(sig="{}", {})'.format(name, sig, ', '.join(kinds)))
        
    lst = lst + ['{ .name = NULL, .sig = NULL }']
    return ',\n  '.join(lst)

def join_dimension_list(lst):
    # Prepends ellipses dimension
    return ' * '.join(lst)

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
    """    
    dimension_symbols = 'NMLKPQRSVWXYZBCDFGHJAEIOU'
    dims_map = {}
    new_arguments = []
    input_index = 0
    output_index = 0
    output_args = []
    for arg in data['arguments']:
        if is_input(arg):
            arg['input_index'] = input_index
            input_index += 1
        if is_output(arg):
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
                    dim['dimension'] = dims
            arg['nofitems'] = '('+')*('.join([dim['value'] for dim in shape]) +')'
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
        
    # must be empty lists:
    data['arguments-list'] = []
    #data['initialize-list'] = []
    data['input_utype-list'] = []
    data['output_utype-list'] = []

def initialize_argument(data):
    if is_scalar(data):
        data['cfmt'] = dict(int32='%d', int64='%ld', float32='%f', float64='%f')[data['type']]
    else:
        data['cfmt'] = '%p'
    
#
# Template strings
#
                    
c_source_template = '''
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

/* generated kernel functions */
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

notimpl_kernel_template = '''
static int
{wrapper_name}(xnd_t gmk_stack[], ndt_context_t *gmk_ctx) {{
  NOT_IMPLEMENTED_KIND_{kind}_for_{function_name};
}}
'''

kernel_template = '''
static int
{wrapper_name}(xnd_t gmk_stack[], ndt_context_t *gmk_ctx) {{
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
        'signatures-list': join_signatures_list,
        'typemap_tests-list': ''
    }
)

source_template['typemap_tests'] = Template(
    dict(
        typemap_tests = typemap_tests_template,
    )
    )

wrapper_name = 'gmk_{arraytype}_{kind}_{function_name}'
source_template['kernels'] = Template(
    dict(kernels = [
        (strided_kernel_template, kernel_template) * kind_is('Strided'),
    ],
         signatures = '{kernel_name}|{sig}|.{kind} = {wrapper_name}',
    ),
    variables = dict(
        wrapper_name = wrapper_name,
        sig = '{input_utype-list} -> {output_utype-list}',
        return_value = ('{function_name}_return_value_ = ', '') * -type_is('void'),
        entering = ('DEBUGMSG("entering {}\\n");'.format(wrapper_name),'') * debug,
        leaving = ('DEBUGMSG("leaving {}\\n");'.format(wrapper_name),'') * debug,
    ),
    initialize = initialize_kernels,
    join = {'declarations-list': '\n  ',
            'body-start-list': '\n  ',
            'body-end-list': '\n  ',
            'arguments-list': ', ',
            'cleanup-list': '\n  ',
            'input_utype-list': ', ',
            'output_utype-list': ', ',
    },
    sort = {
        'body-list': sorted_list,
    }
)

source_template['kernels']['arguments'] = Template(
    dict(
        declarations = ['{ctype} {name};' * (is_scalar+is_scalar_ptr),
                        '{ctype}* {name} = NULL;'*is_array,
                        ['const xnd_t gmk_input_{name} = gmk_stack[{input_index}];',
                         'DEBUGMSG1("gmk_input_{name}.type=%s\\n", ndt_as_string(gmk_input_{name}.type, gmk_ctx));'*debug,
                        ] * is_input,
                        'const xnd_t gmk_output_{name} = gmk_stack[{output_index}];' * is_output,
        ],
        # body generates body-start-list and body-end-list, so all items must contain `...`
        body = [[
            '{name} = (xnd_is_na(&gmk_input_{name}) ? {value} : *GMK_SCALAR_DATA({ctype}, gmk_input_{name}));...'*(is_input*has('value')*(is_scalar+is_scalar_ptr)),
            '{name} = *GMK_SCALAR_DATA({ctype}, gmk_input_{name});...'*(is_input*-has('value')*(is_scalar+is_scalar_ptr)),
            '{name} = GMK_FIXED_ARRAY_DATA({ctype}, gmk_input_{name});...'*(is_input*-has('value')*is_array*(kind_is('C')+kind_is('Fortran'))),
            '''\
{name} = ({ctype}*)xndtools_copy(&gmk_input_{name}, gmk_ctx);
if ({name} != NULL) {{
...
  free({name});
}} else gmk_success = -1;
'''*(is_input*-has('value')*is_array*kind_is('Xnd')),
            '{name} = {value};...'*(-is_input*has('value')*(is_scalar+is_scalar_ptr)),
            '...*GMK_SCALAR_DATA({ctype}, gmk_output_{name}) = {name};' * (is_output*(is_scalar+is_scalar_ptr)),            
        ],
                '{name}',
                ('{depends}','') * has('depends')
        ], # 3-list is handled by sorted_list
        arguments = ('&{name}', '{name}') * is_scalar_ptr * is_argument,
        input_utype = '{sigdims}{type}' * is_input,
        output_utype = '{sigdims}{type}' * is_output,
    ),
    variables = dict(
        sigdims = ('{ellipses}{dimension-list} * ', '{ellipses}')*has('dimension-list'),
        
    ),
    initialize = initialize_argument,
    join = {'dimension-list': join_dimension_list}
)

source_template['kernels']['arguments']['shape'] = Template(
    dict(
        dimension = ('{dimension}', 'var') * is_symbolic
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
