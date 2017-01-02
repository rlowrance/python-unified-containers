'''Python Unified Containers Version 0.1
Types provided
 Scalar
 ScalarX
 Vector
 VectorX (has a 1D numpy.array)
 Map (has a pandas.Series)
 Table
 TableKeyed
where X is in {Bool, Int64, Float64, DateTime, TimeDelta, String, Object}
'''

# import abc
import collections
import numpy as np
import pdb
import unittest


class PUCException(Exception):
    'base class for exceptions raised'
    # ref: https://julien.danjou.info/blog/2016/python-exceptions-guide
    def __init__(self, puc, msg=None):
        if msg is None:
            msg = 'Exception raised for PUC object %s' % puc
        super(PUCException, self).__init__(msg)
        self.puc = puc


class PUCTypeError(PUCException):
    def __init__(self, obj, expected_types):
        def make_msg(expected_types):
            if len(expected_types) == 1:
                return 'Expected type %s, found type %s' % (expected_types[0], type(obj))
            else:
                return 'Expected type to be in %s, found type %s' % (expected_types, type(obj))
        super(PUCTypeError, self).__init__(
            obj,
            msg=make_msg(expected_types),
            )
        self.expected_types = expected_types

class PUCIndexError(PUCException):
    def __init__(self, obj, msg=None):
        super(PUCIndexError, self).__init__(obj, msg=msg)


class PUC(object):
    pass


class Scalar(PUC):
    # TODO: add subtypes ScalarString, ScalarDateTime, ScalarTimeDelta, ScalarObject
    def __init__(self, value, name=None):
        # subclass checks types of value
        self.value = value
        self.name = name  # for example, a column name from a Table

    def __repr__(self):
        return '%s(value=%s%s)' % (
            self.__class__.__name__,
            self.value,
            '' if self.name is None else ', name=%s' % self.name,
            )

    def __add__(self, other):
        allowed_types = (type(self),)
        if isinstance(other, allowed_types):
            return type(self)(self.value + other.value)
        else:
            raise PUCTypeError(other, allowed_types)

    def __eq__(self, other):
        return type(self) == type(other) and self.value == other.value


class ScalarBool(Scalar):
    def __init__(self, value, name=None):
        allowed_types = (bool, np.bool_)
        if isinstance(value, allowed_types):
            super(ScalarBool, self).__init__(value, name=name)
        else:
            raise PUCTypeError(value, allowed_types)

    def __add__(self, other):
        if isinstance(other, ScalarBool):
            return ScalarInt64(self.value + other.value)
        else:
            raise PUCTypeError(other, type(self))


class ScalarInt64(Scalar):
    def __init__(self, value, name=None):
        allowed_types = (int,)
        if isinstance(value, allowed_types):
            super(ScalarInt64, self).__init__(value, name=name)
        else:
            raise PUCTypeError(value, allowed_types)

    def __add__(self, other):
        return super(ScalarInt64, self).__add__(other)


class ScalarFloat64(Scalar):
    def __init__(self, value, name=None):
        allowed_types = (float,)
        if isinstance(value, allowed_types):
            super(ScalarFloat64, self).__init__(value, name=name)
        else:
            raise PUCTypeError(value, allowed_types)

    def __add__(self, other):
        return super(ScalarFloat64, self).__add__(other)


class TestScalar(unittest.TestCase):
    def check(self, constructed, expected_value, expected_name, expected_type):
        self.assertEqual(constructed.value, expected_value)
        self.assertEqual(constructed.name, expected_name)
        self.assertTrue(isinstance(constructed, Scalar))
        self.assertTrue(isinstance(constructed, expected_type))

    def test_init_ScalarBool(self):

        good_values = (True, False)
        for value in good_values:
            x = ScalarBool(value)
            self.check(x, value, None, ScalarBool)

        bad_values = (0, 1, 123, 4.6, 'abc', ScalarBool(False), ScalarInt64(123))
        for value in bad_values:
            self.assertRaises(PUCTypeError, ScalarBool, value)

    def test_add_ScalarBool(self):
        tests = (
            (True, True, 2),
            (True, False, 1),
            (False, True, 1),
            (False, False, 0))
        for x_value, y_value, expected_value in tests:
            actual = ScalarBool(x_value) + ScalarBool(y_value)
            self.assertTrue(isinstance(actual, ScalarInt64))
            self.assertEqual(expected_value, actual.value)

    def test_init_ScalarInt64(self):
        good_values = (-1, 0, 1, 900000000, False, True)  # NOTE: a bool is an int
        for value in good_values:
            x = ScalarInt64(value)
            self.check(x, value, None, ScalarInt64)

        bad_values = (0.0, ScalarBool(True), ScalarInt64(123), 'abc')
        for value in bad_values:
            self.assertRaises(PUCTypeError, ScalarInt64, value)

    def test_add_ScalarInt64(self):
        tests = (
            (-1, 1, 0),
            (0, 123, 123),
            (2, 3, 5),
            )
        for x_value, y_value, expected_value in tests:
            actual = ScalarInt64(x_value) + ScalarInt64(y_value)
            self.assertTrue(isinstance(actual, ScalarInt64))
            self.assertEqual(expected_value, actual.value)

    def test_init_ScalarFloat64(self):
        good_values = (-1.0, 0.0, 123.0, 1e700)
        for value in good_values:
            x = ScalarFloat64(value)
            self.check(x, value, None, ScalarFloat64)

class Vector(PUC):
    'abstract class to hold common methods for VectorX'
    def __init__(self, *args, **kwds):
        assert len(kwds) <= 3  # only name and dtype are allowed
        assert 'dtype' in kwds, 'internal error: %s' % kwds
        assert 'allowed_types' in kwds, 'internal error: %s' % kwds
        allowed_types = kwds['allowed_types']
        for arg in args:
            if not isinstance(arg, allowed_types):
                raise PUCTypeError(arg, allowed_types)
        self.value = np.array(
            args,
            dtype=kwds['dtype'],
            )
        self.name = kwds.get('name', None)

    def __repr__(self,):
        return '%s(value=%s%s)' % (
            self.__class__.__name__,
            self.value,
            '' if self.name is None else ', name=%s' % self.name,
            )

    def __len__(self):
        return self.value.size

    def __getitem__(self, index):
        allowed_types = (ScalarInt64, VectorBool, VectorInt64)
        if not isinstance(index, allowed_types):
            raise PUCTypeError(index, allowed_types)
        if isinstance(index, ScalarInt64):
            # return a Scalar
            index_value = index.value
            if index_value < 0:
                raise PUCIndexError(index, msg='index value %s is negative' % index_value)
            if index_value >= len(self):
                raise PUCIndexError(index, msg='index value %s  not less than length %s' % (index_value, len(self)))
            result_value = self.value[index_value]
            if isinstance(self, VectorBool):
                return ScalarBool(result_value)
            if isinstance(self, VectorInt64):
                return ScalarInt64(result_value)
            assert False, 'TODO: add other VectorX types'
        if isinstance(index, VectorBool):
            pdb.set_trace()
            assert False, 'write me'
        if isinstance(index, VectorInt64):
            pdb.set_trace()
            assert False, 'write me'

class VectorBool(Vector):
    def __init__(self, *args, **kwds):
        kwds.update(dtype=bool)
        kwds.update(allowed_types=(bool,))
        super(VectorBool, self).__init__(*args, **kwds)

class VectorInt64(Vector):
    def __init__(self, *args, **kwds):
        kwds.update(dtype=int)
        kwds.update(allowed_types=(int,))
        super(VectorInt64, self).__init__(*args, **kwds)

class TestVector(unittest.TestCase):
    def test_init_Vector(self):
        'check that construction cannot be done from a list'
        x = VectorInt64()
        self.assertRaises(PUCTypeError, VectorInt64, [])
        x = VectorBool(True)
        x = VectorBool(True, False)
        self.assertRaises(PUCTypeError, VectorBool, (True, False))

    def test_init_VectorBool(self):
        tests = (
            ((True, False), 2),
            ((True,), 1),
            ([], 0),
            )
        for args, expected_len in tests:
            x = VectorBool(*args)
            self.assertEqual(expected_len, len(x))
            for i, arg in enumerate(args):
                # check value of each arg
                self.assertEqual(ScalarBool(arg), x[ScalarInt64(i)])
    
    def test_init_VectorInt64(self):
        tests = (
            ((7, 11), 2),
            ((7,), 1),
            ([], 0),
            )
        for args, expected_len in tests:
            x = VectorInt64(*args)
            self.assertEqual(expected_len, len(x))
            for i, arg in enumerate(args):
                # check value of each arg
                self.assertEqual(ScalarInt64(arg), x[ScalarInt64(i)])

    def test_len(self):
        tests = (
            ([], 0),
            ([10], 1),
            ([10, 20], 2),
        )
        for args, expected_len in tests:
            x = VectorInt64(*args)
            self.assertEqual(expected_len, len(x))
    
    def test_getitem(self):
        def getitem(x, index):
            return x[index]
        x = VectorInt64(7, 11)
        self.assertEqual(ScalarInt64(7), x[ScalarInt64(0)])
        y = VectorInt64()
    
    def test_setitem(self):
        pass


if __name__ == '__main__':
    if False:
        # avoid warnings from pyflakes by using imports
        pdb.set_trace()
    unittest.main()
