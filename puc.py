# Python unified containers


class Storage:
    pass


class Tensor:  # has a Storage
    pass


class Vector(Tensor):
    pass


class Matrix(Tensor):
    pass


class Dictionary:
    pass


# a Table is simlar to a Pandas Dataframe
class Table:
    pass


class KeyedTable:
    pass
