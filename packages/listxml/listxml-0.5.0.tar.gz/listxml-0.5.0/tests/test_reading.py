import unittest
import io, os, tempfile
from listxml import *

class TestBasics(unittest.TestCase):
    def test_basic_parse(self):
        s = io.StringIO('<div id="content"><p>hello there</p><p>foo<em>bar</em></p><hr /><br att="clear" /><p>three<a href="XXX" name="foo">bar</a></p></div>')
        self.assertEqual(construct(s),
                         ['div', [['id', 'content']],
                          ['p', [], 'hello there'],
                          ['p', [], 'foo', ['em', [], 'bar']],# empty attlist and empty element
                          ['hr', []],                         # empty element, no attlist
                          ['br', [['att', 'clear']]],         # empty element, single attribute
                          ['p', [],
                           'three',
                           ['a', [['href', 'XXX'], ['name', 'foo']], # multiple attributes
                            'bar']]])

    def test_basic_parse_dict(self):
        s = io.StringIO('<div id="content"><p>hello there</p><p>foo<em>bar</em></p><hr /><br att="clear" /><p>three<a href="XXX" name="foo">bar</a></p></div>')
        self.assertEqual(construct(s, attributes_as_dict=True),
                         ['div', {'id': 'content'},
                          ['p', {}, 'hello there'],
                          ['p', {}, 'foo', ['em', {}, 'bar']],# empty attlist and empty element
                          ['hr', {}],                         # empty element, no attlist
                          ['br', {'att': 'clear'}],           # empty element, single attribute
                          ['p', {},
                           'three',
                           ['a', {'href': 'XXX', 'name': 'foo'}, # multiple attributes
                            'bar']]])

    def test_basic_parse_emptylist(self):
        s = io.StringIO('<div id="content"><p>hello there</p><p>foo<em>bar</em></p><hr /><br att="clear" /><p>three<a href="XXX" name="foo">bar</a></p></div>')
        self.assertEqual(construct(s, omit_empty_attlist=True),
                         ['div', [['id', 'content']],
                          ['p', 'hello there'],
                          ['p', 'foo', ['em', 'bar']],    # empty attlist and empty element
                          ['hr'],                         # empty element, no attlist
                          ['br', [['att', 'clear']]],     # empty element, single attribute
                          ['p',
                           'three',
                           ['a', [['href', 'XXX'], ['name', 'foo']], # multiple attributes
                            'bar']]])


    def test_basic_parse_dict_emptylist(self):
        s = io.StringIO('<div id="content"><p>hello there</p><p>foo<em>bar</em></p><hr /><br att="clear" /><p>three<a href="XXX" name="foo">bar</a></p></div>')
        self.assertEqual(construct(s, attributes_as_dict=True, omit_empty_attlist=True),
                         ['div', {'id': 'content'},
                          ['p', 'hello there'],
                          ['p', 'foo', ['em', 'bar']],    # empty attlist and empty element
                          ['hr'],                         # empty element, no attlist
                          ['br', {'att': 'clear'}],       # empty element, single attribute
                          ['p',
                           'three',
                           ['a', {'href': 'XXX', 'name': 'foo'}, # multiple attributes
                            'bar']]])

    def test_parse_from_file(self):
        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                temp_fn = f.name
                print("<div id='content'><p>Hello</p></div>", file=f)
            self.assertEqual(construct(temp_fn, omit_empty_attlist=True),
                             ['div', [['id', 'content']], ['p', "Hello"]])
        finally:
            os.remove(temp_fn)

    # The current version is not namespace-aware
    # def test_basic_ns(self):
    #     s = io.StringIO('<div><p xmlns:n="urn:1" a1="v1" n:a2="v2"><n:el/></p><p xmlns="urn:2"><el a1="v1">bar</el></p></div>')
    #     self.assertEqual(construct(s, with_namespaces=True),
    #                      ['div', [],
    #                       ['p', [['a1', 'v1'], ['{urn:1}a2', 'v2']],
    #                        ['{urn:1}el', []]],
    #                       ['{urn:2}p', [],
    #                        ['{urn:2}el', [['a1', 'v1']], 'bar']]])

    # def test_basic_ns_ignored(self):
    #     # XMLNS attributes are not given any significance.
    #     s = io.StringIO('<div><p xmlns:n="urn:1" a1="v1" n:a2="v2"><n:el/></p><p xmlns="urn:2"><el a1="v1">bar</el></p></div>')
    #     self.assertEqual(construct(s),
    #                      ['div', [],
    #                       ['p', [['xmlns:n', 'urn:1'], ['a1', 'v1'], ['n:a2', 'v2']],
    #                        ['n:el', []]],
    #                       ['p', [['xmlns', 'urn:2']],
    #                        ['el', [['a1', 'v1']], 'bar']]])
