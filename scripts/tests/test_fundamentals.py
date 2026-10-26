"""The Studio Fundamentals map holds: twelve skills, each taught by name on a
Year 1 or 2 day whose arc carries it, each shown by named course highlights."""
import fundamentals


def test_the_map_holds():
    assert fundamentals.check() == []


def test_twelve_fundamentals_in_four_groups_all_by_year_two():
    from catalog import load_catalog
    sem = {c["dir"]: c["semester"] for c in load_catalog()["courses"]}
    data = fundamentals.load()
    assert len(data["fundamentals"]) == 12
    assert {f["group"] for f in data["fundamentals"]} == {g["id"] for g in data["groups"]}
    for f in data["fundamentals"]:
        course = f["taught"].split("/")[0]
        assert sem[course] <= 4, f["id"]


def test_a_dropped_mark_is_caught():
    # Pretend the arc for CS-110 day 15 lost its sentence about commits.
    import arcs
    real = arcs.load_arc

    def fake(path):
        import copy
        arc = real(path)
        if path.name == "CS-110" and arc:
            arc = copy.deepcopy(arc)   # load_arc may cache; never mutate the real one
            arc.days[15].idea = arc.days[15].idea.replace("commit", "change")
        return arc
    arcs.load_arc = fake
    try:
        errs = fundamentals.check()
    finally:
        arcs.load_arc = real
    assert any("versions" in e and "CS-110 day 15" in e for e in errs), errs


def test_course_pages_and_portfolio_see_the_same_list():
    import portfolio
    m = portfolio.degree_map()
    for dir, c in m["courses"].items():
        assert c["fundamentals"] == [f["name"] for f in fundamentals.for_course(dir)]
    assert "Raster and vector" in m["courses"]["CAP-402"]["fundamentals"]
    note = fundamentals.course_note("WKSP-101")
    assert "Shows the fundamentals" in note and "fundamentals.html#photographing-work" in note
    assert fundamentals.course_note("HUM-101") == ""


def test_the_page_renders_every_fundamental():
    html = fundamentals.page()
    for f in fundamentals.load()["fundamentals"]:
        assert f'id="{f["id"]}"' in html, f["id"]
    assert "/courses/WKSP-101/" in html
