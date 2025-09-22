import unittest
import io, os, os.path
from listxml import *

class TestBasics(unittest.TestCase):
    def test_conversion(self):
        content = ['div', [['id', 'content']],
                   ['p', 'hello ', 'there'],
                   ['p', [], 'foo', ['em', 'bar']],# empty attlist and inner element
                   ['hr'],                         # empty element, no attlist
                   ['br', [['att', 'clear']]],     # empty element, single attribute
                   ['p',
                    'three',
                    ['a', [['href', 'XXX'], ['name', 'foo']], # multiple attributes
                     'bar']]]                                 # inner element content
        coll = Collector()
        c2 = list_to_collector(content, coll)
        self.assertEqual(c2, coll) # list_to_collector returns the collector argument
        self.assertEqual(c2.get_length(), 132)
        self.assertEqual(b"".join(c2),
                         b'<div id="content"><p>hello there</p><p>foo<em>bar</em></p><hr /><br att="clear" /><p>three<a href="XXX" name="foo">bar</a></p></div>')

    def test_conversion_dict(self):
        content = ['div', {'id':'content'},
                   ['p', 'hello ', 'there'],
                   ['p', {}, 'foo', ['em', 'bar']],# empty attlist and inner element
                   ['hr'],                         # empty element, no attlist
                   ['br', {'att': 'clear'}],       # empty element, single attribute
                   ['p',
                    'three',
                    ['a', {'href': 'XXX', 'name': 'foo'}, # multiple attributes
                     'bar']]]                             # inner element content
        coll = Collector()
        list_to_collector(content, coll)
        self.assertEqual(coll.get_length(), 132)
        self.assertEqual(b"".join(coll),
                         b'<div id="content"><p>hello there</p><p>foo<em>bar</em></p><hr /><br att="clear" /><p>three<a href="XXX" name="foo">bar</a></p></div>')

    # It's good that the following works, but this behaviour isn't quite promised,
    # so it's not worth checking.
    #
    # def test_collect_to_list(self):
    #     content = ['div', [['id', 'content']],
    #                ['p', 'hello ', 'there']]
    #     colllist = []
    #     list_to_collector(content, colllist)
    #     self.assertEqual(''.join([s if isinstance(s,str) else s.decode('utf-8') for s in colllist]),
    #                      '<div id="content"><p>hello there</p></div>')

    def test_escaping(self):
        content = ['div', [['att', '<>&\"']], '<>&\"']
        coll = Collector()
        list_to_collector(content, coll)
        self.assertEqual(b"".join(coll),
                         b"<div att=\"&lt;&gt;&amp;&#34;\">&lt;&gt;&amp;&#34;</div>")

    def test_bytes(self):
        content = ['div', b'unescaped &amp; <hairy']
        coll = Collector()
        list_to_collector(content, coll)
        self.assertEqual(b''.join(coll),
                         b'<div>unescaped &amp; <hairy</div>')

    def test_nonstr(self):
        # non-strings (testing only integers and floats) in content and attribute values
        class Barfly():
            def __init__(self, v):
                self.v = v
            def __str__(self):
                return format("|{}|".format(self.v))
        content = ['div', [['a1', 1], ['a2', 1.1]],
                   "integer ", 1, " float ", 1.1,
                   ' struct ', Barfly(99),
                   ['e', {'b1': 1, 'b2': 1.1}]]
        coll = Collector()
        list_to_collector(content, coll)
        self.assertEqual(b"".join(coll),
                         b'<div a1="1" a2="1.1">integer 1 float 1.1 struct |99|<e b1="1" b2="1.1" /></div>')

    def test_stream1(self):
        # The output ends up as a string because we're using StringIO to collect it.
        # We have to do this, because this prints to a
        # text-file-like stream, such as sys.stdout.
        content = ['div', [['id', 'content']], "element content"]
        s = io.StringIO()
        coll = PrintCollector(s)
        c2 = list_to_collector(content, coll)
        self.assertEqual(c2, coll)
        self.assertEqual(coll.get_length(), 39)
        self.assertEqual(s.getvalue(),
                        '<div id="content">element content</div>')

    def test_stream2(self):
        # as above, but using the set_stream call
        content = ['div', [['id', 'content']], "element content"]
        s = io.StringIO()
        coll = PrintCollector()
        coll.set_stream(s)
        list_to_collector(content, coll)
        self.assertEqual(coll.get_length(), 39)
        self.assertEqual(s.getvalue(),
                         '<div id="content">element content</div>')

    def test_stream3(self):
        # as above, but using list_to_stream
        content = ['div', [['id', 'content']], "element content"]
        s = io.StringIO()
        nwritten = list_to_stream(content, s)
        self.assertEqual(nwritten, 39)
        self.assertEqual(s.getvalue(),
                         '<div id="content">element content</div>')

    # We can append non-XML strings in an unsurprising way.
    def test_declarations(self):
        content = ['div', [['id', 'content']], "element content"]
        coll = Collector()
        coll.append('<?xml version="1.0"?>\n')
        coll.append('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n')
        list_to_collector(content, coll)
        self.assertEqual(b"".join(coll),
                         b'<?xml version="1.0"?>\n<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n<div id="content">element content</div>')

    def test_declarations_stream(self):
        content = ['div', [['id', 'content']], "element content"]
        s = io.StringIO()
        coll = PrintCollector()
        coll.set_stream(s)
        coll.append('<?xml version="1.0"?>\n')
        coll.append('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n')
        list_to_collector(content, coll)
        coll.close()
        # the result here is a string, not bytes, and s is not closed
        self.assertEqual(s.getvalue(),
                         '<?xml version="1.0"?>\n<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n<div id="content">element content</div>')

    def test_badstring1(self):
        content = ['div', [b'sub']]
        coll = Collector()
        with self.assertRaises(TypeError):
            list_to_collector(content, coll)
            print("badstring erroneously produced: {}".format(b''.join(coll)))

    def test_badstring2(self):
        content = ['div', [[b'a1', 'v']]]
        coll = Collector()
        with self.assertRaises(TypeError):
            list_to_collector(content, coll)
            print("badstring erroneously produced: {}".format(b''.join(coll)))

    def test_badstring3(self):
        content = ['div', {b'a1': 'v'}]
        coll = Collector()
        with self.assertRaises(TypeError):
            list_to_collector(content, coll)
            print("badstring erroneously produced: {}".format(b''.join(coll)))

    def test_context_collector1(self):
        content = ['div', [['id', 'content']], "element content"]
        outputfile = 'tmp-printcollector.xml'
        with PrintCollector(file=outputfile) as c:
            list_to_collector(content, c)
        self.assertTrue(os.path.exists(outputfile))
        with open(outputfile, 'r') as f:
            filecontent = f.read()
        self.assertEqual(filecontent, '<div id="content">element content</div>')
        os.remove(outputfile)

    # Confirm that close() works, and can be called multiple times.
    def test_context_collector2(self):
        content = ['div', [['id', 'content']], "element content"]
        outputfile = 'tmp-closing.xml'
        coll = PrintCollector(file=outputfile)
        list_to_collector(content, coll)
        coll.close()
        coll.close() # nilpotent
        self.assertTrue(os.path.exists(outputfile))
        with open(outputfile, 'r') as f:
            filecontent = f.read()
        self.assertEqual(filecontent, '<div id="content">element content</div>')
        os.remove(outputfile)

    def test_context_collector3(self):
        with self.assertRaises(ValueError):
            with PrintCollector(file='tmp-notwritten.xml', stream=sys.stdout):
                pass

    def test_context_collector_stringio(self):
        content = ['div', [['id', 'content']], "element content"]
        s = io.StringIO()
        with PrintCollector(s) as coll:
            list_to_collector(content, coll)
        self.assertEqual(s.getvalue(), '<div id="content">element content</div>')

    # Don't test the following either way.
    # The input is an error, but it produces XML-valid output.
    # I can't decide whether I should catch this (for the benefit of
    # the user, who probably didn't plan that) or not (for the sake of
    # consistency).
    #
    # def test_badattribute(self):
    #     content = ['div', [['a1', ['v1', 'v2']]]]
    #     coll = Collector()
    #     with self.assertRaises(TypeError):
    #         list_to_collector(content, coll)
    #         print("badattribute erroneously produced: {}".format(b''.join(coll)))

    # Test the specific behaviour of the collector append() method.
    # The list_to_collector() function will call the append method with only
    # string or bytes, but we might as well test that it handles other things.
    def test_collect_any(self):
        coll = Collector()
        coll.append('s').append(b'b').append(1).append(2.1)
        self.assertEqual(coll.get_length(), 6)
        self.assertEqual(b''.join(coll), b'sb12.1')

    def test_printcollect_any(self):
        f = io.StringIO()
        coll = PrintCollector(f)
        coll.append('s').append(b'b').append(1).append(2.1)
        self.assertEqual(coll.get_length(), 6)
        self.assertEqual(f.getvalue(), 'sb12.1')
        # PrintCollector returns a dummy iterator
        self.assertEqual(b''.join(coll), b'')
