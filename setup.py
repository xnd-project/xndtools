#
# BSD 3-Clause License
#
# Copyright (c) 2017-2018, plures
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import os
import sys
if sys.version_info[:2] < (3, 4):
    raise RuntimeError("Python version >= 3.4 required.")
import sysconfig

import builtins
builtins.__XNDTOOLS_SETUP__ = True

if os.path.exists('MANIFEST'):
    os.remove('MANIFEST')

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

from distutils.command.build_py import build_py
from glob import glob
from shutil import copyfile

def build_dir_path(dname, *path):
    f = os.path.join('build', '{dirname}.{platform}-{version[0]}.{version[1]}', *path)
    return f.format(dirname=dname,
                    platform=sysconfig.get_platform(),
                    version=sys.version_info)

def kernel_generator_test_modules():
    from argparse import Namespace
    from xndtools.kernel_generator import generate_module
    source_dir = build_dir_path('lib', 'xndtools/kernel_generator/tests/')
    extensions = []
    for cfg in glob('xndtools/kernel_generator/tests/test_*-kernels.cfg'):
        extra_compile_args = ["-Wextra", "-Wno-missing-field-initializers", "-std=c11"]
        extra_link_args = []
        runtime_library_dirs = []        
        m = generate_module(Namespace(config_file = cfg,
                                      target_language = 'python',
                                      package = 'xndtools.kernel_generator.tests',
                                      source_dir = source_dir,
                                      target_file = None,
                                      kernels_source_file = None,
        ))
        ext = Extension (
            m['extname'],
            include_dirs = m['include_dirs'],
            library_dirs = m['library_dirs'],
            depends = m['sources']+[cfg],
            sources = m['sources'],
            libraries = m['libraries'],
            extra_compile_args = extra_compile_args,
            extra_link_args = extra_link_args,
            runtime_library_dirs = runtime_library_dirs
        )
        
        extensions.append(ext)
        
    return extensions

data_files = (
    glob('xndtools/kernel_generator/*.c') +
    glob('xndtools/kernel_generator/*.h')
)


class my_build_py(build_py):
    def run(self):
        if not self.dry_run:
            target_dir = os.path.join(
                self.build_lib, 'xndtools', 'kernel_generator'
            )
            self.mkpath(target_dir)
            for fn in data_files:
                copyfile(fn, os.path.join(target_dir, os.path.basename(fn)))
        build_py.run(self)


DESCRIPTION = "XND Tools"

LONG_DESCRIPTION = """
XND Tools provides development tools of the XND project:
kernel_generator - generate kernels for gumath"""

def setup_package():
    src_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    old_path = os.getcwd()
    os.chdir(src_path)
    sys.path.insert(0, src_path)

    ext_modules = kernel_generator_test_modules()
    
    metadata = dict(
       name='xndtools',
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        license='BSD',
        version='0.2.0.dev3',
        author='Pearu Peterson',
        maintainer='Pearu Peterson',
        author_email='pearu.peterson@quansight.com',
        url='https://github.com/plures/xndtools',
        platforms='Cross Platform',
        classifiers=[
            "Intended Audience :: Developers",
            "License :: OSI Approved :: BSD License",
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            "Operating System :: OS Independent",
            "Topic :: Software Development",
        ],
        install_requires=[
            "ndtypes == v0.2.0.dev3",
            "xnd == v0.2.0.dev3",
            "gumath == v0.2.0.dev3"
        ],
        include_package_data=True,
        packages=['xndtools', 'xndtools.kernel_generator'],
        # package_data={'xndtools': data_files},
        scripts=['scripts/xnd_tools', 'scripts/structinfo_generator'],
        cmdclass={'build_py': my_build_py},
        ext_modules = [ext for ext in ext_modules if ext is not None],
     
    )
    
    try:
        setup(**metadata)
    finally:
        del sys.path[0]
        os.chdir(old_path)
    return

if __name__ == '__main__':
    setup_package()
    del builtins.__XNDTOOLS_SETUP__
