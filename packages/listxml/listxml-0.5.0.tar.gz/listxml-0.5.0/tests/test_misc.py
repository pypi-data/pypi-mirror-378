import unittest, io
from listxml import *

class _Stringable():
    """A class with a __str__() method"""
    def __init__(self, v):
        self.v = v
    def __str__(self):
        return format("|{}|".format(self.v))

class TestMisc(unittest.TestCase):
    def test_valid_str(self):
        '''Confirm that the __str__ method is correctly implemented'''
        s = io.StringIO()
        with PrintCollector(stream=s) as coll:
            list_to_collector(['p', {}, _Stringable(99)], coll)
            self.assertEqual(s.getvalue(), "<p>|99|</p>")

    def test_good_lx(self):
        self.assertTrue(is_listxml_p(['div']))
        self.assertTrue(is_listxml_p(['div',
                                      ['p', "p1"],
                                      ['p', [], b"p2"],
                                      ['p', {}, _Stringable(99)],
                                      ['p', {'a1', 'v1'}, ['p', "p3", ['em', "foo"]]],
                                      ['p', [['x', 1], ['y', _Stringable(1)]], "p4"]]))
        self.assertFalse(is_listxml_p([]))
        self.assertFalse(is_listxml_p({}))
        self.assertFalse(is_listxml_p('str'))
        self.assertFalse(is_listxml_p(['div', [], {}]))
        self.assertFalse(is_listxml_p(['div', {}, []]))
        self.assertFalse(is_listxml_p(['div', {}, [['k', 'v']]]))
        self.assertFalse(is_listxml_p(['div', [['k', []]]]))
        self.assertFalse(is_listxml_p(['div', {'k': []}]))
