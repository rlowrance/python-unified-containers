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
                return 'Expected type %s, found type %s value %s' % (expected_types[0], type(obj), obj)
            else:
                return 'Expected type to be in %s, found type %s value %s' % (
                    expected_types, type(obj), obj)
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
    # types from which each ScalarX type may be constructed
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
        #print type(self), value, name, allowed_types
        if isinstance(value, allowed_types):
            self.value = value
            self.name = name
        else:
            raise PUCTypeError(value, allowed_types)

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
                # special case: + for ScalarBools returns an ScalarInt64
                return ScalarInt64(self.value + other.value)
            else:
                if isinstance(self, (ScalarDatetime, ScalarObject)):
                    raise PUCException(
                        self,
                        'unable to add values of type %s value %s' % (type(self), self),
                    )
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
class ScalarDatetime(Scalar):
    def __init__(self, value, name=None):
        super(ScalarDatetime, self).__init__(value, name=name, allowed_types=PUC.types_datetime)
class ScalarTimedelta(Scalar):
    def __init__(self, value, name=None):
        super(ScalarTimedelta, self).__init__(value, name=name, allowed_types=PUC.types_timedelta)
class ScalarString(Scalar):
    def __init__(self, value, name=None):
        super(ScalarString, self).__init__(value, name=name, allowed_types=PUC.types_string)
class ScalarObject(Scalar):
    def __init__(self, value, name=None):
        super(ScalarObject, self).__init__(value, name=name, allowed_types=PUC.types_object)

class TestScalar(unittest.TestCase):
    def check(self, constructed, expected_value, expected_name, expected_type):
        #print 'TestScalar.check', self
        self.assertEqual(constructed.value, expected_value)
        self.assertEqual(constructed.name, expected_name)
        self.assertTrue(isinstance(constructed, Scalar))
        self.assertTrue(isinstance(constructed, expected_type))

    def test_init_value(self):
        'test self.value attribute for all ScalarX types'
        print 'test_init_value'
        def f():
            pass
        dt = datetime.datetime(2017, 1, 1, 12, 42, 50, 750)
        td = datetime.timedelta(275, 10)
        tests = (  # constructor, good_value, bad_values
            (ScalarBool, (False, True), (0, 1, dt, td, 'abc', f)),
            (ScalarInt64, (-1, 0, 1, False, True), (23.0, dt, 'abc', f)),
            (ScalarFloat64, (-1.0, 0.0, 1.0), (False, 0, dt, 'abc', f)),
            (ScalarDatetime, (dt,),(False, 0, 1.0, 'abc',f)),
            (ScalarTimedelta, (td,), (False, 1, 1.0, dt, 'abc', f)),
            (ScalarString, ('abc', ''), (False, 0, 0.0, dt, td, f)),
            (ScalarObject, (f, (1, 'abc'), False, 0, 0.0, dt, td, 'abc'), ()),
            )
        for constructor, good, bad in tests:
            for ex in good:
                s = constructor(ex)
                self.assertTrue(isinstance(s, Scalar))
                self.assertTrue(isinstance(s, constructor))
                self.assertEqual(ex, s.value)
                self.assertTrue(s.name is None)
            for ex in bad:
                self.assertRaises(
                    PUCException,  # may raise PUCTypeError or PUCConstructionError
                    constructor,
                    ex,
                )

    def test_init_name(self):
        tests = ('abc', 123, None)
        for test in tests:
            s = ScalarInt64(0, name=test)
            self.assertTrue(isinstance(s, Scalar))
            self.assertEqual(test, s.name)

    def test_add(self):
        def dt(x):
            return datetime.datetime(x, 1, 1)
        def td(x):
            return datetime.timedelta(x)
        tests = (
            (ScalarBool, (True, False, 1), None),
            (ScalarInt64, (-1, 1, 0), None),
            (ScalarFloat64, (7.0, 11.0, 18.0), None),
            (ScalarDatetime, None, None),  # but - will yield timedelta
            (ScalarTimedelta, (td(1), td(2), td(3)), None),  # + is allowed
            (ScalarString, ('ab', 'cd', 'abcd'), None),
            (ScalarObject, None, ('a', 1)),
        )
        for constructor, good, bad in tests:
            if good is not None:
                a, b, c = good
                expected = ScalarInt64(c) if constructor == ScalarBool else constructor(c)
                # print a, b, expected, constructor(a) + constructor(b)
                self.assertEqual(expected, constructor(a) + constructor(b))
            if bad is not None:
                def add(a, b):
                    return constructor(a) + constructor(b)
                a, b = bad
                # print constructor, a, b
                self.assertRaises(PUCException, add, a, b)







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