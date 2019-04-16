""" Provides: generate_kernel, get_module_data.
"""
# Author: Pearu Peterson
# Created: April 2018


import os
import sys
import re
import warnings
from glob import glob
from copy import deepcopy
from collections import defaultdict
import pprint
from .readers import PrototypeReader, load_kernel_config
from .utils import (NormalizedTypeMap, split_expression, intent_names,
                    prettify, resolve_path)
from .kernel_source_template import source_template


def update_argument_maps(expr, depends_map, values_map, shapes_map, arguments):
    if isinstance(expr, tuple):  # (<name>, <value|shape>)
        name, value = expr
        for n in re.findall(r'(\b[a-zA-Z_]\w*\b)', value):
            if n in arguments:
                if name not in depends_map[n]:  # avoid circular dependencies
                    depends_map[name].add(n)
    elif '=' in expr:  # <name>=<expr>
        name, value = expr.split('=', 1)
        name = name.strip()
        update_argument_maps((name, value), depends_map, values_map,
                             shapes_map, arguments)
        assert name not in values_map, repr((name, value, values_map[name]))
        values_map[name] = value
    elif '(' in expr:  # <name>(<shape-list>)
        i = expr.index('(')
        if expr[-1] != ')':
            raise ValueError(
                'cannot determine shape from {!r}. IGNORING.'.format(expr))
        name = expr[:i].strip()
        shape = [a.strip() for a in expr[i + 1:-1].split(',')]
        shapes_map[name] = shape
    else:  # <name>
        name = expr
    return name


def apply_typemap(prototype, typemap, typemap_tests):
    orig_type = prototype['type']

    prototype['type'] = normal_type = typemap(orig_type)
    # prototype['ctype'] = c_type = normal_type + '_t'
    c_type = normal_type + '_t'
    prototype['ctype'] = orig_type
    zero = typemap.get_zero(normal_type)
    if zero is not None:
        prototype['ctype_zero'] = zero
    if orig_type != normal_type:
        typemap_tests.add((orig_type, c_type))

    for arg in prototype['arguments']:
        orig_type = arg['type']
        arg['type'] = normal_type = typemap(orig_type)
        # arg['ctype'] = c_type = normal_type + '_t'
        c_type = normal_type + '_t'
        arg['ctype'] = orig_type
        zero = typemap.get_zero(normal_type)
        if zero is not None:
            arg['ctype_zero'] = zero
        if orig_type != normal_type:
            typemap_tests.add((orig_type, c_type))


def generate_kernel(config_file,
                    target_file=None,
                    source_dir=''):
    data = get_module_data(config_file)
    source = source_template(data)
    own_target_file = False
    if target_file == 'stdout':
        target_file = sys.stdout
        own_target_file = False
    else:
        if target_file is None:
            target_file = os.path.join(source_dir,
                                       '{module_name}-kernels.c'.format(**data))
        if isinstance(target_file, str):
            print('generate_kernel: target source file is {}'
                  .format(target_file))
            target_file = open(target_file, 'w')
            own_target_file = True
        else:
            own_target_file = False

    target_file.write(prettify(source['c_source'], target='c'))
    if own_target_file:
        target_file.close()
    return dict(config_file=config_file,
                sources=[target_file.name] + data['sources'])


def update_config_xnd(**config):
    """ Update configuration variables for XND packages.
    """
    sys_include_dir = os.path.join(sys.prefix, 'include')
    sys_lib_dir = os.path.join(sys.prefix, 'lib')
    libraries = ['gumath', 'xnd', 'ndtypes']
    include_dirs = config['include_dirs']
    library_dirs = config['library_dirs']
    has_xnd = None
    for name in libraries:
        try:
            module = __import__(name)
            has_xnd = True
        except ImportError as msg:
            # Skipping for cases where one needs to generate the
            # kernel sources only.
            print(f'update_config_xnd: failed to import the required package'
                  f' `{name}`: {msg}. SKIPPING!')
            has_xnd = False
            continue
        d = os.path.dirname(module.__file__)
        d_files = ' '.join(map(os.path.basename, glob(os.path.join(d, '*.*'))))
        print(f'found `{name}` package in `{d}` that contains:\n  {d_files}')

        include_dir_candidates = (d, sys_include_dir)
        library_dir_candidates = (d, sys_lib_dir)

        for header_name in [f'{name}', f'py{name}']:
            for dh, dl in zip(include_dir_candidates, library_dir_candidates):
                h = os.path.join(dh, f'{header_name}.h')
                if os.path.isfile(h):
                    if h not in include_dirs:
                        include_dirs.append(dh)
                        library_dirs.append(dl)
                        break
            else:
                # In custom configuration user specifies include and
                # library directories.
                include_paths = ':'.join(include_dir_candidates)
                print(f'WARNING:update_config_xnd: no header file'
                      f' `{header_name}.h` found in `{include_paths}`.'
                      ' Assuming custom configuration.')

        if name not in config['libraries']:
            config['libraries'].append(name)
    return has_xnd


def get_module_data(config_file):
    config = load_kernel_config(config_file)
    if config is None:
        return
    config_dir = os.path.dirname(config_file)

    reader = PrototypeReader()
    current_module = None

    xndtools_datadir = os.path.dirname(__file__)

    include_dirs = []
    library_dirs = []
    libraries = []
    has_xnd = update_config_xnd(include_dirs=include_dirs,
                                library_dirs=library_dirs,
                                libraries=libraries)
    include_dirs.append(xndtools_datadir)

    sources = list(glob(os.path.join(xndtools_datadir, '*.c')))
    kernels = []
    typemap_tests = set()

    default_debug_value = False
    default_kinds_value = 'Xnd'  # TODO: move to command line options
    default_ellipses_value = '...'
    default_arraytypes_value = 'symbolic'

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
                include_dirs.append(resolve_path(line, prefix=config_dir))

            for line in current_module.get('sources', '').splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                sources.append(resolve_path(line, prefix=config_dir))

            default_debug = bool(current_module.get('debug', default_debug_value))  # TODO: debug should be command line flag
            default_kinds = split_expression(current_module.get('kinds', default_kinds_value))
            default_ellipses = split_expression(current_module.get('ellipses', default_ellipses_value))
            default_arraytypes = split_expression(current_module.get('arraytypes', default_arraytypes_value))

        elif section.startswith('KERNEL'):
            f = config[section]
            if f.get('skip', None):
                # print ('skipping', section)
                continue
            kernel_name = section.split(maxsplit=1)[1].strip()
            for k in list(f.keys()):
                k_new = None
                if '_arguments' in k:
                    k_new = k.replace('_arguments', '')
                elif k == 'prototypes_C':
                    k_new = 'prototypes[C]'
                elif k == 'prototypes_Fortran':
                    k_new = 'prototypes[Fortran]'
                elif k == 'fortran_C':
                    k_new = 'fortran[C]'
                elif k == 'fortran_Fortran':
                    k_new = 'fortran[Fortran]'
                if k_new is not None:
                    f[k_new] = f[k]
                    del f[k]
                    warnings.warn(f"usage of `{k}` key is deprecated, use `{k_new}` instead (in {config_file}:{kernel_name})",
                                  DeprecationWarning, stacklevel=2)
                if k == 'dimension':
                    warnings.warn(f"usage of `{k}` key is deprecated, specify argument {k} in appropiate intent list (in {config_file}:{kernel_name})",
                                  DeprecationWarning, stacklevel=2)
            description = f.get('description', '').strip()

            prototypes = reader(f.get('prototypes', ''))
            prototypes_C = reader(f.get('prototypes[C]', ''))
            prototypes_Fortran = reader(f.get('prototypes[Fortran]', ''))

            if not (prototypes or prototypes_C or prototypes_Fortran):
                print('get_module_data: no prototypes|prototypes[C]|prototypes[Fortran] defined in [KERNEL {}]'.format(kernel_name))
                continue

            debug = bool(f.get('debug', default_debug))
            kinds = split_expression(f.get('kinds', ''))
            ellipses = f.get('ellipses')
            if ellipses is None:
                ellipses = default_ellipses
            else:
                ellipses = split_expression(ellipses)
            arraytypes = split_expression(f.get('arraytypes', '')) or default_arraytypes

            assert set(arraytypes).issubset(['symbolic', 'variable']), repr(arraytypes)

            # get argument intents and shape information
            intent_arguments = {}
            for intent_name in intent_names:
                intent_arguments[intent_name] = split_expression(f.get(intent_name, ''))
            argument_dimensions = split_expression(f.get('dimension', ''))

            fortran_arguments = split_expression(f.get('fortran', ''))
            fortran_arguments_C = split_expression(f.get('fortran[C]', ''))
            fortran_arguments_Fortran = split_expression(f.get('fortran[Fortran]', ''))

            # propagate prototypes to kernels
            for prototypes_, kinds_, fortran_arguments_ in [
                    (prototypes_C, ['C'], fortran_arguments_C),
                    (prototypes_Fortran, ['Fortran'], fortran_arguments_Fortran),
                    (prototypes, kinds or default_kinds, fortran_arguments),
            ]:
                for prototype in prototypes_:
                    prototype['kernel_name'] = kernel_name
                    prototype['description'] = description
                    prototype['function_name'] = prototype.pop('name')
                    prototype['debug'] = debug
                    prototype['oneline_description'] = prototype['description'].lstrip().split('\n', 1)[0] or '<description not specified>'
                    apply_typemap(prototype, typemap, typemap_tests)

                    depends_map = defaultdict(set)
                    values_map = {}
                    shapes_map = {}
                    arguments = list(prototype['argument_map'])

                    for intent_name in intent_arguments:
                        for name in intent_arguments[intent_name]:
                            name = update_argument_maps(name, depends_map, values_map, shapes_map, arguments)
                            prototype.set_argument_intent(name, intent_name)

                    for name_shape in argument_dimensions:
                        name = update_argument_maps(name_shape, depends_map, values_map, shapes_map, arguments)

                    max_rank = 0
                    has_C_tensors = False
                    has_F_tensors = False
                    for name, shapes in shapes_map.items():
                        for shape in shapes:
                            update_argument_maps((name, shape), depends_map, values_map, shapes_map, arguments)
                        prototype.set_argument_shape(name, shapes)
                        arg = prototype.get_argument(name)
                        if not arg.is_intent_hide:
                            max_rank = max(max_rank, len(shapes))
                            if len(shapes) > 1:
                                if name in fortran_arguments_:
                                    has_F_tensors = True
                                else:
                                    has_C_tensors = True

                    # note that `has_?_tensors` include also output arguments.
                    allowed_kinds = []
                    if has_F_tensors and has_C_tensors:
                        allowed_kinds = ['Xnd']
                    elif has_F_tensors:
                        allowed_kinds = ['Xnd', 'Fortran']
                    elif has_C_tensors:
                        allowed_kinds = ['Xnd', 'C']
                    else:
                        allowed_kinds = ['Xnd', 'C']
                    prototype['max_rank'] = max_rank

                    if max_rank > 1:
                        for name, shapes in shapes_map.items():
                            if len(shapes) > 1:
                                if name in fortran_arguments_:
                                    prototype.set_argument_fortran(name)
                                else:
                                    prototype.set_argument_c(name)
                            else:
                                prototype.set_argument_c(name)
                            a = prototype.get_argument(name)
                            assert (a.is_c and not a.is_fortran) or (not a.is_c and a.is_fortran)
                    elif fortran_arguments_:
                        print('get_module_data: `fortran: {}` not used for kernels with rank[={}] less than 2. [KERNEL {}]'
                              .format(', '.join(fortran_arguments_), max_rank, kernel_name))

                    for name, depends in depends_map.items():
                        prototype.set_argument_depends(name, depends)

                    for name, value in values_map.items():
                        prototype.set_argument_value(name, value)

                    input_args, output_args = prototype.get_input_output_arguments()

                    for arraytype in arraytypes:
                        for kind in kinds_:
                            if arraytype == 'variable' and kind != 'Xnd':
                                continue
                            if kind not in allowed_kinds:
                                print('get_module_data: `kinds: {}` not in allowed set `kinds: {}` [KERNEL {}]`'.format(kind, '|'.join(allowed_kinds), kernel_name))
                                continue

                            # if max_rank < 2 and kind == 'Fortran':
                            #    print('get_module_data: Fortran {}-rank kernel is equivalent to C kernel, skipping. [KERNEL {}]'.format(max_rank, kernel_name))
                            #    continue
                            for ellipses_ in ellipses:
                                kernel = deepcopy(prototype)
                                kernel['kind'] = kind
                                kernel['arraytype'] = arraytype
                                if ellipses_ and ellipses_.lower() != 'none':
                                    if not input_args:  # `void -> ... * T` not allowed
                                        continue
                                    if ellipses_ == '...' and arraytype == 'variable':
                                        kernel['ellipses'] = 'var' + ellipses_ + ' * '
                                    else:
                                        kernel['ellipses'] = ellipses_ + ' * '
                                else:
                                    kernel['ellipses'] = ''
                                kernel['ellipses_name'] = kernel['ellipses'].replace('...', '_DOTS_').replace('.', '_DOT_').replace('*', '_STAR_').replace(' ', '')
                                kernel['kernel_repr'] = pprint.pformat(kernel, indent=4, compact=True)
                                kernels.append(kernel)

    lst = []
    for h in current_module.get('includes', '').split():
        h = h.strip()
        if h:
            lst.append('#include "{}"'.format(h))

    module_data = dict(
        module_name=module_name,
        includes='\n'.join(lst),
        # header_code=current_module.get('header_code', ''),
        include_dirs=include_dirs,
        library_dirs=library_dirs,
        libraries=libraries,
        sources=sources,
        kernels=kernels,
        typemap_tests=list([dict(orig_type=o[0], normal_type=o[1])
                            for o in typemap_tests]),
        has_xnd=has_xnd
    )

    return module_data
