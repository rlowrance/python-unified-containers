# demonstrate api
# inspirations: Q Language, Torch package for Lua
# key ideas:
# - obvious notation for the programmers; no surprising semantics
# - uniform notation for indexing vectors, matrices, dictionaries, tables

# With ideas from Stephen Hoyer and Jonathan Rocher

from puc_demo import Storage, Vector, Matrix, Tensor, Dictionary, Table, KeyedTable

# Storage holds the actual data
# Vectors, Matrices, and Tensors are views of Storage
# A Storage can have zero or more views

s = Storage(n=10, kind="bool")  # 10 elements
s = Storage(n=100, kind="int64")
s = Storage(n=1000, kind="float64")
s = Storage(n=10000, kind="string")
s = Storage([0, 1, 1, 0], kind="bool")  # data provided
s = Storage(place="memory")
s = Storage(place="GPU")
s = Storage(place=("disk", "path/to/file"))

# There will be ufunc equivalents that apply to Storage

# Vectors are 1D views of parts of or all of a Storage

v = Vector(storage=s)  # all elements, same len as underlying storage
v = Vector(storage=s, shape=[8])  # first 8 elements
v = Vector(storage=s, shape=[5], offsets=[0], strides=[2])  # every other
r = add(v, v)  # ufunc-like capability, result is new view of new storage
v2 = v.deepcopy().make_contiguous()  # new storage, view had stride = 1
add(v2, v2)      # potentially faster than operating on v

# Illustration: what offsets allow
def first_delta(v):
    # require v to have an extra element at the end of its storage
    w = Vector(storage=v.storage, shape=v.shape, offset=1)
    return v - w

# indexing returns same shape as the indexer
x = v[3]       # x is a python scalar
x = v[[0, 3]]  # x is a Vector, a new Storage
x = v[Storage([0, 1, 0, 0, 1, 1, 0, 0, 0, 1], kind="bool")]  # masked selection

# Matrices are 2D views of parts of or all of a Storage
m = Matrix(storage=s, shape=[3, 4], offsets=[0, 0], strides=[1, 1])  # dense
x = m[:, 3]  # one column
x = m[2, :]  # one row
row_mask = Vector([0, 1])
col_indices = Vector(range(10))
x = m[row_mask, col_indices]  # selected rows and columns
x = m[row_mask, :]
x = m[:, col_indices]
x = m[23, :]  # or m[23,...]

# Vectors and Matrices are subclasses of Tensors
# methods on Tensors
t = Tensor()     # API to be defines
t.copy()         # copies view object
t.deepcopy()     # also copies the storage
t.is_contiguous()
t.deep_continguous_copy()  # ufuncs can be optimized for continuous storage

# python: [d[key] for key in key_list]
# python: d[key1, key2] is sugar for d[(key1,key2)]
# above from Jonathan Rocher
# Dictionary is like a python dict but [] can return multiple values
d = Dictionary()  # no storage
d["a"]            # one value
d[v]              # vector of values, returns a new object in general
d[v] = 1          # exands 1 to a vector

# How do you handle assignment to rows and columns?
d['a1']  # returns a view of the data
d[['a1', 'a2']]  # returns an object with new data
d['a']['b'] = 1  # this works
d[['a1', 'a2']]['b'] = 1  # breaks silently (in numpy); warns in pandas (usually)
d[['a1', 'a2'], 'b'] = 1  # this works

# Tables are dictionary-like objects conceptualized as an ordered list of
# records. A Table is like a dataframe without observation names.
#
# Tables are stored column-wise.
c1 = Vector(["a", "b", "c"])
c2 = Vector([10, 20, 30])
tab = Table(c1, c2)  # 2 columns, each with same number of rows
# indexing tables is exactly like indexing Matrix objects
# Pandas Dataframes are stored in blocks (not columns nor rows)
#  attempting to optimize a mix of row-based retrievals and column-based
#  retrieval and slices of both

# KeyedTable are dataframe-ike objects with distinct labels for the rows. It
# is conceptually a dictionary of dictionaries. The unique keys could be,
# for example, datetime stamps.
ktab = KeyedTable()  # syntax TBD

# operations on tables include SQL select, but with semantics slightly
# changed to acknowledge that rows are ordered (as in Q-lang).

t.groupby()  # most of the Pandas dataframe sql-like methods
t.select("where ... group by ... having ... ordered by ...")  # sql statement
t.select(where=x, groupby=x, having=x, orderedby=x,)
# could compile the select statement like Python regex's
# Q has a lambda-expression select statement function (not English)

# see R tidyr, package for tidying up data

# R's plyr methods on data frames (that depend on lazy evaluation)
#  filter(), slice(), arrange(), select(), rename(), distinct(),
#  mutate(), transmute(), summarize(), sample_n(), sample_frac()

# R's tidyr methods on data frames clean up data
#  gather(), separate(), spread()

# Can also select on Tensor and Dictionary
# Inspiration is lang-Q's select statement
v.select("where > 10")
d.select("where key < 10 and value > 20")
t.select("first 10")
