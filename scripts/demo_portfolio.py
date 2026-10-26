#!/usr/bin/env python3
"""demo_portfolio.py — a sample Portfolio, clearly labelled, at /portfolio/demo/.

Rowan Hale is a fictional learner, written to show what four years of answers
and made things look like in the Portfolio: Day 0, a few days in every
semester, the made things, and all eight gates. It renders through the same
code as a real published portfolio. No account holds it and nothing about it
is stored on the server; the build writes portfolio/demo.json, and the public
view loads that file when the handle is "demo" (reserved on the server).

Dates follow the real publishing calendar: a day is answered the day after it
publishes, a gate a few days after its semester ends.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

NAME = "Rowan Hale"
NOTE = ("A sample portfolio. Rowan Hale is a fictional learner, written to show what four years of "
        "answers and made things look like here. Nothing on this page belongs to a real person.")

START = dt.date(2026, 12, 28)   # committed and answered Day 0 the week before Week 2

BEGIN = {
    "education": "Getting a degree so I can get a better job. Honestly that's most of it. Maybe also proving to myself I can finish something.",
    "make": "An app, probably. Something people use.",
    "believe": "That you're either a math person or you're not, and I'm not.",
}

# Gate answers: education, make, believe, made, changed.
GATES = {
    1: ("Less about the job than I thought. It's being able to look at something, a wave, a poem, a cup in a museum, and actually see it. I didn't know I couldn't.",
        "Something physical. I want to finish a board before summer.",
        "That I'm not a math person. Less sure now. Calculus on a skate ramp is just paying attention.",
        "A three-minute film about my phone, a motion study of a drop-in, and a box of things I finished in the Workshop.",
        "I finish things. Day 1 said finishing was the assignment and I didn't believe it."),
    2: ("Learning to make things that work and to say why they work. The board taught me more than any lecture: the numbers either hold water or they don't.",
        "A working computer from gates, which I didn't think was possible for me. And a better board.",
        "That a sound is just a sum of waves. I can show it now.",
        "A 6'2\" fish with the calculations to defend it, shown at the exhibition, and an eight-bit computer that runs my program.",
        "I stopped saying I'm not a math person."),
    3: ("Practice being wrong in public and fixing it. Every essay came back marked. The marks were the education.",
        "Writing I'm not embarrassed by.",
        "That the first draft is the real one. It isn't. The third is.",
        "Four essays with the drafts beside them, and a program that went from forty seconds to a fifth of a second.",
        "I read contracts now. And I cut a third of every sentence."),
    4: ("Knowing what's true when someone is selling me something, including when I'm the one selling. And choosing a direction from what I've made, not what I imagined.",
        "Things people use. I declared Design.",
        "That my judgment is better than chance. I scored my forecasts. It is, barely.",
        "Forty public swell forecasts, scored; a ninety-second film that went further than I expected; a carburetor rebuilt for a client.",
        "I want the numbers before I believe anything, my own ideas first."),
    5: ("Learning who I'm making for. A thing nobody can use isn't finished.",
        "An instrument for people who can't afford instruments.",
        "That scenes invent things before companies do. I watched it happen at the bowl.",
        "Tide Clock, a game in a café that strangers actually play, and a fin box that doesn't crack.",
        "I watch people use my work now instead of explaining it to them."),
    6: ("The field term broke my idea that education happens in school. It's the habit of noticing what you assumed and checking it.",
        "The sensor, working, in the water, for a month.",
        "That the thing that never failed is the thing you stopped checking.",
        "A temperature and tide logger that lived on the pier for five weeks, and a field report from twelve weeks at an instrument shop.",
        "I write down the result that contradicts me first."),
    7: ("Taste and responsibility. The tools can make almost anything now. What's left is deciding what's worth making and owning it when it goes wrong.",
        "The capstone: a coastal sensor anyone can build for forty dollars.",
        "That a machine can be my collaborator and the work still be mine, if I keep the ledger.",
        "A generative piece about kelp, with the rules on the wall, and a capstone proposal that survived the scoping.",
        "I keep a record of every handoff to a model, and I can say which calls were mine."),
    8: ("On Day 0 I wrote that it was about a better job. I'd keep the part about finishing. The rest I'd cross out. Education is learning to see clearly, make things that hold up, and stand behind them in front of people. The job is a side effect.",
        "The company that builds the forty-dollar sensor for scientists who can't buy the four-thousand-dollar one.",
        "That small scenes invent the future. I defended it in SIG 301 and I'd defend it again.",
        "The capstone, defended on the sand in front of five people who use it; a short film for the Crossing; a final build on the wall.",
        "Almost everything I wrote on Day 0, except that I wanted to finish something."),
}

# (course dir, day, answer)
DAYS = [
    ("HUM-101", 1, "My phone at night. The mast is leaving it in the kitchen, which I did for a week. I slept better and missed nothing."),
    ("MATH-110", 3, "The tide line on the steps at the Cove. It keeps getting closer to the next step and never quite touches it before it turns."),
    ("PHYS-110", 6, "I pushed off the wall in the pool and the wall pushed me across the lane. It didn't feel like the wall did anything."),
    ("CS-110", 2, "Text me the buoy reading at 6 a.m. so I know whether to bother."),
    ("WKSP-101", 1, "A paper airplane that flies straight. It took eleven tries and throwing away the first ten without arguing with myself."),
    ("HUM-102", 2, "Losing the job at the shop. It looked like a loss. It's the reason I have time for this."),
    ("MATH-120", 5, "Played a voice memo at double speed. The pitch went up an octave. Same sound, half the time, twice the frequency."),
    ("PHYS-120", 8, "Black's sand burned, the water was cold. Same sun. Water takes more energy to warm up, which is why the marine layer happens."),
    ("CS-120", 4, "1101 plus 0111. The carry ran all the way to the left and made a fifth bit. Twenty."),
    ("SIG-101", 3, "Whisper. A room loses it at ten feet. The phone keeps every breath."),
    ("HUM-201", 4, "The company owns it. I read the contract. Locke would have had questions."),
    ("MATH-210", 3, "Paint: three tubes and white. The screen: red, green, blue. My grandmother's spices, which is a stretch."),
    ("RHET-110", 2, "\"I think that it is probably important to note that\" became nothing. That third was me being afraid to say it."),
    ("CS-210", 6, "A word in my notes. I used to search the whole file. Now the program jumps straight to it."),
    ("HUM-202", 1, "A shelf I built got used as a step stool. I went back and made it stronger instead of telling them to stop."),
    ("MATH-220", 6, "Whether the 7:10 bus is late. It's late more than half the time. About 60 out of 100 before I'd stop calling it chance."),
    ("RHET-210", 5, "\"Four out of five surfers prefer\" on a wax ad. Out of how many? It didn't say. I looked. Thirty."),
    ("CS-220", 9, "Choosing a wave: I weigh the size, the crowd, and my mood, and then I weigh how much to trust the mood."),
    ("WKSP-202", 14, "The wiring on the carburetor job. Nobody else wanted it, so I took it."),
    ("HUM-301", 2, "If it surprised me in a way it couldn't have been told to. I haven't seen it yet."),
    ("ART-310", 4, "The barista at the café on Newport. She'll meet it on the counter at 7 a.m. with no time."),
    ("ENGR-310", 7, "My fin box was cast. You can see the seam where the mold closed."),
    ("SIG-301", 3, "A trick at the bowl that only exists because someone filmed it and the others copied it."),
    ("HUM-302", 5, "\"This sensor makes it cheap to watch the coast, and cheap to watch the people on it.\""),
    ("FLD-301", 6, "I assumed the salt was the enemy. It was the cable chafing on the piling. I noticed in week four."),
    ("ENGR-320", 10, "The pier mount. It held through two storms, so I stopped looking. The bracket had rusted halfway through."),
    ("HUM-401", 3, "The Colorado, mostly, by way of an aqueduct I've never seen."),
    ("CS-320", 2, "I asked a model to clean my sensor data and didn't write down what it removed. I wrote it down after."),
    ("ART-410", 9, "The rule that the kelp grows toward the light, and the choice of which forty out of four thousand to keep."),
    ("CAP-401", 4, "A coastal temperature and tide sensor anyone can build for forty dollars. It's done when three people who aren't me build one and their numbers match the pier's."),
    ("HUM-402", 14, "That I'd been wrong on Day 0 and I was glad I wrote it down."),
    ("ART-320", 5, "A window, north, about the size of a door. It made my roommate's face look like a painting."),
    ("CAP-402", 13, "Five people: two scientists, a lifeguard, a teacher, and my mother. They saw three sensors agree with the pier to a tenth of a degree."),
    ("SIG-401", 11, "Said it to my roommate: the kit ships on the first of May. Then I shipped it."),
]

# (course dir, title, form, words, level)
MADE = [
    ("HUM-101", "The Mast", "film", "A three-minute film of a phone left in a kitchen overnight, cut against the Sirens episode and The Endless Summer. Designing around the weakness instead of pretending it away.", "proficient"),
    ("MATH-110", "Drop-In at Washington Street", "report", "One drop-in, frame-stepped from a phone video: position, velocity, and the instant of greatest acceleration, with the calculus beside the data.", "proficient"),
    ("CS-120", "Eight Bits from Nothing", "program", "A simulated computer built up from NAND gates that runs a program I wrote to add the week's swell heights.", "developing"),
    ("PHYS-120", "A 6'2\" Fish, by the Numbers", "object", "A twin-fin fish with its volume, rocker, and fin area calculated and defended before I cut the foam.", "proficient"),
    ("WKSP-102", "The Fish, Glassed", "build", "The same board, shaped and glassed in the Workshop, shown at the year-end exhibition and ridden the next morning.", "proficient"),
    ("RHET-110", "Four Essays, Drafts Beside Finals", "essay", "A made thing described, an argument, a review, and a letter. The distance between the drafts and the finals is the point.", "proficient"),
    ("MATH-220", "Forty Calls", "forecast", "Forty public swell forecasts for the Cove, made in advance and scored. Brier score 0.19, which is better than guessing and worse than I thought.", "proficient"),
    ("SIG-201", "Ninety Seconds at Sunset Cliffs", "film", "A short piece released into a real feed, with the numbers: who watched, how far, and why I think it moved.", "developing"),
    ("WKSP-202", "A Carburetor for a 1978 CB400", "build", "Rebuilt for a client to their brief and deadline. It started on the second kick.", "proficient"),
    ("ART-310", "Tide Clock", "build", "A small interactive piece on a café counter that tells you, at a glance, whether the tide is worth the drive. Observed for two weeks; strangers use it.", "proficient"),
    ("ENGR-310", "A Fin Box That Doesn't Crack", "object", "A redesigned fin box with drawings and tolerances, cast and tested to failure on the bench. It failed above the load I designed for.", "proficient"),
    ("ENGR-320", "Pier Logger", "build", "A temperature and tide logger that lived in saltwater on the pier for five weeks and agreed with the official station.", "proficient"),
    ("FLD-301", "Twelve Weeks at an Instrument Shop", "report", "A field report, the journal behind it, and my mentor's evaluation from a placement building ocean instruments.", "proficient"),
    ("ART-320", "Low Tide, Six Minutes", "film", "The Crossing: a short film, screened, about the hour the reef shows itself.", "developing"),
    ("ART-410", "Kelp", "other", "A generative work: the rules for how the kelp grows are mine, the model draws, and the forty I kept are on the wall with the rules beside them.", "proficient"),
    ("CAP-402", "Cheap Eyes on the Water", "build", "An open coastal temperature and tide sensor anyone can build for about forty dollars, with the build guide, the data, and three independent builds that matched the pier. Defended in public before faculty and outside examiners.", "mastered"),
]


def _iso(d: dt.date, hour: int = 18) -> str:
    return f"{d.isoformat()}T{hour:02d}:00:00Z"


def build() -> dict:
    import publishing
    from catalog import load_catalog

    sem_of = {c["dir"]: c.get("semester") for c in load_catalog()["courses"]}

    def day_date(d: str, n: int) -> dt.date:
        when = publishing.week_date(sem_of[d], n)
        return (when or START) + dt.timedelta(days=1)

    def gate_date(n: int) -> dt.date:
        return publishing.week_date(n, 15) + dt.timedelta(days=5)

    answers = [{"lesson": "/begin", "heading": "commitment", "content": START.isoformat(), "at": _iso(START, 9)}]
    for qid, text in BEGIN.items():
        answers.append({"lesson": "/begin", "heading": qid, "content": text, "at": _iso(START, 9)})
    for d, n, text in DAYS:
        answers.append({"lesson": f"/courses/{d}/day-{n:02d}", "heading": "answer", "content": text, "at": _iso(day_date(d, n))})
    for n, (edu, make, believe, made, changed) in GATES.items():
        when = _iso(gate_date(n), 20)
        for qid, text in (("education", edu), ("make", make), ("believe", believe), ("made", made), ("changed", changed)):
            answers.append({"lesson": f"/gates/semester-{n}", "heading": qid, "content": text, "at": when})
    for d, title, form, words, level in MADE:
        shown = publishing.week_date(sem_of[d], 15) + dt.timedelta(days=3)
        record = {"title": title, "form": form, "link": "", "words": words, "date": shown.isoformat(), "level": level}
        answers.append({"lesson": f"/courses/{d}/made", "heading": "made-thing",
                        "content": json.dumps(record, ensure_ascii=False), "at": _iso(shown, 12)})
    return {"name": NAME, "note": NOTE, "answers": answers}


def write_all(write, out: Path = ROOT) -> None:
    write(out / "portfolio" / "demo.json", json.dumps(build(), ensure_ascii=False, indent=1) + "\n")
