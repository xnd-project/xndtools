.. meta::
   :robots: index, follow
   :description: kernel_generator documentation
   :keywords: xndtools, xnd, C, array computing

.. sectionauthor:: Pearu Peterson <pearu.peterson at gmail.com>


Kernel generator
================

`kernel_generator` is a Python package for generating gumath kernels
from C function prototypes.

The process of generating `gumath` kernels consists of the following
steps:

#. Scan C header files for C function prototypes and create or append
   these to kernel generator configuration file.
#. Modify kernel configuration file to define kernels user interface
   and determine the intention of C function arguments.
#. Generate gumath kernels source code that will contain a function
   ``gmk_init_<module name>_kernels(gm_tbl_t *tbl, ndt_context_t
   *ctx)`` that can be used to register new kernels for
   `libgumath`.
#. Optionally, generate extension modules for specified target
   language to make `gumath` kernels available for a particular
   programming language. Currently implemented target languages are:
   `python`.

The `kernel_generator` package provides a command line tool
`xnd_tools` to execute all the above mentioned steps.


.. toctree::

   configuration.rst
