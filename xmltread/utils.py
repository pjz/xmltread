from .xmltramp import Element

import logging

logger = logging.getLogger(__name__)


def find(e: Element, tag=None, attr=None):
    """generator: find some tags
        * if tag is specified, returned tags must have that name
        * if attr is specified,
          * if attr is of the form 'name=value' then the attr of the specified name must have the specified value
          * otherwise the attr must exist
        * if no params are specified, match all the tags
    """
    for t in e:
        if not isinstance(t, Element):
            logger.info('skipping %r', t)
            continue
        if tag is not None and t._name == tag:
            logger.info('yielding matching tag %r', t)
            yield t
        elif attr is not None:
            k, *v = attr.split('=')
            if k in t._attrs and (v == [] or t._attrs[k] == v[0]):
                logger.info('yielding tag matching attrs %r=%r %r', k, v, t)
                yield t
            else:
                logger.info('%r=%r not found in %r', k, v, t._attrs)
        elif tag is None and attr is None:
            yield t
        logger.info('descending into tag %r', t)
        yield from find(t, tag, attr)
