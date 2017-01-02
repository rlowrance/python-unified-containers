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

## Operations consistent with Q's built-in operators

PUC is inspired in part by the Q language. This section covers all of Q's operators and
explains how PUC treats them. The source for the function names is [code.kx.com/wiki/Reference].

All the operators return a vector of the same shape as self, except where noted.

Mathematical operators

    V.abs()       absolute value
    V.acos()      arc cosine, result in radian in [0, pi]
                  return None if arg is not in [-1, 1]
    V.all()       return Python boolean, False iff one element of V is 0
    V.and(y)      minimum
    V.any()       return Python boolean, True iff any element of V is not 0
    V.asc()       ascending
                  for homogenous vector, return sorted new vector
                  for mixed vector, return new vector sorted within data type
                  set newV.attribute = "sorted"
    V.asin()      arc sine, result in radians in [-pi/2, pi/2]
                  return None if arg is not in [-1, 1]
    V.atan()      arc tangent, result in radian in [-pi/2, pi/2]
                  return None if ?
    V.attr()      return attribute, a string in {"sorted", "unique", "partitioned", "true index"}
                  in this version of PUC, these attributes are not used to optimize operations
    V.avg()       return Python float, the mean
                  return None if V is empty or contains either +inf or -inf
                  ignore any None values in V
    V.avgs()      return Vfloat64 containing running averages
    V.bin(y)      return Vint64 giving index of the last element in V <= y
                  return -1 for y less than first element of x
    V.binr(y)     return index i of first element in self[i] >= y
    V.ceiling()   return Vint64, where each item is the least integer >= self[i]
    V.cor(y)      return Python float in [-1, 1], the correlation of self and y
    V.cos()       return Vfloat64, the cosines in [-1, 1]
                  return None if self[i] is +inf or -inf, result is Vobject
    V.count()     return Python int, the length of V. Return 0 for 0 length
                  vector and Python scalar.
    V.cov(y)      return covariance
    V.cross(y)    return cross-produce (all possible combinations)
    V.cut(y)      split y according to self
                  if self is a single integer, split y into self-sized parts
                  if self is a non-decreasing list of ints, cut y at indices given in self
    V.deltas(y)   return differences between consecutive pairs
    V.desc()      return sorted list in descending order; set newV.attribute = "sorted"
    V.dev()       return standard deviation
    V.differ()    return Vint8 according to whether consecutive pairs differ
    V.distinct()  return unique elements in a new vector
    V.div(y)      return integer division (floor of self / y)
    V.except(y)   return all elements of self not in y
    V.exp()       return Vfloat64 containing e^self
    V.fills()     return self, except that where self is None, result preceeding non-None value
    V.first()     return self[0], which may be a Python object or a Vector
    V.flip()      return transpose of self
    V.floor()     return greatest integer <= self[i]
    V.group()     return D where
                  keys are the distinct elements of self
                  values are the indices where the elements occur
    V.iasc()      return Vint64 of indices that sort self in increasing order
    V.idesc()     return Vint64 of indices that sort self in descending order
    V.in()        return Vint8 indicated which items in self are in y
    V.inter(y)    return Vector of common elements
    V.inv()       return Vobject containing inverse of the matrix self
    V.key()       return keys of dictionary
    V.last()      return last element of self
    V.like(y)     return Vint8 indicating which items in self match the pattern y
    V.log()       return natural log; None if self[i] is neg, -inf if self[i] is 0
    V.lower()     return Vector in lower case
    V.lsq()       least squares; matrix divide; return least squares solution to x = w mmu y
    V.mavg(y)     return moving average
    V.max()       return max of self
    V.maxs()      returm maximums of the prefixs of self
    V.mcount(y)   return self-item moving count of y
    V.mdev(y)     return self-item moving deviation of y
    V.med()       return Python number containing the median of self
    V.min()       return minimum of self
    V.mins()      return minimums of prefixes of self
    V.mmax(y)     return self-item moving maximum of y
    V.mmin(y)     return self-item moving minimum of y
    V.mmu(y)      return matrix multiplication of self and y, both of which are Vobjects
    V.mod(y)      return self mod y
    V.msum(y)     return self-item moving sum of y
    V.neg()       return negative of self
    V.next()      return next item, appending a None (shift left); return Vobject
    V.not()       return Vint8 of 0 and 1
    V.null()      return True if self is None
    V.or(y)       return max of self and y
    V.prd()       return product of argument
    V.prds()      return cumulative products of its argument
    V.prev()      return previous element of each item
    V.rand()      if x is Python 0, return random value of the same type as x
                  if x is Python positive number, return random number in [0, x)
                  if x is a vector, return random element for the vector
                  if x is a symbol in `1 to `8, return random symbol of length x
                    using first 16 lower case letters of alphabet
    V.rank()      return Vint64 list of same length
                  each item is where the corresponding element would occur in sorted list
    V.ratios()    return ratios of consecutive pairs
    V.raze()      join items of argument and collapse one level of nesting
                  convert atom to one-item list
    V.reciprocal()  cast to float, then return reciprocal
    V.reverse()     return reversed items
    V.rotate(y)     return rotation of self positions of vector y
    V.scov(y)       return statistical covariance as Python float
                    scov(x,y) = (n / n - 1) cov(x,y)
    V.sdev()        return standard deviation
                    sdev(x) sqrt((n/(n-1)) var(x))
    V.show()        format self to the console; do not return the formatted value
    V.signum()      return -1, 0, or 1 if self is negative, zero, or positive
    V.sin()         return sin of self in radians, result in [-1,1] or null if self is None or inf
    V.sqrt()        return Vfloat64 square root, or None if arg is negative or None
    V.ss(y)         (string search) return positions of y in self
                    uses pattern matching from like
    V.string()      return vector with each item of self converted to string
    V.sublist(y)    return sublist of y as specified by self
                    if self is a single positive integer, return self items from beginning of y
                    if self is a single negative integer, return self items from end if y
                    if self is an integer pair, return self[1] items from y starting at self[0]
    V.sum()         return sum
    V.sums()        return cumulative sum
    V.svar()        return statistical variance
                    svar(x) = (n / (n - 1)) var(x)
    V.system()      execute system command self returning a result
    V.tan()         return tangent of arg in radians, return None if arg is None or inf
    V.til()         return first self integers as Vint64
    V.trim()        return string with leading and trailing spaces removed
    V.type()        return Python int representing the type
    V.union(y)      return vector of distinct elements in the appended self and y
    V.upper()       return Vector in upper case
    V.var()         return Python float of variances; ignore None values
    V.wavg(y)       return Python float, the x-weighted average of y values
    V.where()       return vector with self[i] copies of i
    V.within()      return Vint8 1 iff self[i] within bounds of the right argument
    V.wsum(y)       return Python float, the sum of self * y
    V.xbar(y)       return round of y to nearest multiple of self
    V.xexp(y)       return x^y
    V.xlog(y)       return log_x (y)
    V.xprev(y)      return self-th previous element of each item in y
    V.xrank(y)      return allocation of y to self buckets

All the methods are vectors are also defined as functions in module PUC, taking 1 or 2 
arguments. For example, instead of executing `V.abs()`, one can execute `PUC.abs(x)` and
instead of executing `V.cor(y)`, one can execute `PUC.cor(x,y)`. This facility is useful
when methods cannot be used, because self would be a Python object that doesn't accept
method calls; for example, Python numbers do not accept method calls.

Some operations are not offered as methods. These are:

    PUC.gtime(dt)  return UTC global date and time
    PUC.ltime()    return UTC local date and time
    PUC.ltrim(s)   remove leading spaces from string
    PUC.md5(s)     return Message-Digest 5 128-bit value of its string argument
    PUC.rtime(s)   return string with trailing spaces removed
    PUC.ssr(x,y,z) replace occurences of y in x with z
                   z is a string or function evaluated on the matching substring
                   use ss to do the search
    PUC.sv(x,y)    return a Python scalar from y
                   if x is string, join strings in y separated by x
                   if x is backtick, join strings in y separated by host line separator
                   if x is backtick, join symbols in y separated by slashes; return file handle
                   if x and y are numeric, return y to base x
                   if x is a list, return <see documentation>
                   if x is 0 and y is a VintN, convert y to corresponding Python integer
    PUX.vs(x,y)    return Vector
                   if x and y are strings, cut y using x as the delimiter
                   if x is False and y is an integer, return bit representation of y as Vint8
                   if x is 0 and y is a number, return hex representation of y as Vint64
                   if x is backtick, split symbols on "."
                                     break file handles into directory and file part
                                     break string into platform-aware lines discarding newlines

Q operators that are not implemented in this version of PUC because they are used for
Q's tables are:

    aj       as of join
    aj0      as of join
    asof     as of verb
    cols     return list of column names of table
    delete   delete rows and columns from a table
    dsave    save table to disk as splayed, unemerated, indexed table
    ej       equijoin verb (join two table on given list of columns)
    enlist   return argument as list; convert dictionary to table
    fby      filter by
    fkeys    return dictionary that maps foreign key columns to their tables
    ij       inner join (join two tables o the key columns y)
    insert   append records to a table
    keys     returns symbol list of the primary key columns
    lj       left join
    meta     return meta data of table in the form of a keyed table
    pj       plus join; join on key columns of right argument
    rload    load a splayed table
    rsave    save a table splayed to a directory
    select   select columns by groups from table where filters
             select[n] select[m n] select[order] select[n;order]
    tables   return sorted list of table in namespace
    txf      indexed lookup on keyed table
    uj       union join
    ungroup  flatten a table
    update   update a table
    upsert   add record to table
    wj       window join
    wj1      window join
    xasc     sort table in ascending order
    xcol     rename columns in table
    xcols    reorder columns in table
    xdesc    sort table in descending order
    xgroup   groups right argument table for foreign keys in left argument
    xkey     set primary keys in table

Other Q operators which are not yet designed into PUC.

    each     adverb
    eval     evaluate a parse tree
    exec     execute parsed form in specified context
    exit     terminate process
    get      read or memory map a Q data file
    getenv   return value of specified environment variable
    hclose   close file or process handle
    hcount   return size in bytes of file
    hdel     delete a file
    hopen    open file or process
    hsym     convert symbol to file name or hostname, ipaddress
    load     load binary data from file system
    over     adverb
    parse    convert string to parse tree
    peach    parallel each adverb
    prior    apply x (a function) between each item of y and its predecessor
    read0    read text file, returning list of lines with LF and CRLF delimiters removed
    read1    read file as list of bytes
    reval    similar to eval(-6!)
    save     save global data to a file
    scan     adverb
    set      assign right argument to the left, which may be a file name
    setenv   set an environment variable
    value    performs several functions depending on its argument
    view     return expression defining a dependency
    views    return sorted list of currently defined views


