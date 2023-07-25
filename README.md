# xmltread

![Tests](https://github.com/pjz/xmltread/actions/workflows/test.yml/badge.svg)

[xmltramp](http://www.aaronsw.com/2002/xmltramp/) was originally created by Aaron Swartz
for simple-yet-powerful parsing of RSS and other xml files.

It is a small, fast alternative to heavyweight parsers like BeautifulSoup and ElementTree.

It has been mildly rewritten for python 3 compatibility, including bringing the packaging up to date so it can once again be installed via pip.
Sadly, python modules can no longer be built from a single source file, but the tweaked original xmltramp lives inside of xmltread.

`from xmltread import xmltramp` works, so you don't need to replace xmltramp with xmltread in your code.

## Installation

via pip:

`pip install xmltread`

## Usage

Everyone's got their data in XML these days. You need to read it. You've looked at the other XML APIs and they all contain miles of crud that's only necessary when parsing the most arcane documents. Wouldn't it be nice to have an easy-to-use API for the normal XML documents you deal with? That's xmltramp:

```
>>> sample_xml = """<doc version="2.7182818284590451"
  xmlns="http://example.org/bar"
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns:bbc="http://example.org/bbc">
  <author><name>John Polk</name> and <name>John Palfrey</name></author>
  <dc:creator>John Polk</dc:creator>
  <dc:creator>John Palfrey</dc:creator>
  <bbc:show bbc:station="4">Buffy</bbc:show>
</doc>"""

>>> import xmltramp
>>> doc = xmltramp.Namespace("http://example.org/bar")
>>> bbc = xmltramp.Namespace("http://example.org/bbc")
>>> dc = xmltramp.Namespace("http://purl.org/dc/elements/1.1/")
>>> d = xmltramp.parse(sample_xml)
>>> d
<doc version="2.7182818284590451">...</doc>
>>> d('version')
'2.7182818284590451'
>>> d(version='2.0')
>>> d('version')
'2.0'
>>> d._dir
[<author>...</author>, <dc:creator>...</dc:creator>, <dc:creator>...</dc:creator>, <bbc:show bbc:station="4">...</bbc:show>]
>>> d._name
('http://example.org/bar', 'doc')
>>> d[0]                # First child.
<author>...</author>
>>> d.author            # First author.
<author>...</author>
>>> str(d.author)
'John Polk and John Palfrey'
>>> d[dc.creator]        # First dc:creator.
<dc:creator>...</dc:creator>
>>> d[dc.creator:]       # All creators.
[<dc:creator>...</dc:creator>, <dc:creator>...</dc:creator>]
>>> d[dc.creator] = "Me!!!"
>>> str(d[dc.creator])
'Me!!!'
>>> d[bbc.show](bbc.station)
'4'
>>> d[bbc.show](bbc.station, '5')
>>> d[bbc.show](bbc.station)
'5'

```

## Credits

Based on the original by Aaron Swartz.


