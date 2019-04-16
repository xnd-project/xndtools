XND Tools
---------

[![Travis CI Build Status](https://travis-ci.org/xnd-project/xndtools.svg?branch=master)](https://travis-ci.org/plures/xndtools)
[![AppVeyor Build status](https://ci.appveyor.com/api/projects/status/lk48i3bmmw2keq3d/branch/master?svg=true)](https://ci.appveyor.com/project/pearu/xndtools/branch/master)

XND Tools provides development tools for the XND project. Currently,
the following tools are provided:

- `xndtools.kernel_generator` - a Python package supporting automatic XND kernel generation using C header files as input.

[XND Tools Documentation](https://xnd.readthedocs.io/en/latest/xndtools/index.html)

# Development instructions

## Checkout, prepare conda environment, develop, and test

```
git clone https://github.com/xnd-project/xndtools.git
cd xndtools
conda env create --file=conda-envs/xndtools-devel.yaml -n xndtools-dev
python setup.py develop
pytest .
```

# Usage

See `xndlib/README.txt` and `xnd_tools -h`.

For example,
```
  cd xndlib
  python setup.py develop
  py.test -sv xndlib/
```
