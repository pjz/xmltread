from xml.sax.handler import EntityResolver, DTDHandler, ContentHandler, ErrorHandler
from xml.sax.handler import feature_namespaces
from xml.sax import make_parser

from .xmltramp import Element


class Seeder(EntityResolver, DTDHandler, ContentHandler, ErrorHandler):
    def __init__(self):
        self.stack = []
        self.ch = ""
        self.prefixes = {}
        ContentHandler.__init__(self)

    def startPrefixMapping(self, prefix, uri):
        if prefix not in self.prefixes:
            self.prefixes[prefix] = []
        self.prefixes[prefix].append(uri)

    def endPrefixMapping(self, prefix):
        self.prefixes[prefix].pop()

    def startElementNS(self, name, qname, attrs):
        ch = self.ch
        self.ch = ""
        if ch and not ch.isspace():
            self.stack[-1]._dir.append(ch)

        attrs = dict(attrs)
        newprefixes = {}
        for k in self.prefixes.keys():
            newprefixes[k] = self.prefixes[k][-1]

        self.stack.append(Element(name, attrs, prefixes=newprefixes.copy()))

    def characters(self, ch):
        self.ch += ch

    def endElementNS(self, name, qname):
        ch = self.ch
        self.ch = ""
        if ch and not ch.isspace():
            self.stack[-1]._dir.append(ch)

        element = self.stack.pop()
        if self.stack:
            self.stack[-1]._dir.append(element)
        else:
            self.result = element


def seed(fileobj):
    seeder = Seeder()
    parser = make_parser()
    parser.setFeature(feature_namespaces, 1)
    parser.setContentHandler(seeder)
    parser.parse(fileobj)
    return seeder.result
