from xmltread import find, parse


def test_find():
    p = parse(
        """
    <doc>a
      <baz d="1">f
        <b d="2">o</b>ob
        <b>a</b>r
      </baz>a
    </doc>"""
    )

    found = list(find(p))
    assert len(found) == 3
    assert [t._name for t in found] == ['baz', 'b', 'b']

    found = list(find(p, tag="b"))
    assert len(found) == 2
    assert [t._name for t in found] == ['b', 'b']

    found = list(find(p, attr="d"))
    assert len(found) == 2
    assert [t._name for t in found] == ['baz', 'b']

    found = list(find(p, attr="d=1"))
    assert len(found) == 1
    assert found[0]._name == 'baz'
    assert len(list(e for e in found[0] if not isinstance(e, str))) == 2


