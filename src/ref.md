# PUC Version 0.1 Reference Manual

Python Unified Containers (PUC) will be 4 classes designed to be easy-to-use, high
performance Python containers. 

Version 0.1 implements one of these, is a vector class V.

## The PUC Abstract Class

In a later version of PUC, user's will be able to control how many rows and columns
of items are printed. But this isn't implemented yet in Version 0.1


## The V Abstract Class

V stands for "vector." 

A V instance is similar to a Python list in that it contains
zero or more items which are accessed by non-negative integer subscripts. Unlike 
Python lists, a V instance may also be indexed by a vector of indices, in which case
another V instance is returned.

A V instance
is also similar to a one dimension numpy array in that it densly stores items that
have certain underlying Python types. This version of PUC densly stores 64 bit integers,
64 bit floats, and 8 bit integers. 

### Construction

The class V is abstract, so that it cannot be instantiated. This version implements 4
concrete subclasses: Vint8, Vint64, Vfloat64, and Vobject.

Constructors never lose precision.

Vint8 instances hold signed 8-bit integers. Use Vint8 instances when vectors of 
booleans would be used. They may be constructed in these ways:

    v = Vint8(<python int that fits in 8 signed bits>)
    v = Vint8(<python list of ints that fit in 8 signed bits>)
    v = Vint8(<python tuple>]
    v = Vint8(<Vint8 instance>)
    v = Vint8(<numpy array with dtype int8>)

Vint64 instances hold signed 32-bit integers. They may be constructed in these ways:

    v = Vint64(<python list>)
    v = Vint64(<python tuple>]
    v = Vint64(<Vint8 instance>)  # allowed, since cannot lose precision
    v = Vint64(<Vint32 instance>)
    v = Vint64(<numpy array with dtype int64>)

Vfloat64 instances hold signed 32-bit integers. They may be constructed in these ways:

    v = Vfloat64(<python list>)
    v = Vfloat64(<python tuple>]
    v = Vfloat64(<Vint8 instance>)  # allowed, since cannot lose precision
    v = Vfloat64(<Vfloat64 instance>)
    v = Vfloat64(<numpy array with dtype float64>)

Note that Vfloat64 intances cannot be constructed from Vint64 instances because of the 
possible loss of precision. However, you can force the conversion through an explicit
coercion.

### Indexing

All V instances are indexed in the same ways. Unlike with Python lists, multiple item
may be returned by indexing using a Vint8 or Vint64. Negative indices are not supported.

   <python object> = v[<python integer >= 0>]
   <V object> = v[<python iterable with each item >= 0>]
   <V object> = v[<Vint64 instance>]

Assignment can be used to set one or more items. No coercions are performed 
automatically. If a python scalar value is assigned to more than one item in
a V instance, the python scalar is replicated as many times as required.

   v[<python integer >= 0>] = <python number>  # throws if a coercion would be needed
   v[<python iterable with each item >= 0>] = <V object>
   v[<Vint64 instance>] = V<object>

### Coercions

V instances can be coerced to other types, possibly with loss of precision. Conversions 
from floating point to integer types use rounding. Q: What happens to very large integers
when converted to floats?

     V.to_numpy(v_instance)  # convert to numpy array
     V.to_Vint8(v_instance)  # convert to Vint8, possibly with loss of precision
     V.to_Vint64(v_instance)   # convert to Vint8, possibly with loss of precision
     V.to_Vfloat64(v_instance) # convert to Vfloat64

### Operations consistent with emulating Python's container types

Unlike Python lists, a V instance can be indexed by another V instance, where upon
they return a vector. The facility is intended to reduce the need for explicit looping
over indices.

    v.__len__(self)             # return len(v),
    v.__reversed__(self)        # return reversed(v), with items in reverse order
    v.__contains__(self, python_object)  # return a Python boolean
    v.__contains__(self, vint8)    # return v[i] s.t. vint8[i] != 0
    vint64.__contains__(self, other_vint64)      # return vint8
    vfloat64.__contains__(self, other_vfloat64)  # return vint8
    v.__iter__(self)   # return iterator for the items

### Operations consistent with immutable Python containers.

These methods are provided so that V instances emulate Python mappings. In all
these methods calls, `other` may be a V instance, in which case, a V instance is
returned.

    v.__keys__(self)  # return iterator over the integers 0, 1, ... len(v) - 1
    v.__values__(self)  # return iterator over the values
    v.__items__(self)   # return iterator over the (index,value) pairs
    v.__iteritems(self) # return iterator over the values
    v.__iterkeys(self)  # return iterator over the indices
    v.__has_key__(self, other)  # return True iff v[other] would succeed
    v.__get__(self, other[,default]) # return value or default
    v.__pop__(self, other[,default]) # delete and return other or default
    v.__popitem__(self)  # delete and return arbitrary (index,value) pair
    v.__setdefault__(self, other)  # now out of range indices will return other
    v.__update(self, other)  # update v using values in other





### Other operations consistent with emulating Python's numeric types

All of these methods return a new V instance. There are no views in PUC. Python numbers
and length 1 V instances are broadcast. Two V instances each of length > 1, must have
the same length.

The + operator is implemented by the `__add__` method.

    v.__add__(self, python_number)  # add the number to each item in v
    v.__add__(self, v_len_1)        # add the item in v_len_1 to each item in v
    v.__add__(self, v_other)        # len(v_other) == len(v); add element by element

Other operations implemented as for add: sub, mul, floordiv, mod, divmod, pow,
lshift, rshift, and, xor, or, div, truediv. In addition, the reflected versions
are implemented.

The augmented versions (e.g., +=) versions of the operators are also implemented.

These unary methods are implemented: `-`, `+`, `abs()`, `~`.

These functions are *not* implemented: `complex()`, `int()`, `long()`, `float()`. Instead,
call the coercion operators.

These methods are *not* implemented: `__oct__(self)`, `__hex(self)__`, `__index__(self)__,
`__coerce__(self, other)`.
