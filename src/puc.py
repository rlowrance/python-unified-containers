'Python Unified Containers wip for Version 0.1'

# import abc
import collections
import numpy as np
import pdb
import unittest


class PUC(object):
    pass


class V(PUC):
    def _repr_items(self):
        first = True
        s = ''
        for item in self._value:
            if first:
                s += '%s' % item
                first = False
            else:
                s += ', ' + '%s' % item
        return s
    pass


class Vint8(V):
    def __init__(self, other):
        if isinstance(other, int):
            if not self._in_range(other):
                raise ValueError(other)
            self._value = other
        elif isinstance(other, collections.Iterable):
            value = np.empty(len(other))
            index = -1
            for item in other:
                if not self._in_range(item):
                    raise ValueError(item)
                index += 1
                value[index] = item
            self._value = value
        elif isinstance(other, Vint8):
            self._value = np.copy(other._value)
        else:
            assert False, 'write me'

    def __repr__(self):
        return 'Vint8([' + super(Vint8, self)._repr_items() + '])'

    def _in_range(self, other):
        return -128 <= other <= 127


class TestVint8(unittest.TestCase):
    def test_construction(self):
        # successes
        v = Vint8(-128)
        v = Vint8((127, 20))
        v = Vint8(v)
        v = Vint8(np.array([10, 20], dtype=np.int8))
        # failures
        try:
            v = Vint8(-129)
            self.assertFalse()
        except:
            pass
        try:
            v = Vint8(128)
            self.assertFalse()
        except:
            pass


if __name__ == '__main__':
    if False:
        # avoid warnings from pyflakes by using imports
        pdb.set_trace()
    unittest.main()
