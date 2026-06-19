import frontmatter


def test_no_frontmatter():
    assert frontmatter.parse("# Hi\n\nbody") == ({}, "# Hi\n\nbody")


def test_basic_meta_and_body():
    meta, body = frontmatter.parse('---\ntitle: "Day 01 — X"\nday: 1\n---\n\n# Day 01\n\ntext\n')
    assert meta["title"] == "Day 01 — X"
    assert meta["day"] == 1
    assert body.startswith("# Day 01")


def test_body_is_lstripped():
    _meta, body = frontmatter.parse("---\na: b\n---\n\n\n  content")
    assert body == "content"


def test_unclosed_is_ignored():
    meta, body = frontmatter.parse("---\ntitle: x\n\nbody")
    assert meta == {} and body == "---\ntitle: x\n\nbody"
