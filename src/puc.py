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
import datetime
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
class PUCConstructionError(PUCException):
    def __init__(self, obj, msg=None):
        super (PUCConstructionError, self).__init__(obj, msg=msg)


class PUC(object):
    types_bool = (bool, np.bool_)
    types_int = (int, np.int32, np.int64)
    types_float = (float, np.float_)
    types_datetime = (datetime.datetime,)
    types_timedelta = (datetime.timedelta,)
    types_string = (str,)
    types_object = (object,)

class Scalar(PUC):
    def __init__(self, value, name=None, allowed_types=None):
        #print 'Scalar.__init__', value, type(value), name, allowed_types
        if type(value) not in allowed_types:
            #print 'Scalar.__init__', 'will raise'
            raise PUCTypeError(value, allowed_types)
        self.value = value
        if name is None or isinstance(name, str):
            self.name = name
        else:
            raise PUCConstructionError(
                name,
                msg='name must be None or a str, was %s' % name,
            )

    def __repr__(self):
        return '%s(value=%s%s)' % (
            self.__class__.__name__,
            self.value,
            '' if self.name is None else ', name=%s' % self.name,
            )

    def __add__(self, other):
        # maybe: allow Scalar + (bool|int|float)
        allowed_types = (type(self),)
        if isinstance(other, allowed_types):
            if isinstance(self, ScalarBool):
                return ScalarInt64(self.value + other.value)
            else:
                return type(self)(self.value + other.value)
        else:
            raise PUCTypeError(other, allowed_types)

    def __eq__(self, other):
        return type(self) == type(other) and self.value == other.value


class ScalarBool(Scalar):
    def __init__(self, value, name=None):
        super(ScalarBool, self).__init__(value, name=name, allowed_types=PUC.types_bool)

class ScalarInt64(Scalar):
    def __init__(self, value, name=None):
        super(ScalarInt64, self).__init__(value, name=name, allowed_types=PUC.types_int)

class ScalarFloat64(Scalar):
    def __init__(self, value, name=None):
        super(ScalarFloat64, self).__init__(value, name=name, allowed_types=PUC.types_float)

class ScalarDateTime(Scalar):
    pass
class ScalarTimeDelta(Scalar):
    pass
class ScalarString(Scalar):
    pass
class ScalarObject(Scalar):
    pass

class TestScalar(unittest.TestCase):
    def check(self, constructed, expected_value, expected_name, expected_type):
        #print 'TestScalar.check', self
        self.assertEqual(constructed.value, expected_value)
        self.assertEqual(constructed.name, expected_name)
        self.assertTrue(isinstance(constructed, Scalar))
        self.assertTrue(isinstance(constructed, expected_type))

    def test_init_ScalarFloat64(self):
        good_tests = (-1.0, 0.0, 7.0)
        for arg in good_tests:
            x = ScalarFloat64(arg)
            self.assertEqual(ScalarFloat64, type(x))
        self.assertRaises(PUCConstructionError, ScalarFloat64, 7.0, 10.0)

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
        good_values = (-1, 0, 1, 900000000) 
        for value in good_values:
            x = ScalarInt64(value)
            self.check(x, value, None, ScalarInt64)

        bad_values = (0.0, False, True, ScalarBool(True), ScalarInt64(123), 'abc')
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


    def _check_index(self, index):
        'raise if index is not valid; otherwise return None'
        # treat an Iterable[X] is if it were a VectorX
        # maybe return index values as a list[int], because I'm going to have to examine all the indices
        allowed_index_types = (ScalarInt64, VectorBool, VectorInt64, int, collections.Iterable)
        if not isinstance(index, allowed_index_types):
            raise PUCTypeError(index, allowed_index_types)
        # if index is a list, it must be of all bools, ints, or floats
        if isinstance(index, list):
            item_type = None
            for item in index:
                if item_type is None:
                    item_type = type(item)
                    if item_type not in (bool, float, int):
                        msg = 'each element of a list index must be a bool, int, or float; found %s' % item_type
                        raise PUCIndexError(index, msg=msg)
                else:
                    if type(item) != item_type:
                        msg = 'found index element of type %s, not expected type %s' % (
                            type(item),
                            item_type,
                        )
                        raise PUCIndexError(index, msg=msg)
        if isinstance(index, (ScalarInt64, int)):
            index_value = index.value if isinstance(index, PUC) else index
            if index_value < 0:
                raise PUCIndexError(index, msg='index value %s is negative' % index_value)
            if index_value >= len(self):
                raise PUCIndexError(index, msg='index value %s  not less than length %s' % (index_value, len(self)))
        elif isinstance(index, VectorBool) or item_type == bool:
            assert False, 'write me'
        elif isinstance(index, VectorInt64) or item_type == int:
            assert False, 'write me'
        else:
            assert False, 'internal error'

   
    def _check_value(self, index, value):
        'raise PUCIndexError if incompatible for self[index] = value; otherwise return None'
        if (
            (isinstance(self, VectorBool) and isinstance(value, (ScalarBool, bool))) or
            (isinstance(self, VectorInt64) and isinstance(value, (ScalarInt64, int))) or
            (isinstance(self, VectorFloat64) and isinstance(value, (ScalarFloat64, float))) or
            (isinstance(self, VectorDateTime) and isinstance(value, (ScalarDateTime, datetime.datetime))) or
            (isinstance(self, VectorTimeDelta) and isinstance(value, (ScalarTimeDelta, datetime.timedelta))) or
            (isinstance(self, VectorString) and isinstance(value, (ScalarString, str))) or
            (isinstance(self, VectorObject) and isinstance(value, (ScalarObject, object)))
        ):
            return None
        else:
            msg = 'value of type %s is not compatible with a Vector of type %s' % (
                    type(value),
                    type(self),
                )
            raise PUCIndexError(msg)

    def __getitem__(self, index):
        'return new PUC object of the same shape and kind as the index'
        self._check_index(index)
        if isinstance(index, (ScalarInt64, int)):
            # return a Scalar
            result_value = self.value[index.value if isinstance(index, ScalarInt64) else index]
            if isinstance(self, VectorBool):
                return ScalarBool(result_value)
            if isinstance(self, VectorInt64):
                return ScalarInt64(result_value)
            if isinstance(self, VectorFloat64):
                return ScalarFloat64(result_value)
            if isinstance(self, VectorDateTime):
                return ScalarDateTime(result_value)
            if isinstance(self, VectorTimeDelta):
                return ScalarTimeDelta(result_value)
            if isinstance(self, VectorString):
                return ScalarString(result_value)
            if isinstance(self, VectorObject):
                return ScalarObject(result_value)
            assert False, 'internal error'
        if isinstance(index, VectorBool):
            # return Vector with selected elements
            pdb.set_trace()
            assert False, 'write me'
        if isinstance(index, VectorInt64):
            # return Vector with selected elements
            pdb.set_trace()
            assert False, 'write me'
        assert False, 'internal error'

    def __setitem__(self, index, value):
        'mutate self'
        self._check_index(index)
        self._check_value(index, value) 
        if isinstance(index, ScalarInt64):
            self.value[index.value] = value.value
        elif isinstance(index, int):
            self.value[index] = value
        elif isinstance(index, VectorBool):
            # new_value must be a Vector
            # take repeatedly from it
            assert False, 'write me'
        elif isinstance(index, VectorInt64):
            # new_value must be a Vector
            # take repeatedly from it
            assert False, 'write me'
        else:
            assert False, 'internal error'


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

class VectorFloat64(Vector):
    pass
class VectorDateTime(Vector):
    pass
class VectorTimeDelta(Vector):
    pass
class VectorString(Vector):
    pass
class VectorObject():
    pass

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
    
    def test_getitem_setitem_ScalarInt64(self):
        # test when the index is a ScalarInt64 or int
        # its OK to test just one subclaass of Vector, because the implementation in in class Vector
        x = VectorInt64(7, 11)  # ? should we require ScalarInt64's as arguments
        index0 = ScalarInt64(0)
        index1 = ScalarInt64(1)
        s7 = ScalarInt64(7)
        s11 = ScalarInt64(11)
        s23 = ScalarInt64(23)
        # test __getitem__
        self.assertEqual(s7, x[index0])
        self.assertEqual(s7, x[0])
        # test __setitem__
        x[index1] = s23
        self.assertEqual(s7, x[0])
        self.assertEqual(s23, x[1])
        x[1] = 23
        self.assertEqual(23, x[1].value)
    
    def test_getitem_setitem_zero_length_Vector(self):
        x = VectorInt64()
        def getitem(index):
            return x[index]
        self.assertRaises(PUCIndexError, getitem, 0)

if __name__ == '__main__':
    if False:
        # avoid warnings from pyflakes by using imports
        pdb.set_trace()
    unittest.main()