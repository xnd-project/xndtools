.. meta::
   :robots: index, follow
   :description: xndtools notes
   :keywords: xnd

.. sectionauthor:: Pearu Peterson <pearu.peterson at gmail.com>

=============================
Representation of XND objects
=============================

The XND project aims at providing a set of C libraries for storing
data (libxnd), for describing the data (libndtypes), and for
manipulating the data (libgumath). Each library is developed
separately, however, libxnd requires libndtypes, and libgumath depends
on both libxnd and libndtypes. In this note libxnd and libndtypes are
discussed, in particular, how xnd objects are represented in memory
and what are the relations between various members of data structures.

Embedding data in memory
========================

In libxnd the data is stored using the following data strucure:

::

  xnd_master_t
    flags : uint32_t
    master : xnd_t

  xnd_t
    bitmap : xnd_bitmap_t
    index : int64_t
    type : ndt_t*
    ptr : char*

  xnd_bitmap_t
    data : uint8_t*
    size : int64_t
    next : xnd_bitmap_t*

  ndt_bytes_t
    size : int64_t
    data : uint8_t*
    
where ``*`` represents pointer values of the corresponding data types.
The corresponding C `typedef` definitions are in `libxnd/xnd.h`.

A short decription of data type members is given in the following table:

======================== =========================================================
Member                   Description
======================== =========================================================
``xnd_master_t::flags``  Contains ownership information about the ``data``, ``type``, and ``ptr`` members. Needed for memory management.
``xnd_master_t::master`` An xnd view of data.
``xnd_t::bitmap``        Implements optional value support. 
``xnd_t::index``         Linear index of data items. Used only when ``type->tag`` is ``FixedDim|VarDim`` (data is an array of items).
``xnd_t::type``          Points to a type value (``ndt_t`` is provided by libndtypes, see below).
``xnd_t::ptr``           Points to a computer memory where data is embedded. Data can be stored as bytes (``ptr`` points to ``ndt_bytes_t`` value) or referred by its pointer value (``ptr`` points to data value pointer). In the case of arrays and ``type->ndim==0``, ``ptr`` points to the data item given by ``index``.
``xnd_bitmap_t::data``   Points to a bitmap data. Each data item (in ``ptr``) has the corresponding bit value in ``data``. Bit value ``0`` means that data item value has been provided.
``xnd_bitmap_t::size``   Number of subtree bitmaps. This is nonzero when ``type->tag`` is ``Tuple|Record|Ref|Constr|Nominal``.
``xnd_bitmap_t::next``   Refers to bitmaps of subtrees. Used when data has tree-like structure.
``ndt_bytes_t::size``    Number of bytes needed to store data.
``ndt_bytes_t::data``    Points to computer memory where data is stored as bytes.
======================== =========================================================

Note that the linear index is varied during iterations.

Typing the data
===============

Typing the data means attaching a meaning to a junk of data stored in
computer memory.  The libndtypes implements data types using ndtypes
type language ( Blaze datashape) that combines the shape and element
type information in one unit. Note that ndtypes is similar to the
Python based implementation of Blaze datashape but there are several
differences to make these distinct.

Ndtypes uses the following data structure:

::
   
   ndt_t
     tag : enum ndt {Module, Function, AnyKind, ..., Typevar}
     access : enum ndt_access {Abstract, Concrete}
     flags : uint32_t
     ndim : int
     datasize : int64_t
     align : uint16_t

     // Abstract part
     union
       Module
         name : char*
	 type : ndt_t*
       Function
         nin : int64_t
         nout : int64_t 
         nargs : int64_t 
         types : ndt_t**
       FixedDim | SymbolicDim | EllipsisDim | Constr
         shape : int64_t 
         type : ndt_t*
       VarDim | Ref
         type : ndt_t*
       Tuple
         flag : enum ndt_variadic {Nonvariadic, Variadic}
         shape : int64_t 
         types : ndt_t**
       Record
         flag : enum ndt_variadic
         shape : int64_t
	 names : char**
         types : ndt_t**
	 
     Concrete
       union
         FixedDim
	   itemsize : int64_t
	   step : int64_t
	 VarDim
	   flag : enum ndt_offsets {InternalOffsets, ExternalOffsets}
	   itemsize : int64_t
           noffsets : int32_t
           offsets : int32_t*
           nslices : int
           slices : ndt_slice_t*;
	 Tuple | Record
	   offset : int64_t*
           align : uint16_t*
           pad : uint16_t*
	 Nominal
           name : char*
           type : ndt_t*
           meth : ndt_methods_t*
	 Categorical
	   ntypes : int64_t
           types : ndt_value_t*
	 FixedString
	   size : int64_t
           encoding : enum ndt_encoding {Ascii, Utf8, Utf16, Utf32, Ucs2}
	 FixedBytes
	   size : int64_t
           align : uint16_t
	 Bytes
           align : uint16_t
	 Char
           encoding : enum ndt_encoding
	 Typevar
           name : char*

While the definition of ``ndt_t`` looks long, the union parts share
the same memory and the interpretation of this depends on the
ndtypes kind (specified by ``ndt_t::tag`` member).

Note that ``ndt_t`` holds both the shape and item type information of
the xnd view object.

The ndtypes implementation ``ndt_t`` can be used in two modes,
*abstract* or *concrete*, specified by ``ndt_t::access`` member.  The
ndtypes is in concrete mode when it contains enough information
needed to compute what is the contiguous memory size (``datasize``)
that fits the first and last item of the data. Otherwise the
ndtypes is in abstract mode.

The abstract ndtypes can be used only as patterns.  The concrete
ndtypes can be used as patterns as well as for describing the
structure of a data stored in a xnd view object (``xnd_t`` instance).

Here follows a summary of data type members:

============================= =========================================================
Member                        Description
============================= =========================================================
``xnd_t::tag``                Specifies ndtypes kind.
``xnd_t::access``             Specifies ndtypes mode, abstract or concrete.
``xnd_t::flags``              Contains various information about the data type: endianess, optional, subtree, ellipses.
``xnd_t::ndim``               Specifies dimension index. Ndtypes with ``ndim==0`` is interpreted as the ndtypes of a scalar value.
``xnd_t::datasize``           Size of data item in bytes [undefined in abstract mode]
``xnd_t::align``              Alignemnt of data in bytes [undefined in abstract mode]
``xnd_t::Module``             Abstract part of ``Module`` type kind.
``...``                       ...
``xnd_t::Concrete::FixedDim`` Concrete part of ``FixedDim`` type kind.
``...``                       ...
============================= =========================================================



In the following each ndtypes kind is described in separate subsections.

Arrays
------

Array is a data structure that contains data items of the same data
type.  When data items use the same amount of memory, representation
of an array is particularly simple: one only needs to know the
location of the first data item in memory and the byte-size of data
item type in order to have access to any data item in the array.
However, there exists data types such as strings or ragged arrayswhere
the data item byte-size depends on the data item content and a more
general representation of array structure is needed.

In libndtypes several kinds of array representations are supported.

In abstract mode one can represent arrays of different item types
(named type variable), of different dimensions (ellipses), and of
different shapes (symbolic dimensions) using a single ndtypes
instance. The purpose of such ndtypes instances is to define
patterns of arrays that is used in libgumath. The libgumath library
provides computational kernels that implement algorithms to manipulate
data with specific structure. The kernels can be called only on data
that ndtypes matches the signature of a particular kernel.

In concrete mode the main purpose of a ndtypes instance is to provide
information how to access the data items in an array (using also the member ``xnd_t::index``).

Abstract array ndtypes
++++++++++++++++++++++

Ndtypes is in abstract mode when ``ndt_t::access==Abstract``. 

======================================= =========================================================
Member                                  Description
======================================= =========================================================
``ndt_t::tag==FixedDim``                Ndtypes represents an array dimension with fixed shape value
``ndt_t::FixedDim::shape``              Specifies the shape value of the array dimension
``ndt_t::FixedDim::type``               Points to data item type specification.
``xnd_t::datasize``                     undefined
``xnd_t::align``                        undefined
``xnd_t::Concrete::...``                undefined
======================================= =========================================================

*Undefined* means that the value is set to ``0`` or ``NULL``.

Note that ``FixedDim`` ndtypes is in abstract mode when ``type`` ndtypes is in abstract mode.

=========================== =========================================================
Member                      Description
=========================== =========================================================
``ndt_t::tag==VarDim``      Ndtypes represents an array dimension that shape may vary
``ndt_t::VarDim::type``     Points to data item type specification.
``xnd_t::datasize``         undefined
``xnd_t::align``            undefined
``xnd_t::Concrete::...``    undefined
=========================== =========================================================

============================ =========================================================
Member                       Description
============================ =========================================================
``ndt_t::tag==SymbolicDim``  Ndtypes represents an array dimension that shape is a symbolic.
``ndt_t::SymbolicDim::name`` Contains symbol name.
``ndt_t::SymbolicDim::type`` Points to data item type specification.
``xnd_t::datasize``          undefined
``xnd_t::align``             undefined
``xnd_t::Concrete::...``     undefined
============================ =========================================================

The shape symbol must start with a capital letter.

============================ =========================================================
Member                       Description
============================ =========================================================
``ndt_t::tag==EllipsisDim``  Ndtypes represents 0 or more dimensions.
``ndt_t::EllipsisDim::name`` Contains ellipsis name.
``ndt_t::EllipsisDim::type`` Points to data item type specification.
``xnd_t::datasize``          undefined
``xnd_t::align``             undefined
``xnd_t::Concrete::...``     undefined
============================ =========================================================

The named ellipsis name must start with a capital letter or be equal
to ``'var'``.  Ellipsis ``var...`` is special and it is used only for
ragged arrays (when ``ndt_t::tag==VarDim``).

Concrete array ndtypes
++++++++++++++++++++++

Ndtypes is in concrete mode when ``ndt_t::access==Concrete``. 

In the case of fixed shape arrays we have:

======================================= =========================================================
Member                                  Description
======================================= =========================================================
``ndt_t::tag==FixedDim``                Ndtypes represents an array dimension with fixed shape value
``ndt_t::FixedDim::shape``              Specifies the shape value of the array dimension
``ndt_t::FixedDim::type``               Points to data item type specification.
``xnd_t::datasize``                     Specifies the byte-size of array data
``xnd_t::align``                        Alignment of data item.
``xnd_t::Concrete::FixedDim::itemsize`` Specifies the byte-size of array item.
``xnd_t::Concrete::FixedDim::step``     Specifies the byte-step to the next item in array. E.g. in the case of slice view the step is a integer multiple of itemsize.
======================================= =========================================================

Note that the ``datasize`` is defined as the byte-size of memory that
is occupied between the first and the last array item (including the
items that are discarded due to slicing with ``step!=1``). So,
``datasize`` does not correspond to the size of memory needed to hold
the data defined by xnd view, it only defines the upper bound.

In the case of ragged arrays we have:

====================================== =========================================================
Member                                 Description
====================================== =========================================================
``ndt_t::tag==VarDim``                 Ndtypes represents an array dimension that shape may vary
``ndt_t::FixedDim::type``              Points to data item type specification.
``xnd_t::datasize``                    Specifies the byte-size of array data
``xnd_t::align``                       Alignment of data item.
``xnd_t::Concrete::VarDim::flag``      Specifies the ownership of offsets data.
``xnd_t::Concrete::VarDim::itemsize``  Specifies the byte-size of array item.
``xnd_t::Concrete::VarDim::noffsets``  Specifies the byte-size of ``offsets`` member.
``xnd_t::Concrete::VarDim::offsets``   
``xnd_t::Concrete::VarDim::nslices``   Specifies the byte-size of ``slices`` member.
``xnd_t::Concrete::VarDim::slices``
====================================== =========================================================
