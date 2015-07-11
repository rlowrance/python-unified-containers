# demonstrate api

from puc import Storage, Vector, Matrix, Tensor, Dictionary, Table, KeyedTable

# Storage is the actuall data
# The other types are views of a Storage
# A Storage can have zero or more views

s = Storage(n=10, kind="bool")  # 10 elements
s = Storage(n=100, kind="int64")
s = Storage(n=1000, kind="float64")
s = Storage(n=10000, kind="string")
s = Storage([0, 1, 1, 0], kind="bool")

# Vectors are 1D views of parts of or all of a Storage

v = Vector(storage=s)  # all elements, same len as underlying storage
v = Vector(storage=s, shape=[8])  # first 8 elements
v = Vector(storage=s, shape=[5], offsets=[0], strides=[2])  # every other

# indexing returns same shape as the indexer
x = v[3]       # x is a python scalar
x = v[[0, 3]]  # x is a Vector
x = v[Storage([0, 1, 0, 0, 1, 1, 0, 0, 0, 1], kind="bool")]  # masked selection

# Matrices are 2D views of parts of or all of a Storage
m = Matrix(storage=s, shape=[3, 4], offsets=[0, 0], strides=[1, 1])  # dense

# Vectors and Matrices are subclasses of Tensors
# methods on Tensors
t = Tensor()     # API to be defines
t.copy()         # copies view object
t.deepcopy()     # also copies the storage
t.is_contiguous()
t.deep_continguous_copy()  # ufuncs can be optimized for continuous storage

# Dictionary have multiple items
d = Dictionary()  # no storage
d["a"]            # one value
d[v]              # vector of values

# Tables are dictionary-like objects conceptualized as an ordered list of
# records. A Table is like a dataframe without observation names.
#
# Tables are stored column-wise.
c1 = Vector(["a", "b", "c"])
c2 = Vector([10, 20, 30])
tab = Table(c1, c2)  # 2 columns, each with same number of rows

# KeyedTable are dataframe-ike objects with distinct labels for the rows. It
# is conceptually a dictionary of dictionaries. The unique keys could be,
# for example, datetime stamps.
ktab = KeyedTable()  # syntax TBD

# operations on tables

t.groupby()  # most of the Pandas dataframe sql-like methods
t.select("where ... group by ... having ... ordered by ...")  # sql statement
