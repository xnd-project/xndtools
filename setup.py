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

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from distutils.command.build_py import build_py
from glob import glob
from shutil import copyfile

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

setup(
    name='xndtools',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    license='BSD',
    version='0.2.0dev3',
    author='Pearu Peterson',
    maintainer='Pearu Peterson',
    author_email='pearu.peterson@quansight.com',
    url='https://github.com/plures/xndtools',
    platforms='Cross Platform',
    classifiers=[
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
    install_requires=[
        "ndtypes == v0.2.0dev3",
        "xnd == v0.2.0dev3",
        "gumath == v0.2.0dev3"
    ],
    include_package_data=True,
    packages=['xndtools', 'xndtools.kernel_generator'],
    # package_data={'xndtools': data_files},
    scripts=['scripts/xnd_tools', 'scripts/structinfo_generator'],
    cmdclass={'build_py': my_build_py},
)
