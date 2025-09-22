import unittest, io
from listxml import *

class _Stringable():
    """A class with a __str__() method"""
    def __init__(self, v):
        self.v = v
    def __str__(self):
        return format("|{}|".format(self.v))

class TestSearching(unittest.TestCase):
    def test_simple(self):
        content = ['div',
                   ['p', "hello"],
                   ['p', [], "hello ", ['em', "there"]],
                   ['h1', "heading"],
                   ['p', "and ", ['em', "more"], " still"],
                   # not matched with ['p','em']: the em is not a child of p
                   ['p', ['x', ['em', 'x-inner']]],
                   # the inner one is matched with ['p', 'em']
                   ['p', ['p', ['em', 'p-inner']]],
                   ['div',
                    # searching for 'p' should find only the outer element here,
                    # not the inner 'p' in addition
                    ['p', "p1", ['p', ['em', 'boo!']]],
                    ['div', ['p', "pdiv"]],
                    ['p', "p2 ", ['em', [['a1', 'v1']], "p2em"]]]]

        self.assertEqual(search_for_path('p', content),
                         [['hello'],
                          ["hello ", ['em', "there"]],
                          ["and ", ['em', "more"], " still"],
                          [['x', ['em', 'x-inner']]],
                          [['p', ['em', 'p-inner']]],
                          ["p1", ['p', ['em', 'boo!']]],
                          ["pdiv"],
                          ["p2 ", ['em', [['a1', 'v1']], "p2em"]]])
        self.assertEqual(search_for_path('p/em', content),
                         [['there'],
                          ['more'],
                          ['p-inner'],
                          ['boo!'],
                          ['p2em']])

        # and again, with with_element=True
        self.assertEqual(search_for_path('p',  content, with_element=True),
                         [['p', {}, "hello"],
                          ['p', {}, "hello ", ['em', "there"]],
                          ['p', {}, "and ", ['em', "more"], " still"],
                          ['p', {}, ['x', ['em', 'x-inner']]],
                          ['p', {}, ['p', ['em', 'p-inner']]],
                          ['p', {}, "p1", ['p', ['em', 'boo!']]],
                          ['p', {}, "pdiv"],
                          ['p', {}, "p2 ", ['em', [['a1', 'v1']], "p2em"]]])
        self.assertEqual(search_for_path('p/em', content, with_element=True),
                         [['em', {}, "there"],
                          ['em', {}, "more"],
                          ['em', {}, 'p-inner'],
                          ['em', {}, 'boo!'],
                          ['em', {'a1': 'v1'}, "p2em"]])

    # similar to above, but with non-strings (including 'stringable' things)
    # instead of strings
    def test_nonstrings(self):
        content = ['div',
                   ['p', b"hello"],
                   ['p', [], b"hello ", ['em', 1.1]],
                   ['h1', b"heading"],
                   ['p', b"and ", ['em', b"more"], b" still"],
                   ['div',
                    ['p', b"p1"],
                    ['div', ['p', b"pdiv"]],
                    ['p', b"p2 ", ['em', [['a1', 'v1']], _Stringable(99)]]]]

        # In order to turn the stringables into something testable,
        # we send this through a Collector
        res = [['li', *p] for p in search_for_path('p/em', content)]
        coll = Collector()
        list_to_collector(['div', *res], coll)
        self.assertEqual(b"".join(coll),
                         b'<div><li>1.1</li><li>more</li><li>|99|</li></div>')

    def test_attributes_list(self):
        content = ['div',
                   ['p', "p1"],
                   ['p', [], "p2"],
                   ['p', [['a1', 'v1']], "p3"],
                   ['p', [['x', 'nothing']],
                    ['p', [['a1', 'v2']], 'p4a'],
                    "p4b"],
                   ['p', [['x', 'nothing']],
                    ['p', [['a1', 'v2'], ['a2', 'v2a']],
                     ['p', 'p5a'], "p5b"]],
                   ['p', [['x', 'nothing']],
                    ['p', [['a1', 'v2']],
                     ['q', 'p6a'], "p6b"]],
                   ['other', [['a1', 'v3-@$é z']], "other-content"],
                   ['other', [['a1', '']], "other2"]]
        self.assertEqual(search_for_path('p/@a1', content),
                         ['v1', 'v2', 'v2', 'v2'])
        self.assertEqual(search_for_path('p[@a1="v2"]', content),
                         # returns the contents of the elements with this att
                         [['p4a'], [['p', 'p5a'], "p5b"], [['q', 'p6a'], "p6b"]])
        self.assertEqual(search_for_path('p[@a1="v2"]/p', content),
                         # returns the contents of the <p> inside <p a1="v2">
                         [['p5a']])
        self.assertEqual(search_for_path('other[@a1="v3-@$é z"]', content),
                         # no restrictions on attribute values
                         [['other-content']])
        # empty values work, too
        self.assertEqual(search_for_path('other[@a1=""]', content),
                         [['other2']])
        # single-quotes instead of double
        self.assertEqual(search_for_path("p[@a1='v1']", content),
                         [['p3']])
        # Search for the element with attribute @a1=v2, and return the @a2 value.
        self.assertEqual(search_for_path('p[@a1="v2"]/@a2', content),
                         ['v2a'])
        with self.assertRaises(ValueError):
            search_for_path('p[x]', content)

    # ...repeated with dict attributes
    def test_attributes_dict(self):
        content = ['div',
                   ['p', "p1"],
                   ['p', [], "p2"],
                   ['p', [['a1', 'v1']], "p3"],
                   ['p', [['x', 'nothing']], ['p', [['a1', 'v2']], 'p4a'], "p4b"],
                   ['p', [['x', 'nothing']], ['p', [['a1', 'v2']], ['p', 'p5a'], "p5b"]],
                   ['p', [['x', 'nothing']], ['p', [['a1', 'v2']], ['q', 'p6a'], "p6b"]],
                   ['other', [['a1', 'v3']]]]
        self.assertEqual(search_for_path('p/@a1', content),
                         ['v1', 'v2', 'v2', 'v2'])
        self.assertEqual(search_for_path('p[@a1="v2"]', content),
                         [['p4a'], [['p', 'p5a'], "p5b"], [['q', 'p6a'], "p6b"]])
        self.assertEqual(search_for_path('p[@a1="v2"]/p', content),
                         [['p5a']])

    def test_attributes_with_element(self):
        # another repeat of test_attributes_list, but with with_element=True
        content = ['div',
                   ['p', "p1"],
                   ['p', [], "p2"],
                   ['p', [['a1', 'v1']], "p3"],
                   ['p', [['x', 'nothing']], ['p', [['a1', 'v2']], 'p4a'], "p4b"],
                   ['p', [['x', 'nothing']], ['p', [['a1', 'v2']], ['p', 'p5a'], "p5b"]],
                   ['p', [['x', 'nothing']], ['p', [['a1', 'v2']], ['q', 'p6a'], "p6b"]],
                   ['other', [['a1', 'v3']]]]
        # element name and attributes do appear
        self.assertEqual(search_for_path('p[@a1="v2"]', content, with_element=True),
                         [['p', {'a1': 'v2'}, 'p4a'],
                          ['p', {'a1': 'v2'}, ['p', 'p5a'], "p5b"],
                          ['p', {'a1': 'v2'}, ['q', 'p6a'], "p6b"]])
        self.assertEqual(search_for_path('p[@a1="v2"]/p', content, with_element=True),
                         [['p', {}, 'p5a']])
        # no change when reporting attributes
        self.assertEqual(search_for_path('p/@a1', content, with_element=True),
                         ['v1', 'v2', 'v2', 'v2'])

    def test_nodecount(self):
        content = ['div',
                   ['p', 'p1', ['em', 'x1']],
                   ['p', 'p2', ['em', 'x2']],
                   ['p', 'p3', ['em', 'x3']]]
        self.assertEqual(search_for_path('p[2]', content),
                         [['p2', ['em', 'x2']]])
        self.assertEqual(search_for_path('p[2]', content, with_element=True),
                         [['p', {}, 'p2', ['em', 'x2']]])
        self.assertEqual(search_for_path('p[2]/em', content),
                         [['x2']])
        self.assertEqual(search_for_path('p[2]/em', content, with_element=True),
                         [['em', {}, 'x2']])
        self.assertEqual(search_for_path('p[99]', content),
                         [])

    def test_edges(self):
        # I can't decide what search_for_path('', x) should return:
        # one or other of the following.
        # See FIXME in listxml.py
        #self.assertEqual(search_for_path('', ['div', ['foo', "wibble"]]), [])
        self.assertEqual(search_for_path('', ['div', ['foo', "wibble"]]), ['div', ['foo', "wibble"]])

        self.assertEqual(search_for_path('p', []), [])
        self.assertEqual(search_for_path('p', ['div']), [])


        # the path should be a string!
        with self.assertRaises(ValueError):
            search_for_path(['p'], ['p'])

        # malformed paths
        with self.assertRaises(ValueError):
            # empty path element
            search_for_path('p/', ['p'])
        with self.assertRaises(ValueError):
            # no attribute name
            search_for_path('p/@', ['p'])
        with self.assertRaises(ValueError):
            # att=value tests should be in a [predicate]
            search_for_path('p/@a=b', ['p'])
        with self.assertRaises(ValueError):
            # attribute equality tests should be in "quotes"
            search_for_path('p/[@a=b]', ['p'])
