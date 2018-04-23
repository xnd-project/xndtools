#!/usr/bin/env python

import os, sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from glob import glob
    
setup(
    name='xndtools',
    description='XND Tools',
    long_description="""
    XND Tools provides development tools of the XND project:
      kernel_generator - generate kernels for gumath
    """,
    license='BSD',
    version='0.1',
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
    package_data={'': glob('xndtools/kernel_generator/*.c')+['xndtools/kernel_generator/*.h']},
    scripts = ['scripts/xnd_tools'],
)
