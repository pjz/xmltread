from .xmltramp import Element


def find(e: Element, tag):
    """generator: find all the tags with the name 'tag'"""
    for t in e:
        if not isinstance(t, Element):
            continue
        if t._name == tag:
            yield tag
        else:
            yield from find(t, tag)
