Listxml
=======

Listxml is an _unpythonic_ XML wrangler!

Version: 0.5.0, released 2025 September 21.

Python provides the DOM and ElementTree interfaces for creating an XML
tree, and serialising it for output.
These work well, but can hardly be called lightweight; it can be
wearisome to programmatically assemble an XML document, and because the
document is assembled from a multitude of method calls, it's easy to
lose the wood amongst the trees.

The `listxml` package provides a different way of creating a data
structure which can be serialised into XML.  That structure might represent an
(X)HTML file, or something like an RSS feed.  The structure's easy to generate
programmatically (list comprehensions are your friend!),
and, because it's compact, you can see more of it on
the screen at once.

Rather than be clever about fancy syntax, Listxml aims for minimalism
and a homogeneous representation (pssst: if you think this looks a bit
lispy, you would not be mistaken).

There is also a simple function for searching a listxml list in an
XML-like way.  It implements a (very) small fragment of the XPath
syntax (it's much less ambitious, but we aim not to be gratuitously
incompatible with XPath).

This is still a beta release: the interface and functionality is still
not 100% fixed, and comments would be welcome.

For example:

    import listxml

    # l is a list representing an element
    l = ['div',                      # a <div> element
         ['p',                       # the element name is a string
          [['class', 'highlight']],  # attributes are a list of two-element lists
          "Hello, world", 99],       # element content, string or str()-friendly
         ["p", "& another <para>"]]  # no attributes, and escaped content

    coll = listxml.Collector()
    listxml.list_to_collector(l, coll)

    # print the resulting byte content
    for content in coll:
        print(content.decode('utf-8'), end='')

    # or use it as an iterator
    print(b''.join(coll))

In each case, the printed result is

    <div><p class="highlight">Hello, world99</p><p>&amp; another &lt;para&gt;</p></div>

Alternatively, use `PrintCollector` as a collector, to send output to stdout
or another stream (`list_to_stream` does that).

    coll = listxml.PrintCollector()
    listxml.list_to_collector(l, coll)

A ‘collector’, here, is anything which matches the `Collector` interface described below.

The intention is that, as long as you don't use the `b'bytestring'`
escape mechanism mentioned below, it should be impossible to serialise
an invalid XML file using this package.

For symmetry, the package also includes a way of turning XML into the
sort of list it expects (wrapping the expat parser built in to Python):

    # The named file contains "<xml>...</xml>"...
    filename = "foo.xml"
    l = listxml.construct(filename)

    coll = listxml.Collector()
    listxml.list_to_collector(l, coll)
    b''.join(coll)

...should produce output which is equivalent, in XML terms, to the
input file.


A fuller example
----------------

This example assembles an HTML page body, and drops it into a ‘template’.

    import listxml

    def wrap_body(title, body):
        """Create a standard XHTML document (ie, this is a form of templating)"""
        return ['html', [['xmlns', 'http://www.w3.org/1999/xhtml']],
                ['head',
                 ['title', title],
                 ['link', [['rel', 'stylesheet'],
                           ['type', 'text/css'],
                           ['href', 'http://example.org/mystyle.css']]]],
                ['body',
                 ['h1', title],
                 *body]]

    # assemble a list of li elements
    items = ["First item", "Second item"]
    ul = [['li', i] for i in items]

    # build up a list of body content elements
    b = [['p', 'One paragraph'],
         ['p', "Another one, with ",
          ['a', [['href', 'http://example.org/home.html']],
           "a link"]],
         ['ul', *ul]] # append the ul list to make list contents

    # use the PrintCollector to send this to stdout
    coll = listxml.PrintCollector()
    listxml.list_to_collector(wrap_body("My XHTML file", b), coll)



Classes and functions
---------------------

The package defines the following classes and functions.

### Function `list_to_collector(lx, coll)`

  * lx: a list representation of an XML document
  * coll: a Collector – see below

Convert the input list to XML and send it to the collector.
See below for the structure of the input list.
Returns the input collector.

In fact, the 'coll' object can be any object with an append() method.

### Function `list_to_stream(lx, stream=None)`

  * lx: a list representation of an XML document
  * stream: a text stream, such as `sys.stdout`, the object returned
    from `open()`, or an
    [`io.StringIO`](https://docs.python.org/3/library/io.html?highlight=io#io.StringIO)
    object.

As with list_to_collector, except that the contents are 'collected' to
stdout.  If the `stream` argument is present, send the output there
instead.  This function returns the number of characters written to
the stream.

### Class `Collector`

Collect strings or bytes, and return them as a iterator of bytestrings.  The
Collector object is given to the `list_to_collector` function to
accumulate the results of the conversion of the list.  The Collector
object may subsequently be treated as an iterator, returning a
sequence of bytestrings.  This may therefore be printed as:

    content = ['div', ['p', "Hello, world"], ["p", "Another paragraph"]]

    coll = listxml.Collector()
    listxml.list_to_collector(content, coll)
    for bs in coll:
        print(bs.decode('utf-8'), end='')

or write it out as a single bytestring:

    with open('output.xml', 'wb') as f:
        f.write(b''.join(coll))

We can also ‘append’ strings to the collector in an unsusprising way:

    coll = listxml.Collector()
    coll.append('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n')
    listxml.list_to_collector(content, coll)
    ...

Methods:

  * append(s): append something to the collector, which can be a string,
    a bytestring, or anything `str()` can work with.  Returns self.
  * get_length(): return the length of the contents, in bytes.

### Class `PrintCollector`

A Collector-like object which 'collects’ its output and sends it to a stream.
The output is sent to `sys.stdout`, unless an alternative is set with
the `set_stream()` method.

The ‘stream’ must be a text file, such as `sys.stdout`, the stream
returned by the `open()` function, or an in-memory object such as
`io.StringIO`.

This is not in fact a subclass of Collector, though it has the same
interface.

    coll = listxml.PrintCollector()
    listxml.list_to_collector(content, coll)

Keyword arguments:

  * `stream` : if the object is constructed with `stream=foo`, then
    that stream is installed as the default stream to which the
    collector writes, instead of `sys.stdout`.
  * `file` : the default stream is created as an output file pointing
    to this file; when called in this way, the object can be used as a
    Context Manager, or the object's `close()` function can close the
    collector and stream later.

Methods: as with `Collector`, with some adjustments

  * append(s): append something to the collector, as with `Collector`.  Returns self.
  * get_length(): returns the number of characters written to the stream.
  * set_stream(s): set the stream that is written to.
  * close(): close the output stream, if it is a file
    (but not if it is a stream, since the caller may wish to write
    more to the stream)).

The `PrintCollector` object can also be used as a context manager (in
which case it will usually make sense to include the `file`
parameter).

    with listxml.PrintCollector(file='myoutput.xml') as coll:
        listxml.list_to_collector(content, coll)

Or alternatively just use the `list_to_stream` function:

    with open('output.xml', 'w') as f:
        listxml.list_to_stream(content, f)

To print to a string:

    s = io.StringIO()
    with PrintCollector(stream=s) as coll:
        list_to_collector(['p', "hello"], coll)
    print(s.getvalue())


### Function `construct(filename_or_stream, keywords...)`

For symmetry, there is also a function to turn an XML source into a list.
Given a (string) filename or a text stream containing XML,
this constructs a list representation of the XML, and returns it.

Keyword arguments:

  * **attributes_as_dict**:
    If `attributes_as_dict` is False (default) then attributes are
    `[['name','value'], ...]`; if it is True, then attributes are a dict
    `{'name': 'value', ...}`.
  * **omit_empty_attlist**:
    If `omit_empty_attlist` is False (default)
    then there is always an attribute element, even when the attribute
    list is empty (ie, `[]` or `{}`); if it is True, then empty attribute
    lists are suppressed.

This reading function is, in this version, not XML Namespace-aware.
Adding that isn't hard, but it's currently unclear how best to
represent namespaces in a convenient way, when generating the input
list for writing.  Thus, at present, `xmlns` attributes in the input
XML are not interpreted in any special way.

If the argument is not a file name, it is an input stream, which can
come from a file `open()` or via
[io.StringIO](https://docs.python.org/3/library/io.html), to read from
a string containing XML:

    lx = construct("/path/to/file")

    with open("/path/to/file") as f:
        lx = construct(f)

    lx = construct(io.StringIO("<p>hello</p>"))

### Function `search_for_path(path, lx, with_element=False)`

A simple path query.  The syntax is a (very small!) subset of the XPath syntax.

The path argument is

    path      ::= node-spec ( '/' node-spec)*
    node-spec ::=   element-name
                  | element-name '[' predicate ']'
                  | '@' attribute-name
                  | <number>
    predicate ::= '@' attribute-name '=' attribute-value
    element-name, attribute-name ::= [a-zA-Z0-9_-]+
    attribute-value ::= '"' [^"]* '"' | "'" [^']* "'"

The function selects elements and attributes within the list which
have parent-child relationships which match the path, and returns a
list of all of the matching elements (rather than merely the first
one).

If the path ends with a `@attname` then the function instead returns a list of
attribute values.

If an element is qualified by a predicate, `[@att="value"]`, then it
matches only if it has an element `@att` with the given value.  The
attribute-value can be enclosed in single- or double-quotes.

If it has predicate `[<n>]`, then it matches only the n-th element in
the list (where the first element is no.1).

If the node-spec doesn't match the above syntax, then a `ValueError` is raised.

For example, given the document

    doc = ['div',
           ['foo', "p1"],
           ['bar', [['a1', 'v1x']], "p1x"],
           ['foo', ['p', ['bar', 'content']]],
           ['foo', ['bar', "p2"]],
           ['foo', ['bar', ['baz', "p3"]]],
           ['foo', ['bar', [['a1', 'v1']], "text", ['p', "p4"]]],
           ['foo', ['bar', [['a1', 'v2'], ['a3', 'v3']], "p5"]]]

the following `path` arguments produce the given results

path                 | search_for_path(path, doc)
---------------------|--------------
foo/bar              |  [['p2'], [['baz', 'p3']], ['text', ['p', 'p4']], ['p5']]
foo/bar/@a1          |  ['v1', 'v2']
foo/bar[@a1="v1"]    |  [['text', ['p', 'p4']]]
foo/bar[@a1="v1"]/p  |  [['p4']]
foo/bar[@a1="v2"]/@a3|  ['v3']

If `with_element` is True, then include the matching element, with
attributes, rather than only the content.  For example, with the above
document, `search_for_path('foo/bar[@a1="v1"]', doc,
with_element=True)` produces `[['bar', {'a1': 'v1'}, 'p4']]` rather
than only the content `[['p4']]`.

**Note:** the syntax of this function's path argument changed in v0.4.0.


### Function `is_listxml_p(lx)`

Return true if the argument is a valid listxml representation
of an element.  See below for the definition.


Common techniques
-----------------

Assemble a list:

    trs = [['tr', ['td', 'foo']],
           ['tr', ['td', 'bar']]]
    table = ['table', *trs]   # wrap an array of elements in a parent element

    doc = ['body',
           ['p',
            [['class', 'highlight']],
            "Here is table no.", 1],
           table,
           ['p', "that was ", ['em', "easy"]]]

    with open('t.xhtml', 'w') as f:
        listxml.list_to_stream(doc, stream=f)

Part of the point of this library is that in some circumstances it's
convenient to generate list content:

    elements = ['one', 'two']
    trs = [['tr', ['td', e]] for e in elements]

In this context, note the difference between

    table1 = ['table', trs]

and

    table2 = ['table', *trs]

The first produces

    ['table', [['tr', ['td', 'one']], ['tr', ['td', 'two']]]]

which is not the structure desired, because this appears to be an attribute `tr`,
with value `['td', 'one']` (this won't produce an error, since the
package will (successfully) call `str()` on the attribute value).
In contrast the second version produces

    ['table', ['tr', ['td', 'one']], ['tr', ['td', 'two']]]

which is correct, and which turns into

    <table><tr><td>one</td></tr><tr><td>two</td></tr></table>

Another possibility would be `table = ['table']; table.extend(trs)`.


Input syntax
------------

The input list consists of a single `element` representing an XML document, where

    element: [STRING, optional-attributes?, item ...]
    optional-attributes: [] | [[STRING, stringable], ...] | DICT
    item: element | stringable | BYTESTRING

where `STRING` and `BYTESTRING` are the Python types,
`DICT` is a (`STRING` -> `stringable`) Python dictionary,
and `stringable` is either a string,
or something (other than an `optional-attributes`) which
[`str()`](https://docs.python.org/3/library/stdtypes.html#str)
can turn into a string.

Thus:

    ['el', 'foo', 'b&r', ...]                         -- an element <el>foob&amp;r...</el>
    ['el', [['k1', 'v1'], ['k2', 'v2'], ...]], ...]   -- an element <el k1="v1" k2="v2"...>...</el>
    ['el', {'k1': 'v1', 'k2': 'v2', ...}, ...]        -- ditto

and the ... may include other such elements.  Items which are
‘stringable’ are escaped when being printed.  Items which are
bytestrings are not; thus it's possible to have
`b'<div>content</div>'` as an item and this will be emitted as-is,
even if doing so would produce invalid XML.


Release notes
-------------

Release 0.5.0 (2025 September 21):

  * `search_for_path`: the predicate was unduly strict in its syntax.
    It now accepts any string as an `attribute-value`.
  * `search_for_path`: added predicate `p[<n>]`, to match the n-th `p`
    element.

Release 0.4.2 (2024 September 31):

  * Fixed error in README.
  * Check argument types.
  * Minor refactoring.
  * Fixed: `PrintCollector(stream=s)` shouldn't close the stream.

Release 0.4.1 (2023 March 22):

  * Fixed `.../@att` search path in `search_for_path`.

Release 0.4.0 (2023 March 5):

  * The path argument to `search_for_path` changed to be a (small!)
    subset of the XPath syntax.  This is incompatible with the 0.3.0 syntax.

Release 0.3.0 (2022 September 25):

  * PrintCollector can now be used as a context manager.
  * The order of the arguments to `list_to_collector` has been swapped.
