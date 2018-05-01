XND Tools
---------

XND Tools provides development tools for the XND project. Currently, the following tools are provided:

- `xndtools.kernel_generator` - a Python package supporting automatic XND kernel generation using C header files as input.

# Prerequisites

- Define installation prefix. It can be `/usr/local`, for instance. Or
  when using conda environment, prefix is $CONDA_PREFIX:

  export PREFIX=$CONDA_PREFIX

- [ndtypes](https://github.com/plures/ndtypes)

  git clone https://github.com/plures/ndtypes.git
  cd ndtypes
  ./configure --prefix=$PREFIX
  make
  make install
  cd ..
  
- [xnd](https://github.com/plures/xnd)

  git clone https://github.com/plures/xnd.git
  cd xnd
  ./configure --prefix=$PREFIX --with-includes=$PREFIX/include
  make
  make install
  cd ..

- [gumath](https://github.com/plures/gumath)

  git clone https://github.com/plures/gumath.git
  cd gumath
  ./configure --prefix=$PREFIX --with-includes=$PREFIX/include
  make
  make install
  cd ..

# Installation

  git clone https://github.com/plures/xndtools.git
  cd xndtools
  pip install -U .

# Usage

See `xndlib/README.txt` and `xnd_tools -h`.

For example,

  cd xndlib
  python setup.py develop
  python test_example.py

  