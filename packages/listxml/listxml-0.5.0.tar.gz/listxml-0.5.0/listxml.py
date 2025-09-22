###
#
# Creating XML.
#
#    l = [['p', "Hello, world"], ["p", "Another paragraph"]]
#    coll = Collector()
#    list_to_collector(l, coll)
#
# coll can be used as an iterator, so print eg b''.join(coll).
# See list_to_collector below for the structure of the input list.
#
# Alternatively, use PrintCollector as a collector, to send output to stdout,
# or another stream (list_to_stream does that).

import re, sys
import xml.sax # this package, and the expat parser, are included in Python by default

_escapees = re.compile("[<>&\"]")
_escapees_lookup = { "<": "&lt;",
                     ">": "&gt;", # unnecessary but tidy
                     "&": "&amp;",
                     "\"": "&#34;" } # necessary only in attributes
def _collect_with_escapes(coll, s):
    '''Append the string s to the collector, escaping characters where necessary.'''
    startpos = 0
    m = _escapees.search(s, startpos)
    if m:
        while m:
            pos = m.start()
            coll.append(s[startpos:pos])
            coll.append(_escapees_lookup[s[pos]])
            startpos = pos+1
            m = _escapees.search(s, startpos)
        coll.append(s[startpos:])
    else:
        coll.append(s)

class Collector(object):
    """Collect strings or bytes, and return them as a iterator
    (really just a wrapper for List.append())"""
    def __init__(self):
        self._l = []
    def append(self, s):
        """Append something to the collector, namely
        string, bytes, or anything str() can work with.
        Return self."""
        if isinstance(s, bytes):
            self._l.append(s)
        elif isinstance(s, str):
            self._l.append(s.encode('utf-8'))
        else:
            # This final case won't happen as a call from the functions below,
            # but might, I suppose, if this class is used by something outside
            # this package (so we might as well DTRT).
            self._l.append(str(s).encode('utf-8'))
        return self
    def get_length(self):
        "The length of the contents, in bytes"
        llen = 0
        for s in self._l:
            llen += len(s)
        return llen
    def __iter__(self):
        """Make this an iterable object containing the things which have been
        collected so far by this object."""
        return self._l.__iter__()

class PrintCollector(object):
    """A Collector-like object which 'collects' its output and sends it to a stream.
    The output is sent to sys.stdout, unless the `stream` argument is present.
    This is not in fact a subclass of Collector, though it has the same interface.

    If the output is a file, we close it at the end.
    If the output is a stream, we do not,
    since the caller may have other things to send there."""
    def __init__(self, stream=None, file=None):
        if stream and file:
            raise ValueError("PrintCollector: can't specify stream and file parameters")
        self._is_file_stream = False
        if file:
            self.set_stream(open(file, 'w'))
            self._is_file_stream = True
        elif stream:
            self.set_stream(stream)
        else:
            self.set_stream(sys.stdout)
        self._nwritten = 0
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, ext_tb):
        self.close()
        return False
    def close(self):
        if self._stream != sys.stdout:
            if self._is_file_stream:
                self._stream.close()
            self._stream = sys.stdout

    def append(self, s):
        """Send something to the collector stream, namely
        string, bytes, or anything str() can work with.
        Return self."""
        if isinstance(s, str):
            self._nwritten += len(s)
            print(s, end='', file=self._stream)
        elif isinstance(s, bytes):
            tmpstr = s.decode('utf-8')
            self._nwritten += len(tmpstr)
            print(tmpstr, end='', file=self._stream)
        else:
            # DTRT, as above
            t = str(s)
            self._nwritten += len(t)
            print(t, end='', file=self._stream)
        return self
    def get_length(self):
        """Return the number of characters written.
        The name is unexpected, but is intended to match
        the corresponding Collector method."""
        return self._nwritten
    def set_stream(self, s):
        """Set the stream that this object writes to.
        The ‘stream’ must be a text file, such as `sys.stdout`, the stream
        returned by the `open()` function, or an in-memory object such as
        `io.StringIO`."""
        if self._is_file_stream:
            self._stream.close()
        self._stream = s
    def __iter__(self):
        """Return an empty iterator."""
        return [].__iter__()

def list_to_collector(l, coll):
    """Convert the input list to XHTML and send it to the collector.
    The input list consists of:

       element: item | [string, optional-attributes?, element ...]
       optional-attributes: [[string, string], ...] | dict
       item: string | bytestring

    thus:

       ['el', 'foo', ...]                                -- an element <el>foo...</el>
       ['el', [['k1', 'v1'], ['k2', 'v2'], ...]], ...]   -- an element <el k1="v1" k2="v2"...>...</el>
       ['el', {'k1': 'v1', 'k2': 'v2', ...}, ...]        -- ditto

    and the ... may include other such elements.  Items which are
    strings are escaped when being printed.  Items which are
    bytestrings are not; thus it's possible to have
    b'<div>content</div>' as an item and this will be emitted as-is.

    The 'coll' object is any object with an append() method,
    such as the Collector class above.

    Return the input collector.
    """
    if isinstance(l, bytes):
        # a special case: bytes are copied verbatim to the output
        coll.append(l)
    elif not isinstance(l, list):
        # content: this is either a string (the usual case),
        # or something else which str() is expected to work on
        _collect_with_escapes(coll, str(l))
    elif len(l) == 0:
        pass
    else:
        body = None
        if not isinstance(l[0], str):
            raise TypeError("element names must be strings, not {}".format(l[0]))
        if len(l) > 1:
            if (isinstance(l[1], list) # list, possibly of attributes
                and l[1]               # not empty
                and isinstance(l[1][0], list)): # ...containing lists
                # attributes as a list
                coll.append(f"<{l[0]}")
                for (a, v) in l[1]:
                    if isinstance(a, str):
                        coll.append(f' {a}="')
                        _collect_with_escapes(coll, str(v)) # str(v)==v if v is a string
                        coll.append(b'"')
                    else:
                        raise TypeError(f"attribute names must be strings, not {a}")
                body = l[2:]
            elif isinstance(l[1], dict):
                # attributes as a dict
                coll.append(f"<{l[0]}")
                for kv in l[1].items():
                    if isinstance(kv[0], str):
                        coll.append(f' {kv[0]}="')
                        _collect_with_escapes(coll, str(kv[1]))
                        coll.append(b'"')
                    else:
                        raise TypeError(f"attribute names must be strings, not {kv[0]}")
                body = l[2:]
            else:
                coll.append(f"<{l[0]}")
                body = l[1:]
        else:
            coll.append(f"<{l[0]}")
            body = l[1:]

        if body:
            coll.append(b'>')
            for content in body:
                list_to_collector(content, coll)
            coll.append(f"</{l[0]}>")
        else:
            # empty element
            coll.append(b" />")

    return coll

def list_to_stream(l, stream=None):
    """As with list_to_collector, except that the contents are 'collected' to stdout.
    If the `stream` argument is present, send the output there instead.
    This function returns the number of characters written to the stream."""
    coll = PrintCollector(stream)
    list_to_collector(l, coll)
    return coll.get_length()

# See https://docs.python.org/3/library/xml.sax.handler.html#module-xml.sax.handler
class ListHandler(xml.sax.handler.ContentHandler):
    def __init__(self, attributes_as_dict=False, omit_empty_attlist=False):
        self._elementstack = None
        self._result = None
        self._attributes_as_dict=attributes_as_dict
        self._omit_empty_attlist=omit_empty_attlist
    def get_result(self):
        return self._result
    def startDocument(self):
        self._elementstack = [['*ROOT*']]
    def endDocument(self):
        self._result = self._elementstack.pop().pop()
    def startElement(self, name, attrs):
        attlist = [[item[0], item[1]] for item in attrs.items()]
        if not attlist and self._omit_empty_attlist:
            t = [name]
        elif self._attributes_as_dict:
            t = [name, dict(attlist)]
        else:
            t = [name, attlist]
        self._elementstack.append(t)
    # The following is an alternative, which has different paths for
    # namespaced and non-namespaced elements.  Omit this at present,
    # since it's not currently clear to me how best to represent
    # namespaced elements for output.
    #
    # def _startElement(self, name, attlist):
    #     if not attlist and self._omit_empty_attlist:
    #         t = [name]
    #     elif self._attributes_as_dict:
    #         t = [name, dict(attlist)]
    #     else:
    #         t = [name, attlist]
    #     self._elementstack.append(t)
    # def startElement(self, name, attrs):
    #     self._startElement(name, [[item[0], item[1]] for item in attrs.items()])
    # def startElementNS(self, name, qname, attrs):
    #     attlist = [[("{{{}}}{}".format(item[0][0], item[0][1]) if item[0][0] else item[0][1]),
    #                 item[1]] for item in attrs.items()]
    #     if name[0]:
    #         self._startElement("{{{}}}{}".format(name[0], name[1]), attlist)
    #     else:
    #         self._startElement(name[1], attlist)
    def endElement(self, name):
        t = self._elementstack.pop()
        self._elementstack[len(self._elementstack)-1].append(t)
    # def endElementNS(self, name, qname):
    #     if name[0]:
    #         self.endElement("{{{}}}{}".format(name[0], name[1]))
    #     else:
    #         self.endElement(name[1])
    def characters(self, content):
        self._elementstack[len(self._elementstack)-1].append(content)

def _is_stringable_p(x):
    if isinstance(x, dict) or isinstance(x, list):
        # exclude this from being stringable, even though it has a __str__ method
        return False
    return isinstance(x, str) or ('__str__' in dir(x))

def is_listxml_p(lx):
    """Return true if the argument is a valid listxml representation
    of an element.

    The input list consists of a single element representing an XML document, where

        element: [STRING, optional-attributes?, item ...]
        optional-attributes: [] | [[STRING, stringable], ...] | DICT
        item: element | stringable | BYTESTRING

    where STRING and BYTESTRING are the Python types,
    DICT is a (STRING -> stringable) Python dictionary,
    and stringable is either a string,
    or something (other than a dict) which str() can turn into a string."""

    if not (isinstance(lx, list)
            and lx
            and isinstance(lx[0], str)):
        return False
    if len(lx) > 1 and isinstance(lx[1], dict):
        for k,v in lx[1].items():
            if not (isinstance(k, str) and _is_stringable_p(v)):
                return False
        body = lx[2:]
    elif (len(lx) > 1
          and isinstance(lx[1], list)
          and (not lx[1] or isinstance(lx[1][0], list))):
        for [k,v] in lx[1]:
            if not (isinstance(k, str) and _is_stringable_p(v)):
                return False
        body = lx[2:]
    else:
        body = lx[1:]

    for x in body:
        if not (_is_stringable_p(x)
                or isinstance(x, bytes)
                or is_listxml_p(x)):
            return False

    return True

def construct(file_or_stream,
              attributes_as_dict=False,
              omit_empty_attlist=False):
    """Given a (string) filename or a text stream containing XML,
    construct a list representation of the XML.

    If attributes_as_dict is False (default) then attributes are [['name','value'], ..];
    if it is True, then attributes are a dict {'name': 'value', ...}.
    If omit_empty_attlist=False (default) then there is always an
    attribute element, even when the attribute list is empty (ie, [] or {});
    if it is True, then empty attribute lists are suppressed."""

    parser = xml.sax.make_parser()
    # if with_namespaces:
    #     parser.setFeature("http://xml.org/sax/features/namespaces", True)

    h = ListHandler(attributes_as_dict, omit_empty_attlist)
    parser.setContentHandler(h)
    parser.parse(file_or_stream)

    return h.get_result()

def _search_for_path_list(topels, els, ll, with_element):
    """Like _search_for_path(), except that the content argument is a list of elements,
    rather than an element."""
    #print("_path_list: els={}  ll={}  with_element={}".format(els, ll, with_element))
    if els:
        res = []
        idx = 0
        for l in ll:
            idx += 1
            if isinstance(l, list):
                p = _search_for_path(topels, els, l, with_element, idx)
                if p:
                    res.extend(p)
        return res
    else:
        # nothing more to search for
        return [ll]

def _search_for_path(topels, els, l, with_element, idx):
    """The worker for search_for_path().  This passes both topels, which
    is the initial argument to search_for_path() and els, which is the path being
    currently searched-for, which is worn down as the search advances successfully."""
    # FIXME: null-els:
    # What should search_for_path([], x) return?
    # If it should return x, then...
    if not l:
        return []
    if not els:
        return l
    # but if it should return [], then...
    # if not els or not l:
    #     return []

    if len(l) == 1:
        atts = {}
        body = []
    elif isinstance(l[1], list) and (not(l[1]) or isinstance(l[1][0], list)):
        atts = dict(l[1])
        body = l[2:]
    elif isinstance(l[1], dict):
        atts = l[1]
        body = l[2:]
    else:
        atts = {}
        body = l[1:]

    #print("_path: els={}  l={}  atts={}  body={} idx={}".format(els, l, atts, body, idx))

    if els[0] == l[0]:
        if len(els) == 1:
            return [[l[0], atts, *body]] if with_element else [body]
        elif isinstance(els[1], list):
            # match a node predicate
            # els is [elementname, [xxx]]
            #
            if isinstance(els[1][0], int):
                # els is [elementname, [int]]
                #print("pred: topels={}  els={}  body={}".format(topels, els, body))
                if els[1][0] == idx:
                    if len(els) == 2:
                        if with_element:
                            return [[els[0], atts, *body]]
                        else:
                            return [body]
                    else:
                        return _search_for_path_list(topels, els[2:], [body[els[1][0]-1]], with_element)
                else:
                    return []
            elif len(els[1]) == 1:
                # els is [elementname, ['attname']]
                a = els[1][0]
                if a in atts:
                    return [atts[a]]
                else:
                    #print("notatt: topels={}  body={}".format(topels, body))
                    return _search_for_path_list(topels, topels, body, with_element)
            elif len(els[1]) == 2:
                # els is [elementname, ['attname', 'value']]
                a = els[1][0]
                if a in atts and els[1][1] == atts[a]:
                    #print("2att: topels={} els2={} body={}".format(topels, els[2:], body))
                    if with_element and not els[2:]:
                        # _search_for_path_list doesn't quite handle this case
                        return [[els[0], atts, *body]]
                    elif len(els) >= 3 and isinstance(els[2], list):
                        # Lookahead: the next test is (another) attribute test.
                        # Construct an els[] search expression which omits the first
                        # attribute, and re-call.
                        return _search_for_path(topels, [els[0], *els[2:]], l,
                                                with_element, idx)
                    else:
                        return _search_for_path_list(topels, els[2:], body, with_element)
                else:
                    # restart from here, with the initial search path
                    return _search_for_path_list(topels, topels, body, with_element)
            else:
                raise ValueError(f"search_for_path: paths which end in a list must have either one or two values, not {topels}")
        else:
            #print("1match: topels={}  els1={}  body={}".format(topels, els[1:], body))
            return _search_for_path_list(topels, els[1:], body, with_element)
    elif topels != els:
        # restart the search from here, but with the initial search-path
        #print("restart: topels={}  l={}".format(topels, l))
        return _search_for_path(topels, topels, l, with_element, idx)
    else:
        #print("nomatch: topels={}  body={}".format(topels, body))
        return _search_for_path_list(topels, topels, body, with_element)

def search_for_path(xp, l, with_element=False):
    """A simple path query.  The syntax is similar to the XPath syntax, but simpler.

    The 'xp' path argument is a string, with syntax:

        path      ::= node-spec ( '/' node-spec)*
        node-spec ::=   element-name
                      | element-name '[' predicate ']'
                      | element-name '@' attribute-name
        predicate ::= '@' attribute-name '=' attribute-value
                      | <number>
        element-name, attribute-name ::= [a-zA-Z0-9_-]+
        attribute-value = '"' [^"]* '"' | "'" [^']* "'"

    The function selects and returns elements and attributes within the list which
    have parent-child relationships which match the path.  Thus

        p/q  returns (the contents of) all 'q' elements contained within a 'p' element;
        p/@a returns the value of any 'a' attributes on a 'p' element;
        p[@a="foo"] returns any 'p' elements whcih have an attribute 'a' with value "foo"
        p[2] returns the second p element (the first element is 1)

    If `with_element` is true, then include the matching element, with
    attributes, rather than only the content."""

    if not isinstance(xp, str):
        raise ValueError(f"argument xp must be a string, not {xp}")

    els_list = _parse_xpath(xp)
    #print("{} -> {}".format(xp, els_list))
    return _search_for_path(els_list, els_list, l, with_element, 0)

_xptrans_atts = re.compile(r'(?:(\w+)(?:\[([^]]+)\])?|@(\w+))$')
_xptrans_attvalue = re.compile('(?:@(\\w+)=(?:"([^"]*)"|\'([^\']*)\')|(\\d+))$')
def _parse_xpath(xp):
    def xptrans(el):
        if not el:
            raise ValueError(f"Malformed xpath (empty element): {xp}")
        m = _xptrans_atts.match(el)
        if m:
            if m.group(2):
                # el[spec]
                m2 = _xptrans_attvalue.match(m.group(2))
                if m2:
                    if m2.group(2) != None:
                        # spec is [@att="value"]
                        return (m.group(1), [m2.group(1), m2.group(2)])
                    elif m2.group(3) != None:
                        # spec is [@att='value']
                        return (m.group(1), [m2.group(1), m2.group(3)])
                    elif m2.group(4) != None:
                        # spec is [n]
                        # we may support this in future, but I'm undecided how to implement it
                        return (m.group(1), [int(m2.group(4))])
                        #raise ValueError(f"Malformed xpath (bad predicate; [n] currently unsupported): {xp}")
                    else:
                        # what?
                        raise ValueError(f"Malformed xpath (bad predicate): {xp}")
                else:
                    raise ValueError(f"Malformed xpath (bad predicate; odd value?): {xp}")
            elif m.group(1):
                # el
                return (m.group(1),)
            else:
                # @att
                return ([m.group(3)],)
        else:
            raise ValueError(f"Malformed xpath: {xp}")
    r = []
    if xp:
        for el in [xptrans(x) for x in xp.split('/')]:
            r.extend(el)
    return r

# doc = ['div',
#        ['foo', "p1"],
#        ['bar', [['a1', 'v1x']], "p1x"],
#        ['foo', ['p', ['bar', 'content']]],
#        ['foo', ['bar', "p2"]],
#        ['foo', ['bar', ['baz', "p3"]]],
#        ['foo', ['bar', [['a1', 'v1']], "text", ['p', "p4"]]],
#        ['foo', ['bar', [['a1', 'v2'], ['a3', 'v3']], "p5"]]]
# for path in ('foo/bar', 'foo/bar/@a1', 'foo/bar[@a1="v1"]', 'foo/bar[@a1="v1"]/p', 'foo/bar[@a1="v2"]/@a3'):
#     print("{}  |  {}".format(path, search_for_path(path, doc)))
