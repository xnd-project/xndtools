=================================
Generating new kernels for gumath
=================================

Operations on XND containers live in the `gumath
<https://github.com/plures/gumath>`_ library. It already provides binary
operations like add, subtract, multiply and divide, and unary operations like
abs, exponential, logarithm, power, trigonometric functions, etc. They can
operate on various data types, e.g. ``int32`` or ``float64``. But you might want
to create your own kernel, either from a code that you wrote or from an existing
library. This tutorial will show how to do that using the kernel generator from
XND Tools.

----------------
Kernel generator
----------------

`XND Tools <https://github.com/plures/xndtools>`_ provide development tools for
XND. Among them, ``xndtools.kernel_generator`` facilitates the creation of new
kernels by semi-automatically wrapping e.g. C code. Fortran will be supported in
the future, as there are tons of high performance libraries out there.

^^^^^^^^^^^^^^^
Wrapping C code
^^^^^^^^^^^^^^^

Let's say we want to make a kernel out of the following C function, which just
squares a number:

.. code-block:: c

   // file: square.c
   
   #include "square.h"
   
   double square(double a)
   {
       return a * a;
   }

This is the implementation of the function that we want to turn into a kernel,
but the kernel generator is only concerned about its prototype, which looks like
this:

.. code-block:: c

   // file: square.h

   extern double square(double);

Note the ``extern`` keyword: because this header file will be used by the kernel
generator to build the kernel, the ``square`` function will be assumed to be
available somewhere else. We will then be able to compile the kernel and the
``square.c`` file independently, and link them later. This is not so important
in our simple example, but it could be if we were wrapping an existing library
like LAPACK, which has its own build process. The kernel generator doesn't need
to know how to build the library, all it needs is a header file with the
function prototypes.

Now run the following command:

.. code-block:: bash

   $ xnd_tools config square.h

This creates an initial kernel configuration file ``square-kernels.cfg``, which
looks like this:

.. code-block:: none

  [MODULE square]
  typemaps = 
  	double: float64
  includes = 
  	square.h
  include_dirs = 
  	
  libraries = 
  	
  library_dirs = 
  	
  header_code = 
  kinds = Xnd
  ellipses = ..., var...
  
  [KERNEL square]
  skip = # REMOVE THIS LINE WHEN READY
  prototypes = 
  	double square(double   a);
  description = 
  dimension = 
  input_arguments = a
  inplace_arguments = 
  inout_arguments = 
  output_arguments = 
  hide_arguments = 

For this simple kernel, we don't actually have to change anything, so we'll just
remove the ``skip`` line as indicated, and save the file.

The next step is about creating the interface to ``gumath``, and registering our
``square`` function as a kernel. The following command will create a
``square-kernels.c`` file:

.. code-block:: bash

   $ xnd_tools kernel square-kernels.cfg

For now we are still in the C world, so we also need to expose our kernel to
Python. This is done by creating an extension module. Fortunately, XND tools
does that for us as well. The following command will create the
``square-python.c`` file:

.. code-block:: bash

   $ xnd_tools module square-kernels.cfg

Assuming the variable ``$SITE_PACKAGES`` contains the path to your Python
``site-packages`` directory, where ``xnd``, ``ndtypes``, ``gumath`` and
``xndtools`` are installed (given by ``python -c "from distutils.sysconfig
import get_python_lib; print(get_python_lib())"``), you can compile the square
function, its kernel, and create a static library with the following commands:

.. code-block:: bash

   $ gcc -fPIC                                   \
   $ -c square.c                                 \
   $ -c square-kernels.c -fPIC                   \
   $ -I$SITE_PACKAGES/ndtypes                    \
   $ -I$SITE_PACKAGES/xnd                        \
   $ -I$SITE_PACKAGES/gumath                     \
   $ -I$SITE_PACKAGES/xndtools/kernel_generator
   $ ar rcs libsquare-kernels.a square-kernels.o square.o

Then building a C extension for CPython can be done using ``distutils``. It just
needs a ``setup.py`` script, which for our simple case looks like this:

.. code-block:: python

   # file: setup.py

   from distutils.core import setup, Extension
   from distutils.sysconfig import get_python_lib
   
   site_packages = get_python_lib()
   libs = ['ndtypes','gumath', 'xnd']
   lib_dirs = [f'{site_packages}/{lib}' for lib in libs]
   
   module1 = Extension('square',
                       include_dirs = lib_dirs,
                       libraries = ['square-kernels'] + libs,
                       library_dirs = ['.'] + lib_dirs,
                       sources = ['square-python.c'])
   
   setup (name = 'square',
          version = '1.0',
          description = 'This is a gumath kernel extension that squares an XND container',
          ext_modules = [module1])

Finally, we can build and install our extension with the following command:

.. code-block:: bash

   $ python setup.py install

If everything went fine, we can now test it in the Python console::

   >>> from xnd import xnd
   >>> from square import square
   >>> a = xnd([1., 2., 3.])
   >>> a
   xnd([1.0, 2.0, 3.0], type='3 * float64')
   >>> square(a)
   xnd([1.0, 4.0, 9.0], type='3 * float64')
