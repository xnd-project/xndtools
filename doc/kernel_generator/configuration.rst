.. meta::
   :robots: index, follow
   :description: kernel_generator documentation: configuration file
   :keywords: xndtools, xnd, C, array computing

.. sectionauthor:: Pearu Peterson <pearu.peterson at gmail.com>


Kernel generator configuration file
===================================

Kernel generator configuration file describes the interface between C
functions and gumath kernels.

The kernel generator configuration file uses configuration language
that can be parsed using `configparser`_ Python package.

.. _configparser: https://docs.python.org/3/library/configparser.html

Overview
--------

Generally speaking, a gumath kernel is a function that has input
arguments and output arguments. On the other hand, C functions
represented by their C function prototypes have one or zero return
values and a number of arguments. The aim of the kernel generator is
to semi-automatically generate a gumath kernel that calls a C function
with kernel inputs and returns changed arguments as kernel outputs.

In C language, the intention of the arguments (input or output or both
or neither) is not well-defined (except for scalar arguments that can
be of input intent only).  The intention of arguments may become clear
from the API documentation of the C function. So, the kernel
generation process cannot be fully automated and developer input for
giving a meaning to the C function arguments is required. For that, a
kernel generator configuration file is introduced. The initial
configuration file can be generated using command line tool
`xnd_tools`::

  xnd_tools config -m <modulename> <header file 1> [<header file 2> ...]

that will generate a file ``<modulename>-kernels.cfg`` (see
``xnd_tools config --help`` for more information). The developer is
expected to revise the generated file and adjust the argument intents
and specify their dimensions as well as initial values as appropiate.
By default, all generated kernel definitions are disabled in the
configuration file.

The final form of a kernel function depends on the target language:

In C:
  .. code:: c
     
    int <kernel function name>(xnd_t stack[], ndt_context_t *ctx) {
      ...
      return <success value is 0>
    }

  where the kernel input and output arguments are collected in ``stack`` array.

  To generate gumath kernels for C language, use::

    xnd_tools kernel `<modulename>-kernels.cfg

  See ``xnd_tools kernel --help`` for more information.

In Python (implemented using Python C/API):
  .. code:: python
  
    def <kernel function name>(*<input arguments>):
        ...
        return <output arguments>

  To generate gumath kernels for Python language, use::

    xnd_tools module `<modulename>-kernels.cfg 

  See ``xnd_tools module --help`` for more information.

	
In Ruby:
  ::
    
    TODO

  To generate gumath kernels for Ruby language, use::

    xnd_tools module `<modulename>-kernels.cfg \
      --target-language=ruby [NOT IMPLEMENTED] 

etc.
  
.. contents::
   :local:


Configuration file sections
---------------------------

The kernel configuration file must include the following sections:

``[MODULE <modulename>]``
  The configuration file is expected to contain exactly one
  ``[MODULE]`` section followed by ``[KERNEL]`` sections.
  ``<modulename>`` is the name of a module containing gumath
  kernels. The source code of kernels will be saved to a file
  ``<modulename>-kernels.c``.

``[KERNEL <kernelname>]``
  The configuration file is expected to contain one or more
  ``[KERNEL]`` sections.  ``<kernelname>`` is a name of a kernel.

``[MODULE]`` keys
-----------------

The ``[MODULE]`` section may define the following keys::

  typemaps: <list of mappings `<C type spec>:<typename><bitwidth>`>
  kinds: <default list of kernel kinds>
  ellipses: <default list of signature ellipses>
  include_dirs: <list of include directories>
  includes: <list of include files>
  sources: <list of additional C source files>

The definitions of the keys are as follows:
  
``typemaps:``
  Specify mapping between C type specifications used in C prototypes
  and canonical types in the form ``<typename><bitwidth>``.  For
  instance::

    typemaps:
      double:float64
      float:float32
      MKL_INT:int64

  The command ``xnd_tools config ...`` is able to generate typemaps
  for all standard C primitive types.

  To prevent errors due to the specification of wrong bit-widths
  (e.g. ``double:float32``), the generated kernel source code will
  contain a function ``int
  gmk_test_<modulename>_typemaps(ndt_context_t *)`` that will raise
  runtime error when ``sizeof(<C type spec>)`` is not equal to
  ``sizeof(<typename><bitwidth>)``.

``kinds:``
  Specify default kinds of kernels. ``[KERNEL]`` section may override this key.
  The comma-separated list of supported kernel kinds are:

  ``C``
    Generate kernels that will be called when all arguments are C contiguous.

  ``Fortran``
    Generate kernels that will be called when all arguments are Fortran contiguous.
    
  ``Xnd``
    Generate kernels that will be called for non-contiguous inputs, or
    if ``C`` or ``Fortran`` kind of kernels are not generated.
    
``ellipses:``

  Specify default ellipses of kernel signatures. ``[KERNEL]`` section
  may override this key.  Ellipses in signatures allows calling
  kernels on multidimensional arrays of kernel inputs. Supported
  ellipses are (to be specified as comma-separated list):

  ``none``
    Use no ellipses. The generated kernel is used for inputs that
    exactly match the kernel arguments.

  ``...``
    The generated kernel is used for arrays with fixed dimensions as
    well as for inputs that exactly match the kernel arguments.

  ``var...``
    The generated kernel can be used for arrays with variable dimensions.

``include_dirs:``

  Specify a list of include file directories to be used when compiling
  kernel source code. The directory paths may include:
  
  - environment variables in the form ``$<ENVIRONMENT VARIABLE NAME>``
  - ``<prefix>`` that will be replaced with ``sys.prefix``
  - ``<site>`` that will be replaced with the output of ``distutils.sysconfig.get_python_lib()``.

``includes:``

  Specify a list of header file names to be used in the header of
  kernel source code.

``sources:``

  Specify a list of C source files that should be compiled and linked
  together with kernel source code. The file paths may include words
  described in the ``include_dirs:`` key description.
  
    
``[KERNEL]`` keys
-----------------
  
The ``[KERNEL]`` section may define the following keys::

  description: <multiline documentation>
  kinds: <list of kernel kinds>
  ellipses: <list of signature ellipses>
  prototypes: <list of C prototypes>
  prototypes[C]: <list of C prototypes>
  prototypes[Fortran]: <list of C prototypes>
  input: <list of arguments>
  inplace: <list of arguments>
  inout: <list of arguments>
  hide: <list of arguments>
  output: <list of arguments>
  fortran: <list of arguments>
  fortran[C]: <list of arguments>
  fortran[Fortran]: <list of arguments>
  arraytypes: <variable|symbolic>
  dimension: <list of dimension specifications> [deprecated]

The definitions of the keys are as follows:

``description:``

  Specify documentation string of a kernel. The first non-empty line
  will be used as one-line documentation.

``kinds:``, ``ellipses:``
  See above.

``prototypes:``, ``prototypes[C]:``, ``prototypes[Fortran]:``

  Specify a list of C function prototypes (one per line) for which
  gumath kernels are generated. The functions under ``prototypes[C]``
  and ``prototypes[Fortran]`` are used for kernels with ``C`` and
  ``Fortran`` kinds, respectively, when specified.

``input:``

  Specify a comma-separated list of C function arguments that have
  intent ``input``.  Intent ``input`` means that the C function uses
  the value of the corresponding argument. In a case of
  non-contiguous input array, the array will be copied to a contiguous array
  that will be used as an argument to the C function.

``inplace:``

  Specify a comma-separated list of C function arguments that have
  intent ``inplace``. Intent ``inplace`` means that the C function
  uses and may change the value of the corresponding argument.  In a
  case of non-contiguous input array, the array will be copied to a
  contiguous array that will be used as an argument to the C function.
  After the return, the contiguous array content is copied back to the
  initial input array.

``inout:``

  Specify a comma-separated list of C function arguments that have
  intent ``inout``.  Intent ``inout`` means that the C function uses
  and may change the value of the corresponding argument.
  In a case of non-contiguous input array, an exception will be raised.
  
``output:``

  Specify a comma-separated list of C function arguments that have
  intent ``output``.  Intent ``output`` means that the C function may
  change the corresponding argument. The memory for output arguments
  is allocated by gumath.
  
``hide:``

  Specify a comma-separated list of C function arguments that have intent ``hide``.
  Intent ``hide`` means that the corresponding C function argument
  will not appear in a list of kernel arguments. The value of the argument
  is determined by initializing it or it may be left undefined.

  TODO: Using intent ``hide`` for array arguments.
  
``fortran:``, ``fortran[C]:``, ``fortran[Fortran]:``

  Specify a comma-separated list of C function arguments that have
  intent ``fortran`` (default intent of all arguments is ``c``).
  The ``[C|Fortran]`` parts are used when ``prototypes[C|Fortran]`` are specified.
  Intent ``fortran`` means that the C functions expects the argument
  to be F-contiguous.

The C function arguments specified in intent keys may be specified in the
following forms:

- ``<argument name>``
  
- ``<argument name> = <initial C value>`` - used for scalar arguments
  that can be undefined (value is ``None``). The ``<initial C value>``
  can be:

  + any valid C expression
  + ``len(<argument name>)`` - length of specified array argument
  + ``shape(<argument name>)`` - shape of specified array argument
  + ``ndim(<argument name>)`` - number of dimensions in specified array argument
      
- ``<argument name>(<shape-list>)`` - used for array arguments to
  specify the shape. The ``<shape-list>`` is a comma-separated list of
  valud C expressions or ``len(...)`` or ``shape(...)``.

