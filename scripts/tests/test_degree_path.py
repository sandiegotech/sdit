import degree_path


def test_sequence_shape():
    seq = degree_path.sequence()
    assert seq[0].kind == "begin"
    gates = [s for s in seq if s.kind == "gate"]
    assert [g.semester for g in gates] == list(range(1, 9))
    spine = [s for s in seq if s.kind == "day" and not s.studio]
    # Semesters 1-4 are 5, 6, 5, 6 courses of 15 days: 330 days every learner walks.
    assert sum(1 for s in spine if s.semester <= 4) == 330


def test_first_week_runs_in_the_weekly_rhythm():
    week1 = [s for s in degree_path.sequence() if s.kind == "day" and s.semester == 1 and s.week == 1]
    assert [s.course["dir"] for s in week1] == ["HUM-101", "MATH-110", "PHYS-110", "CS-110", "WKSP-101"]
    assert [s.label for s in week1] == ["Mon", "Tue", "Wed", "Thu", "Fri"]
    assert all(s.published for s in week1)


def test_next_on_the_path_crosses_courses_and_weeks():
    nxt = degree_path.next_on_path("HUM-101", 1)
    assert nxt.key == ("MATH-110", 1)
    after_friday = degree_path.next_on_path("WKSP-101", 1)
    assert after_friday.key == ("HUM-101", 2)
    assert after_friday.published is False and after_friday.publishes is not None


def test_next_on_the_path_skips_studios():
    # Semester 5, Monday HUM 301: the next spine day is not a studio.
    nxt = degree_path.next_on_path("HUM-301", 1)
    assert nxt is not None and not nxt.studio


def test_unpublished_days_take_the_arc_title():
    s = degree_path.day_step("HUM-102", 2)
    assert s and not s.published and s.title and s.title != "Day 02"
