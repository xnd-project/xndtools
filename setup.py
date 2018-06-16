#!/usr/bin/env python

import os, sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from distutils.command.build_py import build_py
from shutil import copyfile
from glob import glob
data_files = glob('xndtools/kernel_generator/*.c')+glob('xndtools/kernel_generator/*.h')

class my_build_py(build_py):
    def run(self):
        if not self.dry_run:
            target_dir = os.path.join(self.build_lib, 'xndtools', 'kernel_generator')
            self.mkpath(target_dir)
            for fn in data_files:
                copyfile(fn, os.path.join(target_dir, os.path.basename(fn)))
        build_py.run(self)

setup(
    name='xndtools',
    description='XND Tools',
    long_description="""
    XND Tools provides development tools of the XND project:
      kernel_generator - generate kernels for gumath
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
    include_package_data=True,
    packages=['xndtools', 'xndtools.kernel_generator'],
    #package_data={'xndtools': data_files},
    scripts = ['scripts/xnd_tools'],
    cmdclass={'build_py': my_build_py},
)
