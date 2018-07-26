==========================
Running kernels on the GPU
==========================

We will see how we can run kernels on the GPU. The following is a typical CUDA
code which adds the elements of two arrays of a given size:

.. code-block:: c

   // file: add_gpu.cu

   #include "gpu.h"
   
   __global__
   void add(int n, float* x, float* y, float* r)
   {
       int index = blockIdx.x * blockDim.x + threadIdx.x;
       int stride = blockDim.x * gridDim.x;
       for (int i = index; i < n; i += stride)
           r[i] = x[i] + y[i];
   }
   
   void add_gpu(int n, float* x, float* y, float* r)
   {
       int blockSize = 256;
       int numBlocks = (n + blockSize - 1) / blockSize;
       add<<<numBlocks, blockSize>>>(n, x, y, r);
       cudaDeviceSynchronize();
   }

The ``add`` function is called a CUDA kernel (not to be confused with the
``gumath`` kernels!). This is what will actually run on the GPU. The reason why
a GPU is faster than a CPU is because it can massively parallelize
computations, and this is why we have these ``index`` and ``stride`` variables:
the kernel will be applied on different parts of the data at the same time.

Our ``gumath`` kernel however will use the ``add_gpu`` function, which
internally calls ``add`` with a special CUDA syntax and some extra-parameters
(basically specifying how much it will be parallelized). The
``cudaDeviceSynchronize()`` function call blocks the CPU execution until all
GPU computations are done.

The GPU has its own memory, which is different from the CPU memory. When we
want to do a computation on the GPU, we first have to copy the data from the
CPU side to the GPU side, and when we want to retrieve the results from the
GPU, we have to copy its data back to the CPU. This can be taken care of by the
so called "unified memory", which provides a single memory space accessible by
the GPU and the CPU. The following file contains functions to allocate memory
in the unified memory and to delete it, here again through special CUDA
functions:

.. code-block:: c

   // file: gpu.cu

   #include "gpu.h"
   
   float* get_array(int n)
   {
       float* x;
       cudaMallocManaged(&x, n * sizeof(float));
       return x;
   }
   
   void del_array(float* x)
   {
       cudaFree(x);
   }

Now let's see how the ``gpu.h`` file looks like:

.. code-block:: c

   // file: gpu.h
   
   extern "C" void add_gpu(int n, float* x, float* y, float *r);
   extern "C" float* get_array(int n);
   extern "C" void del_array(float* x);

It consists of the prototypes of the ``add_gpu`` function for which we want to
make a kernel, and the ``get_array`` and ``del_array`` functions which we will
use to manage the memory for our data. Note the ``extern "C"`` declaration:
because ``nvcc`` (the CUDA compiler) is a C++ compiler, we need to expose them
as C functions to Python.

Since ``gpu.cu`` only manages the GPU memory, and is independent of the
``gumath`` kernel generation, we will simply access its functions through a
shared library.  This is how we compile it:

.. code-block:: bash

   $ nvcc -o libgpu.so --compiler-options "-fPIC" --shared gpu.cu

This gives us a ``libgpu.so`` library that we can interface with in Python using
``ctypes``. The following code wraps the C functions to Python functions:

.. code-block:: python

    # file: gpu.py

    import ctypes
    import numpy as np
    from xnd import xnd
    
    gpu = ctypes.CDLL('./libgpu.so')
    gpu.get_array.restype = ctypes.POINTER(ctypes.c_float)
    gpu.del_array.argtypes = [ctypes.POINTER(ctypes.c_float), ]
    
    def xnd_gpu(size):
        addr = gpu.get_array(size)
        a = np.ctypeslib.as_array(addr, shape=(size,))
        x = xnd.from_buffer(a)
        return x, addr
    
    def del_gpu(addr):
        gpu.del_array(addr)

``xnd_gpu`` returns an XND container (and its data pointer) whose data live in
the unified memory, and ``del_gpu`` frees the memory referenced by a pointer.

Now we need to generate the ``gumath`` kernel for our ``add_gpu`` function. We
save its prototype in the following file:

.. code-block:: c

   // file: add_gpu.h

   extern void add_gpu(int n, float* x, float* y, float *r);

The corresponding configuration file looks like this:

.. code-block:: none

   # file: add_gpu-kernels.cfg

   [MODULE add_gpu]
   typemaps = 
   	float: float32
   	int: int32
   includes = 
   	add_gpu.h
   include_dirs = 
   sources =
   	add_gpu.c
   	
   libraries = 
   	
   library_dirs = 
   	
   header_code = 
   kinds = C
   ellipses = none
   
   [KERNEL add_gpu]
   prototypes = 
   	void add_gpu(int   n, float *  x, float *  y, float *  r);
   description = 
   dimension = x(n), y(n), r(n)
   input_arguments = x, y
   inplace_arguments = r
   hide_arguments = n = len(x)

We can now generate the kernel:

.. code-block:: bash

   $ xnd_tools kernel add_gpu-kernels.cfg
   $ xnd_tools module add_gpu-kernels.cfg

And create a static library:

.. code-block:: bash

   $ nvcc --compiler-options '-fPIC' -c add_gpu.cu
   $ gcc -fPIC                                               \
   $ -c add_gpu-kernels.c                                    \
   $ -c $SITE_PACKAGES/xndtools/kernel_generator/xndtools.c  \
   $ -I$SITE_PACKAGES/xndtools/kernel_generator              \
   $ -I$SITE_PACKAGES/xnd                                    \
   $ -I$SITE_PACKAGES/ndtypes                                \
   $ -I$SITE_PACKAGES/gumath
   $ ar rcs libadd_gpu-kernels.a add_gpu.o add_gpu-kernels.o xndtools.o

Finally, launch ``python setup.py install`` with this ``setup.py`` file:

.. code-block:: python

   # file: setup.py

   from distutils.core import setup, Extension
   from distutils.sysconfig import get_python_lib
   
   site_packages = get_python_lib()
   lib_dirs = [f'{site_packages}/{i}' for i in ['ndtypes', 'gumath', 'xnd']]
   
   module1 = Extension('add_gpu',
                       include_dirs = lib_dirs,
                       libraries = ['add_gpu-kernels', 'ndtypes','gumath', 'xnd', 'cudart', 'stdc++'],
                       library_dirs = ['.', '/usr/local/cuda-9.2/lib64'] + lib_dirs,
                       sources = ['add_gpu-python.c'])
   
   setup (name = 'add_gpu',
          version = '1.0',
          description = 'This is a gumath kernel extension that adds two XND containers on the GPU',
          ext_modules = [module1])

If everything went fine, you should be able to run the kernel on the GPU::

   >>> from gpu import xnd_gpu, del_gpu
   >>> from add_gpu import add_gpu
   >>> size = 1 << 20
   >>> x0, a0 = xnd_gpu(size)
   >>> x1, a1 = xnd_gpu(size)
   >>> x2, a2 = xnd_gpu(size)
   >>> for i in range(size):
   ...     x0[i] = i
   ...     x1[i] = 1
   >>> x0
   xnd([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, ...], type='1048576 * float32')
   >>> x1
   xnd([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, ...], type='1048576 * float32')
   >>> add_gpu(x0, x1, x2)
   >>> x2
   xnd([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, ...], type='1048576 * float32')
   >>> del_gpu(a0)
   >>> del_gpu(a1)
   >>> del_gpu(a2)
