#!/usr/bin/env python
"""
Requirements:

  ndtypes, xnd, gumath, xndtools
"""

import os, sys
try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

import xndtools
from xndtools.kernel_generator import generate_module
from argparse import Namespace

# Import requirements:
import ndtypes
NDTYPES_ROOT = os.path.dirname(ndtypes.__file__)
import xnd
XND_ROOT = os.path.dirname(xnd.__file__)
import gumath
GUMATH_ROOT = os.path.dirname(gumath.__file__)

# TODO: detect conda, mkl
CONDA_PREFIX=os.environ['CONDA_PREFIX']
MKLROOT = CONDA_PREFIX

kernel_configuration_files = ['example-kernels.cfg',
                              'test_scalar-kernels.cfg',
                              'test_array-kernels.cfg',
                              'test_mixed-kernels.cfg',
                              'mkl_vml-kernels.cfg'
][1:]

ext_modules = []
for cfg in kernel_configuration_files:
    include_dirs = [NDTYPES_ROOT, XND_ROOT, GUMATH_ROOT, os.path.join(CONDA_PREFIX, 'include')]
    library_dirs = [NDTYPES_ROOT, XND_ROOT, GUMATH_ROOT, os.path.join(CONDA_PREFIX, 'lib')]
    libraries = ["ndtypes", "xnd", "gumath"]

    extra_compile_args = ["-Wextra", "-Wno-missing-field-initializers", "-std=c11"]
    extra_link_args = []
    runtime_library_dirs = []
    
    if cfg.startswith('mkl_'):
        libraries += ['mkl_intel_ilp64', 'mkl_sequential', 'mkl_core', #'mkl_rt',
                      'pthread', 'm', 'dl']
        extra_compile_args += ['-DMKL_ILP64', '-m64']
        extra_link_args += ['-Wl,--no-as-needed']        
        include_dirs += [os.path.join(MKLROOT, 'include')]
        library_dirs += [os.path.join(MKLROOT, 'lib')]
        
    m = generate_module(Namespace(config_file = cfg,
                                  target_language = 'python',
                                  package = 'xndlib',
                                  source_dir = '',
                                  target_file = None,
                                  kernels_source_file = None,
    ))
    include_dirs += m['include_dirs']
    sources = m['sources']
    depends = sources + [cfg] + [xndtools.__file__]

    ext = Extension (
      m['extname'],
      include_dirs = include_dirs,
      library_dirs = library_dirs,
      depends = depends,
      sources = sources,
      libraries = libraries,
      extra_compile_args = extra_compile_args,
      extra_link_args = extra_link_args,
      runtime_library_dirs = runtime_library_dirs
    )
    ext_modules.append(ext)

    
def mkl_blas_ext():
    depends = []
    sources = ["mkl_blas.c","mkl_blas_kernels.c"]
    include_dirs = [NDTYPES_ROOT, XND_ROOT, GUMATH_ROOT, os.path.join(CONDA_PREFIX, 'include'), os.path.join(MKLROOT, 'include')]
    library_dirs = [NDTYPES_ROOT, XND_ROOT, GUMATH_ROOT, os.path.join(CONDA_PREFIX, 'lib'), os.path.join(MKLROOT, 'lib')]
    libraries = ["ndtypes", "xnd", "gumath"]
    libraries += ['mkl_intel_ilp64', 'mkl_sequential', 'mkl_core', 'pthread', 'm', 'dl']
    extra_compile_args = ["-Wextra", "-Wno-missing-field-initializers", "-std=c11", '-DMKL_ILP64', '-m64']
    extra_link_args = ['-Wl,--no-as-needed']
    runtime_library_dirs = []
    return Extension (
      "mkl_blas",
      include_dirs = include_dirs,
      library_dirs = library_dirs,
      depends = depends,
      sources = sources,
      libraries = libraries,
      extra_compile_args = extra_compile_args,
      extra_link_args = extra_link_args,
      runtime_library_dirs = runtime_library_dirs
    )
    
#ext_modules += [mkl_blas_ext()]    


setup(
    name='xndlib',
    description='XND Libraries',
    long_description=""" XND Libraries provides a collection of extension modules
    containing gumath wrappers to various software libraries.
    """,
    license='BSD',
    version='0.2',
    author='Pearu Peterson',
    maintainer='Pearu Peterson',
    author_email='pearu.peterson@quansight.com',
    url='https://github.com/plures/xndtools',
    platforms='Cross Platform',
    classifiers = [
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        "Operating System :: OS Independent",
        "Topic :: Software Development",
    ],
    packages=['xndlib'],
    #cmdclass={'install': install, 'sdist': sdist},
    ext_modules = [ext for ext in ext_modules if ext is not None],
)
