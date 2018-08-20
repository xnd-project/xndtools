.. meta::
   :robots: index, follow
   :description: xndtools notes
   :keywords: xnd

.. sectionauthor:: Pearu Peterson <pearu.peterson at gmail.com>

=======================================================
Array arguments in generated gumath kernels: algorithms
=======================================================

Introduction
------------

For a single `gumath` kernel several implementations can
co-exists. Which one of these implementations will be used for
computations depends on the integral nature of kernel input arguments:

- input arguments shapes and types must match the shape-type pattern
  of a kernel signature,
  
- input arguments data layouts determine whether more efficient
  kernel implementations can be used for particular inputs.

This note document is created to analyze how the selection of kernel
implementations works depending on the data layout of given input
arguments. For simplicity we assume than no ellipses are used in
kernel signatures.

`gumath` kernel selection and kernel implementations
----------------------------------------------------

`gumath` kernel selection algorithm works as follows:

- when *all* input arguments are C- or F-contiguous, kernel
  implementations of `C` or `Fortran` kinds are used, respectively;

- otherwise, the most general kernel implementation of `Xnd` kind will
  be used. This includes cases when at least one of the input
  arguments is non-contiguous or have different layout property from
  other input arguments.

Note that the data layout property (`C` or `Fortran`), plays a role
only when the number of argument dimensions is greater than 1. In the
following such arguments are called tensor arguments.  Otherwise, the
argument is either a 0-D array (scalar argument) or 1-D array (vector
argument, `C` or `Fortran` layouts are equivalent).

So, when all kernel arguments are 0 or 1 dimensional arrays, kernel
implementation of `Fortran` kind is never used, except when the `C`
kind of a kernel is not implemented.

`xndtools` kernel generator
---------------------------

`xndtools` kernel generator is a tool that helps generating kernels
for existing C functions. As a rule, the array input arguments to
existing C functions must be either C- or F-contiguous.

If the arguments must have mixed layouts (for instance, one argument
must be C-contiguous and another F-contiguous) then only `Xnd` kind of
kernel implementations can be used.

So, `xndtools` kernel generator can create kernel implementations
according to the following table:

+----------------------------------+------------------------+
| C function arguments:            | Implementation kinds   |
|           layout and shape       +------+------+----------+
|                                  | Xnd  | C    | Fortran  |
+==================================+======+======+==========+
| only scalars and vectors         | yes  |  yes |   no     | 
+----------------------------------+------+------+----------+
| all tensors must be C-contiguous | yes  |  yes |   no     |
+----------------------------------+------+------+----------+
| all tensors must be F-contiguous | yes  |   no |  yes     |
+----------------------------------+------+------+----------+
| tensors are C- and F-contiguous  | yes  |   no |   no     | 
+----------------------------------+------+------+----------+

Here "no" means that the corresponding implementation kind would
contradict with expected argument layouts or be equivalent to `C`
kind.

In `xndtools` kernel generator configuration file one can specify:

- `prototypes` for C functions:

  * ``prototypes[C]`` is used in `C` kind of kernel implementation;
  * ``prototypes[Fortran]`` is used in `Fortran` kind of kernel
    implementation;
  * ``prototypes`` is used in `Xnd` kind of kernel implementation, as
    well as for `C` and `Fortran` kinds when the corresponding
    ``prototypes[...]`` keys are not used.

- `fortran` intent for C function (tensor) arguments to indicate that
  the argument data is F-contiguous. This is only useful when there
  both C- and F-contiguous tensor arguments are used by the C function
  because `Fortran` kind of kernel implementation already implies that
  the arguments are F-contiguous.

- various argument intents such as `input`, `inplace`, `inout`,
  `hide`, `output`, `input/output`, `inplace/output`, and
  `inout/output`.

Handling arguments in generated gumath kernels
----------------------------------------------

Let us introduce the following notations:

``cfunc(T s, T* a)``
  A C function where ``T`` is some type specification, ``s`` is a
  scalar argument and ``a`` is an array argument (0, 1, or more
  dimensions).

``kernel(S, A, O)``
  A gumath kernel where ``S`` represent a `xnd` scalar object and
  ``A`` represents a `xnd` input array object and ``O`` represents a
  `xnd` output array object.

``get_data_ptr(A) -> T*``
  A function that returns pointer to ``A`` data.

``is_c_contiguous(A) -> bool``, ``is_f_contiguous(A) -> bool``
  Functions that test whether ``A`` is C- or F-contiguous.

``ccopy(A) -> T*``
  A function that returns newely allocated memory and copies ``A``
  content to it in C-contiuous way. Caller is responsible freeing the
  memory.

``fcopy(A) -> T*``
  A function that returns newely allocated memory and copies ``A``
  content to it in F-contiuous way. Caller is responsible freeing the
  memory.

``inv_copy(a, A)``
  A function that copies C-contiguous data in ``a`` to ``A``.

``inv_fcopy(a, A)``
  A function that copies F-contiguous data in ``a`` to ``A``.

``nbytes(A)``
  A function that returns the size of ``A`` in bytes.

In the following, ``copy`` is ``fcopy`` for Fortran kernels and
``ccopy`` for C kernels.  Similarly, ``is_contiguous`` is
``is_f_contiguous`` for Fortran kernels and ``is_c_contiguous`` for C
kernels.
  
In the following are presented the algorithms that `xndtools` kernel
generator implements for particular type of arguments.

All kernels: scalars
````````````````````

``input|inplace|inout: s``::

  s = get_data_value(S)
  cfunc(s)

``input|inplace|inout,output: s``::

  s = *get_data_ptr(S)
  cfunc(s)
  *get_data_ptr(S) = s

``output: s``::

  s = 0
  cfunc(s)
  *get_data_ptr(S) = s

``hide: s``::

  s = 0
  cfunc(s)

``input|inplace|inout: s = s0``::

  if is_na(S):
    s = s0
  else:
    s = get_data_value(S)
  cfunc(s)

``input|inplace|inout,output: s = s0``::

  if is_na(S):
    s = s0
  else:
    s = *get_data_ptr(S)
  cfunc(s)
  *get_data_ptr(S) = s

``output: s = s0``::

  s = s0
  cfunc(s)
  *get_data_ptr(S) = s

``hide: s = s0``::

  s = s0
  cfunc(s)

Note: for scalars with ``inplace|inout|output`` intent the C function
is in the form ``cfunc(*s)`` and the corresponding calls are in a form
``cfunc(&a)``.
  
Fortran kernel: F-contiguous tensor, or C kernel: C-contiguous tensor
`````````````````````````````````````````````````````````````````````

``input|inplace|inout: a``::

  a = get_data_ptr(A)
  cfunc(a);

``output``::

  a = get_data_ptr(O)
  cfunc(a);

``hide: a``::

  a = malloc(sizeof(T)*<shape-product>)
  if a != NULL:
    cfunc(a);
    free(a)
  else: <memory-error>

``input|inplace|inout, output: a``::

  a = get_data_ptr(O)
  inv_copy(a, A)
  cfunc(a);


Xnd kernel: C- or F-contiguous tensor or C-contiguous vector
````````````````````````````````````````````````````````````

``input: a``::

  if is_contiguous(A):
    a = get_data_ptr(A)
  else:
    a = copy(A)
  if a != NULL:
    cfunc(a);
    if not is_contiguous(A):
      free(a)
  else: <memory-error>

``inplace: a``::

  if is_contiguous(A):
    a = get_data_ptr(A)
  else:
    a = copy(A)
  if a != NULL:
    cfunc(a);
    if not is_contiguous(A):
      inv_copy(a, A)
      free(a)
  else: <memory-error>

``inout: a``::

  if is_contiguous(A):
    a = get_data_ptr(A)
    cfunc(a);
  else: <value-error>  

``output: a``::

  a = malloc(sizeof(T)*nbytes(O))
  if a != NULL:
    cfunc(a);
    inv_copy(a, O)
    free(a)
  else: <memory-error>

  TODO: optimize when ndtypes will support F-contiguous O
    
``hide: a``::

  a = malloc(sizeof(T)*<A-shape-product>)
  if a != NULL:
    cfunc(a);
    free(a)
  else: <memory-error>

``input,output: a``::

  if is_contiguous(A):
    a = get_data_ptr(A)
  else:
    a = copy(A)
  if a != NULL:
    cfunc(a);
    inv_copy(a, O)
    if not is_contiguous(A):
      free(a)
  else: <memory-error>

``inplace,output: a``::

  if is_contiguous(A):
    a = get_data_ptr(A)
  else:
    a = copy(A)
  if a != NULL:
    cfunc(a);
    inv_copy(a, O)
    if not is__contiguous(A):
      inv_copy(a, A)
      free(a)
  else: <memory-error>

``inout,output: a``::

  if is_contiguous(A):
    a = get_data_ptr(A)
    cfunc(a);
    inv_copy(a, O)
  else: <value-error>

All kernels, C function return value
````````````````````````````````````

For non-void functions the return value is assigned to the extra
output argument ``R`` of the kernel. Such argument is always the last one::

  r = cfunc(...)
  *get_data_ptr(R) = r
