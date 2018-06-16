"""Kernel configuration file generator.

Usage:

  1. Add new extension module specification to main file. Specify
  modulename and includes arguments as minimum.

  2. Execute the script. This will generate a file
  'kernels_<modulename>.cfg' to current working directory.

  3. Copy the kernels configuration file where needed.

  4. Edit the kernels configuration file. See instructions in its
  header.

  5. Generate the extension module source by executing

      generate_module.py <kernels_<modulename>.cfg

     that will generate a file `<modulename>.c`

  6. Build the extension module using your favorite tool.

"""
# Author: Pearu Peterson
# Created: April 2018

import os
import re
import sys
from collections import defaultdict
import configparser
from xndtools.kernel_generator.readers import PrototypeReader, load_kernel_config
from xndtools.kernel_generator.utils import NormalizedTypeMap

def main():
    # See
    #  https://software.intel.com/en-us/articles/intel-mkl-link-line-advisor/
    # for linking options
    
    include_dirs = [os.path.join('$MKLROOT', 'include'),
                    os.path.join('$CONDA_PREFIX', 'include')
    ]
    exclude_patterns = [r'.*_\Z', r'\A[A-Z0-9_]+\Z', r'.*_(batch|pack|alloc|free|work)\Z']
    strip_left, strip_right = ['mkl_'], [] # parameters to NormalizedTypeMap
    
    generate_config(modulename = 'mkl_blas',
                    includes = ['mkl_blas.h'],
                    include_dirs = include_dirs,
                    libraries = [],
                    exclude_patterns = exclude_patterns,
                    typemap_options = dict(
                        strip_left = strip_left,
                        strip_right = strip_right,
                    ),
    )
    
    generate_config(modulename = 'mkl_cblas',
                    includes = ['mkl_cblas.h'],
                    include_dirs = include_dirs,
                    libraries = [],
                    exclude_patterns = exclude_patterns,
                    typemap_options = dict(
                        strip_left = strip_left,
                        strip_right = strip_right,
                        initial = dict(
                            CBLAS_INDEX='size_t',
                        )
                    ),
    )

    generate_config(modulename = 'mkl_lapacke',
                    includes = ['mkl_lapacke.h'],
                    include_dirs = include_dirs,
                    libraries = [],
                    exclude_patterns = exclude_patterns,
                    reader_options = dict(
                        extra_specifiers = ['LAPACK_DECL'],
                    ),
                    typemap_options = dict(
                        initial = dict(
                            lapack_int = 'MKL_INT',
                            lapack_logical = 'lapack_int',
                            lapack_complex_float = 'MKL_Complex8',
                            lapack_complex_double = 'MKL_Complex16',
                        ),
                        strip_left = strip_left,
                        strip_right = strip_right,
                    ),
    )

    generate_config(modulename = 'mkl_scalapack',
                    includes = ['mkl_scalapack.h'],
                    include_dirs = include_dirs,
                    libraries = [],
                    exclude_patterns = exclude_patterns,
                    typemap_options = dict(
                        strip_left = strip_left,
                        strip_right = strip_right,
                    ),
    )

    # TODO: mkl_vml, mkl_dfti, mkl_df, etc

config_editing_instructions = '''

Editing instructions
--------------------

1.1 MODULE section contains typemaps. Check that C type is correctly
    mapped [OPTIONAL]. Other fields can also modified.

1.2 MODULE section contains header_code that may contain C code that
    is inserted after include statements of extension modules source.

2.1 KERNEL name must be changed to appropriate one [REQUIRED].

2.2 KERNEL section contains skip field. When present, the corrsponding
    section will be ignored. When done editing the section, you can
    delete the skip field. [REQUIRED]

2.3 Prototypes field contains C function prototypes as retrieved from
    the header files. There should be no need to edit prototypes.
    Note that within a section all prototypes must have the same
    arguments, only their type specification may differ.

2.4 Section contains description field that will be used as doc string
    of the kernel. Please fill it in [OPTIONAL].

2.5 Dimension field field is used to specify dimensions of array
    arguments. Please fill it in as follows [REQUIRED]:

      <argument name>(<dimension spec>)

    where <dimension spec> is a comma-separated list of dimensions.
    All arguments not specified in dimension field are considered scalars.

2.6 Section contains input/inplace/output/hide_arguments
    fields. Please add argument names to the field as appropiate
    [OPTIONAL]. Initial fillment is based on the use of const in
    prototypes.

2.7 Section contains pre/post_call_code that may contain C code that
    is inserted before/after the call to the backend function
    [OPTIONAL]. This is useful in special circumstances.

'''

def generate_config(modulename,
                    includes,
                    target_file = None,
                    include_dirs = [],
                    match_patterns = [],
                    exclude_patterns = [],
                    libraries = [], library_dirs = [],
                    reader_options = {},
                    typemap_options = {},
):
    """Generate kernel configuration using C function prototypes from header files.

    The kernel configuration file is generated once. The file needs to
    be manually edited to add hints like the dimensions of array
    arguments, descriptions, argument intents, etc.

    Parameters
    ----------
    modulename : str
      Specify the name of extension module.

    target_file : {file, str, None}
      Specify the name of a file where the kernel configuration data
      is written (using .ini file format).  When file exists, the
      function returns without doing anything. When None, target file
      is will be `kernels_<modulename>.cfg`.

    includes : list
      Specify a list of header files that are scanned for C function
      prototypes and to be included into extension module.

    include_dirs : list
      Specify a list of directories where the header files are looked
      for.

    libraries : list
      Specify a list of library names that are linked with the
      extension module.

    library_dirs : list
      Specify a list of directories containing the libraries.

    match_patterns, exclude_patterns : list
      Specify match/exclude patterns for C function names. The
      patterns must be valid re strings.
  
    strip_left, strip_right : list
      Specify ctype stripping rules for NormalizedTypeMap

    """
    own_target_file = False
    if target_file is None:
        target_file = 'kernels-{}.cfg'.format(modulename)
    existing_names = []
    original_content = ''
    if target_file == 'stdout':
        target_file = sys.stdout
        own_target_file = False
    elif isinstance(target_file, str):
        if os.path.exists(target_file):
            reader = PrototypeReader()    
            config = load_kernel_config(target_file)
            for section in config.sections():
                if section.startswith('KERNEL'):
                    f = config[section]
                    for prototype in reader(f['prototypes']):
                        existing_names.append(prototype['name'])
            original_content = open(target_file).read()
            #print ('generate_config: target file {!r} exists! SKIPPING'.format(target_file))
            #return
            print('generate_config: results will be appended to {}'.format(target_file))
        else:
            print('generate_config: results will be saved to {}'.format(target_file))
        target_file = open(target_file, 'w')
        own_target_file = True

    header_files = []
    for header_file in includes:
        if os.path.isfile(header_file):
            header_files.append(header_file)
        else:
            for include_dir in include_dirs:
                if include_dir.startswith('$'):
                    l = include_dir.split(os.sep)
                    include_dir = os.path.join(*([os.environ.get(l[0][1:], l[0])]+l[1:]))
                fn = os.path.join(include_dir, header_file)
                if os.path.isfile(fn):
                    header_files.append(fn)
                    break
            else:
                print ('generate_config:WARNING: could not find header file {} in {}. SKIPPING.'.format(header_file, ':'.join(['.']+include_dirs)))
    
    config = configparser.ConfigParser()
    reader = PrototypeReader(**reader_options)
    typemap = NormalizedTypeMap(**typemap_options)
    
    groups = defaultdict(list)

    functions = []
    for filename in header_files:
        source = open (filename).read()
        for prototype in reader(source, match_patterns = match_patterns, exclude_patterns = exclude_patterns + existing_names):
            print('generate_config: included: {}'.format(prototype['name']))
            prototype.signature(typemap=typemap) # makes typemap
            s = prototype.signature(typemap=typemap, kind='match')
            groups[s].append(prototype)

    for s in sorted(groups):
        prototypes = groups[s]
        name = s.rsplit(maxsplit=1)[-1].strip()

        # inital estimates
        input_arguments = []
        inplace_arguments = []
        for arg in prototypes[0]['arguments']:
            if arg.is_scalar:
                input_arguments.append(arg['name'])
            else:
                inplace_arguments.append(arg['name'])
        
        
        functions.append((name,
                          dict(
                              SKIP = '# REMOVE THIS LINE WHEN READY',
                              prototypes = '\n'+'\n'.join((str(p) for p in prototypes)),
                              description = '',
                              dimension = '',
                              input_arguments = ', '.join(input_arguments),
                              inplace_arguments = ', '.join(inplace_arguments),
                              output_arguments = '',
                              hide_arguments = '',
                              #pre_loop_code = '',
                              #pre_call_code = '',
                              #post_call_code = '',
                              #post_loop_code = '',
                          )))
            
    default = dict(
        typemaps = '\n'.join(['']+['{}: {}'.format(k, v) for k,v in sorted(typemap.items()) if k!=v]),
        includes = '\n'+'\n'.join(includes),
        include_dirs = '\n'+'\n'.join(include_dirs),
        libraries = '\n'+'\n'.join(libraries),
        library_dirs = '\n'+'\n'.join(library_dirs),
        header_code = '',
        kinds = 'Xnd', # TODO: move to command line options
        ellipses = '..., var...',
    )


    if original_content:
        target_file.write(original_content+'\n')
    else:
        target_file.write('# This file is generated from {} and requires editing.'.format(__file__))
        target_file.write(config_editing_instructions.replace('\n', '\n#  ')+'\n')
        config['MODULE '+modulename] = default
    
    for name, func_config in functions:
        config['KERNEL '+name] = func_config

    config.write(target_file)

    if own_target_file:
        target_file.close()

    return dict(config_file = target_file)

        
if __name__ == '__main__':
    main()
