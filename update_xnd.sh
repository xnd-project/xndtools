#!/bin/bash
CWD=$(pwd)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# assuming conda environment:
export PREFIX=$CONDA_PREFIX

if [[ -z "${TRAVIS}" ]]; then
    if ! [ -d $DIR/ndtypes ]; then
	git clone git@github.com:plures/ndtypes.git
    fi
    
    if ! [ -d $DIR/xnd ]; then
	git clone git@github.com:plures/xnd.git
    fi
    
    if ! [ -d $DIR/gumath ]; then
	git clone git@github.com:plures/gumath.git
    fi
else
    git clone https://github.com/plures/ndtypes.git
    git clone https://github.com/plures/xnd.git
    git clone https://github.com/plures/gumath.git
fi

cd $DIR/ndtypes
git pull
#make distclean
#./configure --prefix=$PREFIX
#make
#make install
pip install -U .

cd $DIR/xnd
git pull
#make distclean
#./configure --prefix=$PREFIX --with-includes=$PREFIX/include
#make
#make install
pip install -U .

cd $DIR/gumath
git pull
#make distclean
#./configure --prefix=$PREFIX --with-includes=$PREFIX/include
#make
#make install
pip install -U .

cd $CWD
