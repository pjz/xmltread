from xmltread import find, parse


def test_find():
    p = parse(
        """
    <doc>a
      <baz>f
        <b>o</b>ob
        <b>a</b>r
      </baz>a
    </doc>"""
    )

    assert len(list(find(p, "b"))) == 2
