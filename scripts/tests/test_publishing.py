import datetime as dt

import publishing

CAL = {
    "publishing": {"first_release": dt.date(2027, 1, 4), "cadence_days": 7, "breaks": []},
    "semesters": [{"n": i, "label": f"S{i}", "weeks": 15} for i in range(1, 9)],
}


def test_launch_week_has_no_date():
    assert publishing.week_date(1, 1, CAL) is None


def test_weeks_count_straight_through_the_degree():
    assert publishing.week_date(1, 2, CAL) == dt.date(2027, 1, 4)
    assert publishing.week_date(1, 15, CAL) == dt.date(2027, 4, 5)
    assert publishing.week_date(2, 1, CAL) == dt.date(2027, 4, 12)
    # Semester 8, Week 15 is the 119th week after the first release.
    assert publishing.week_date(8, 15, CAL) == dt.date(2027, 1, 4) + dt.timedelta(weeks=118)


def test_a_break_pushes_later_weeks_back():
    cal = {**CAL, "publishing": {**CAL["publishing"], "breaks": [{"after": {"semester": 1, "week": 15}, "weeks": 2}]}}
    assert publishing.week_date(1, 15, cal) == dt.date(2027, 4, 5)
    assert publishing.week_date(2, 1, cal) == dt.date(2027, 4, 26)


def test_formats():
    d = dt.date(2027, 1, 11)
    assert publishing.long_date(d) == "Monday, 11 January 2027"
    assert publishing.short_date(d) == "11 Jan"


def test_real_calendar_starts_on_a_monday():
    assert publishing.week_date(1, 2).weekday() == 0
