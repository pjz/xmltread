"""xmltramp: Make XML documents easily accessible.

Originally:
__version__ = "2.18"
__author__ = "Aaron Swartz"
__credits__ = "Many thanks to pjz, bitsko, and DanC."
__copyright__ = "(C) 2003-2006 Aaron Swartz. GNU GPL 2."

"""


def isstr(f):
    return isinstance(f, type(""))


def islst(f):
    return isinstance(f, type(())) or isinstance(f, type([]))


def isint(f):
    return isinstance(f, type(0))


empty = {
    "http://www.w3.org/1999/xhtml": [
        "img",
        "br",
        "hr",
        "meta",
        "link",
        "base",
        "param",
        "input",
        "col",
        "area",
    ]
}


def quote(x, elt=True):
    if elt and "<" in x and len(x) > 24 and x.find("]]>") == -1:
        return "<![CDATA[" + x + "]]>"
    else:
        x = x.replace("&", "&amp;").replace("<", "&lt;").replace("]]>", "]]&gt;")
    if not elt:
        x = x.replace('"', "&quot;")
    return x


class Element:
    def __init__(self, name, attrs=None, children=None, prefixes=None):
        if islst(name) and name[0] is None:
            name = name[1]
        if attrs:
            na = {}
            for k in attrs:
                if islst(k) and k[0] is None:
                    na[k[1]] = attrs[k]
                else:
                    na[k] = attrs[k]
            attrs = na

        self._name = name
        self._attrs = attrs or {}
        self._dir = children or []

        prefixes = prefixes or {}
        self._prefixes = dict(zip(prefixes.values(), prefixes.keys()))

        self._dNS = prefixes.get(None, None) if prefixes else None

    def __repr__(self, recursive=0, multiline=0, inprefixes=None):
        def qname(name, inprefixes):
            if not islst(name):
                return name
            if inprefixes[name[0]] is not None:
                return inprefixes[name[0]] + ":" + name[1]
            else:
                return name[1]

        def arep(a, inprefixes, addns=1):
            out = ""

            for p in self._prefixes:
                if p not in inprefixes:
                    if addns:
                        out += " xmlns"
                        if self._prefixes[p]:
                            out += ":" + self._prefixes[p]
                        out += '="' + quote(p, False) + '"'
                    inprefixes[p] = self._prefixes[p]

            for k in a:
                out += " " + qname(k, inprefixes) + '="' + quote(a[k], False) + '"'

            return out

        inprefixes = inprefixes or {"http://www.w3.org/XML/1998/namespace": "xml"}

        # need to call first to set inprefixes:
        attributes = arep(self._attrs, inprefixes, recursive)
        out = "<" + qname(self._name, inprefixes) + attributes

        if not self._dir and (
            self._name[0] in empty and self._name[1] in empty[self._name[0]]
        ):
            out += " />"
            return out

        out += ">"

        if recursive:
            content = 0
            for x in self._dir:
                if isinstance(x, Element):
                    content = 1

            pad = "\n" + ("\t" * recursive)
            for x in self._dir:
                if multiline and content:
                    out += pad
                if isstr(x):
                    out += quote(x)
                elif isinstance(x, Element):
                    out += x.__repr__(recursive + 1, multiline, inprefixes.copy())
                else:
                    raise TypeError(f"I wasn't expecting {x!r}.")
            if multiline and content:
                out += "\n" + ("\t" * (recursive - 1))
        else:
            if self._dir:
                out += "..."

        out += "</" + qname(self._name, inprefixes) + ">"

        return out

    def __str__(self):
        text = "".join(str(x) for x in self._dir)
        return " ".join(text.split())

    def __getattr__(self, n):
        if n[0] == "_":
            raise AttributeError(f"Use foo['{n}'] to access the child element.")
        if self._dNS:
            n = (self._dNS, n)
        for x in self._dir:
            if isinstance(x, Element) and x._name == n:
                return x
        raise AttributeError(f"No child element named {n!r}")

    def __hasattr__(self, n):
        for x in self._dir:
            if isinstance(x, Element) and x._name == n:
                return True
        return False

    def __setattr__(self, n, v):
        if n[0] == "_":
            self.__dict__[n] = v
        else:
            self[n] = v

    def __getitem__(self, n):
        if isint(n):  # d[1] == d._dir[1]
            return self._dir[n]
        elif isinstance(n, slice):
            # numerical slices
            if isint(n.start) or n.start is n.stop is None:
                return self._dir[n.start : n.stop]

            # d['foo':] == all <foo>s
            n = n.start
            if self._dNS and not islst(n):
                n = (self._dNS, n)
            out = []
            for x in self._dir:
                if isinstance(x, Element) and x._name == n:
                    out.append(x)
            return out
        else:  # d['foo'] == first <foo>
            if self._dNS and not islst(n):
                n = (self._dNS, n)
            for x in self._dir:
                if isinstance(x, Element) and x._name == n:
                    return x
            raise KeyError(n)

    def __setitem__(self, n, v):
        if isint(n):  # d[1]
            self._dir[n] = v
        elif isinstance(n, slice):
            # d['foo':] adds a new foo
            n = n.start
            if self._dNS and not islst(n):
                n = (self._dNS, n)

            nv = Element(n)
            self._dir.append(nv)

        else:  # d["foo"] replaces first <foo> and dels rest
            if self._dNS and not islst(n):
                n = (self._dNS, n)

            nv = Element(n)
            nv._dir.append(v)
            replaced = False

            todel = []
            for i in range(len(self)):
                if self[i]._name == n:
                    if replaced:
                        todel.append(i)
                    else:
                        self[i] = nv
                        replaced = True
            if not replaced:
                self._dir.append(nv)
            for i in todel:
                del self[i]

    def __delitem__(self, n):
        if isint(n):
            del self._dir[n]
        elif isinstance(n, slice):
            # delete all <foo>s
            n = n.start
            if self._dNS and not islst(n):
                n = (self._dNS, n)

            for i in range(len(self)):
                if self[i]._name == n:
                    del self[i]
        else:
            # delete first foo
            for i in range(len(self)):
                if self[i]._name == n:
                    del self[i]
                break

    def __call__(self, *_pos, **_set):
        if _set:
            for k in _set.keys():
                self._attrs[k] = _set[k]
        if len(_pos) > 1:
            for i in range(0, len(_pos), 2):
                self._attrs[_pos[i]] = _pos[i + 1]
        if len(_pos) == 1:
            return self._attrs[_pos[0]]
        if len(_pos) == 0:
            return self._attrs

    def __len__(self):
        return len(self._dir)


class Namespace:
    def __init__(self, uri):
        self.__uri = uri

    def __getattr__(self, n):
        return (self.__uri, n)

    def __getitem__(self, n):
        return (self.__uri, n)


def load_fileobj(fileobj):
    from .seeder import seed

    return seed(fileobj)


def load_url(url):
    from urllib.request import urlopen

    return load_fileobj(urlopen(url))


def load_file(filename: str):
    with open(filename) as fileobj:
        return load_fileobj(fileobj)


def parse(text):
    from io import StringIO

    return load_fileobj(StringIO(text))
