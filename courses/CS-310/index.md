---
id: cs-310
title: "CS 310 — Machine Learning II / AI Systems Engineering"
course_code: CS 310
units: 4
thread: The Depths
status: syllabus
syllabus:
  level: upper
  prerequisites: [HUM 202, MATH 220, CS 220, RHET 210, WKSP 202]
  corequisites: []
  method: [studio]
  hours:
    instruction: 1
    studio_or_lab: 6
    independent: 5
  materials:
    - {title: "Python 3", author: "Python Software Foundation", edition: "current release, python.org", access: open, cost: 0}
    - {title: "An AI assistant of the learner's choice", access: open, cost: 0}
    - {title: "The studio server and bench review", access: provided, cost: 0, note: "Open learner uses any free-tier host or a home machine."}
    - {title: "Hidden Technical Debt in Machine Learning Systems", author: "D. Sculley et al.", edition: "NeurIPS 2015 proceedings", access: open, cost: 0}
    - {title: "Information Management: A Proposal", author: "Tim Berners-Lee", edition: "1989, hosted by CERN", access: open, cost: 0}
    - {title: "Clever Hans (The Horse of Mr. von Osten)", author: "Oskar Pfungst", edition: "1911, Project Gutenberg", access: open, cost: 0}
    - {title: "Novum Organum", author: "Francis Bacon", edition: "Project Gutenberg", access: open, cost: 0}
    - {title: "The Aeneid, Book II", author: "Virgil", edition: "Lectio edition", access: open, cost: 0}
    - {title: "On Governors", author: "James Clerk Maxwell", edition: "1868, Internet Archive", access: open, cost: 0}
    - {title: "Cybernetics", author: "Norbert Wiener", access: library, cost: 0}
    - {title: "Report of the Presidential Commission on the Space Shuttle Challenger Accident, with Appendix F", author: "Rogers Commission", edition: "NASA History Office", access: open, cost: 0}
    - {title: "My Life and Work", author: "Henry Ford", edition: "1922, Project Gutenberg", access: open, cost: 0}
    - {title: "Meditations, Book 10", author: "Marcus Aurelius", edition: "Lectio edition", access: open, cost: 0}
  assessment:
    - {component: "The deployed system, its evaluation harness, and the failure analysis, defended with its users in the room", weight: 45}
    - {component: "Weekly studio milestones: harness, logs, monitor, and critique days", weight: 25}
    - {component: "Unassisted examination, Day 11: diagnosis from logs and an evaluation function written by hand", weight: 20}
    - {component: "Bench review participation", weight: 10}
  exam: "Day 11, 90 minutes, tools closed: diagnose a system you have never seen from a page of evaluation results and a page of logs, write a one-page failure analysis, and write a working evaluation function for one stated case."
  rubric: working-system
  core_competencies:
    quantitative-reasoning: D
    critical-thinking: D
    written-communication: D
  outcome_levels:
    intelligence: D
    craft: D
    judgment: D
---

# CS 310 — Machine Learning II / AI Systems Engineering

**The Depths** · 4 units · Semester 5 · Depth studio — Engineering · the Crossing for others

## Overview

Models are easy; systems are hard. In CS 220 you trained a model and reported a number. In this studio you put a model inside a system, give the system to people who are not you, and find out what the number was hiding. Deployment, evaluation, agents, failure modes — the engineering discipline of making machine intelligence dependable, learned the only way it can be: on a system that is live.

The studio runs on three verbs. What breaks: the plumbing around the model fails before the model does. What lies: a model produces what is probable, a metric measures what is easy, and a user types what is hostile. What scales: doing it once and doing it ten thousand times a day are different kinds of engineering. Each week on the page is one idea and one thing to experience — a chess automaton with its cabinet open, a horse that could not count, the first logged bug, an accident report written so the next engineer could use it. Each week off the page you ship.

This is a depth studio: a room with a server, a master who has carried a pager for a system like yours, and a bench review where logs are read aloud. The page is the brief. It ends the way every SDIT course ends — in a made thing, defended out loud, with its users in the room.

## The Two Registers

- **Catalog register:** Applied machine learning systems — deployment, evaluation, agents, failure modes.
- **Teaching frame:** Real systems in the world — what breaks, what lies, what scales.

## Course Information

<!-- sdit:info:begin -->
| | |
|---|---|
| Catalog number | CS 310 — Machine Learning II / AI Systems Engineering |
| Units | 4 semester units · 180 hours of work over 15 weeks |
| Each week | 1 h instruction · 6 h studio or laboratory · 5 h independent work |
| Level | Upper division |
| Offered | Semester 5 · Year 3 · Fall |
| Prerequisites | [HUM 202](/courses/HUM-202/index.html), [MATH 220](/courses/MATH-220/index.html), [CS 220](/courses/CS-220/index.html), [RHET 210](/courses/RHET-210/index.html), [WKSP 202](/courses/WKSP-202/index.html) |
| Corequisites | None |
| Instructional method | Studio |
| Instructor | A practitioner-scholar with a body of work in the field: a terminal degree, or equivalent professional standing documented under the Institute's rubric (The Degree, section 9). |
| Rubric | [The working system (Computation and Engineering)](/curriculum/rubrics.html#working-system) |
| Core competencies | Written communication (developed) · Quantitative reasoning (developed) · Critical thinking (developed) |
| Unassisted examination | Day 11, 90 minutes, tools closed: diagnose a system you have never seen from a page of evaluation results and a page of logs, write a one-page failure analysis, and write a working evaluation function for one stated case. |

**Required materials**

- *Python 3*, Python Software Foundation — current release, python.org · open, free
- *An AI assistant of the learner's choice* · open, free
- *The studio server and bench review* · provided in the room; open learner uses any free-tier host or a home machine
- *Hidden Technical Debt in Machine Learning Systems*, D. Sculley et al. — NeurIPS 2015 proceedings · open, free
- *Information Management: A Proposal*, Tim Berners-Lee — 1989, hosted by CERN · open, free
- *Clever Hans (The Horse of Mr. von Osten)*, Oskar Pfungst — 1911, Project Gutenberg · open, free
- *Novum Organum*, Francis Bacon — Project Gutenberg · open, free
- *The Aeneid, Book II*, Virgil — Lectio edition · open, free
- *On Governors*, James Clerk Maxwell — 1868, Internet Archive · open, free
- *Cybernetics*, Norbert Wiener · public library, free
- *Report of the Presidential Commission on the Space Shuttle Challenger Accident, with Appendix F*, Rogers Commission — NASA History Office · open, free
- *My Life and Work*, Henry Ford — 1922, Project Gutenberg · open, free
- *Meditations, Book 10*, Marcus Aurelius — Lectio edition · open, free

Required materials cost: nothing. Every item is open, borrowable from a public library, or provided in the room.
<!-- sdit:info:end -->

## Learning Outcomes

By the end of this course you can:

1. Deploy a system with a model inside it to real users, with logging, monitoring, a fallback, and a way to turn it off. → *Workmanship*
2. Build and maintain an evaluation harness — fixed cases, expected outcomes, run before every change — and use it to tell improvement from luck. → *Command of Intelligence* · *Quantitative reasoning*
3. Identify how a model lies: shortcut learning, confabulation, distribution shift, and hostile input — and design the system so the lie is caught. → *Judgment* · *Critical thinking*
4. Design and bound an agent — tools, loops, budgets, and the stop condition — and say what it may never do. → *Command of Intelligence*
5. Write a failure analysis in the form of an accident report: what was believed, what was true, what changed, what is still unknown. → *Judgment · Workmanship* · *Written communication*

*Each outcome maps to the five institutional outcomes (Judgment, Command of Intelligence, Workmanship, Articulation, Breadth of Mind) — the assessment spine of the degree and its accreditation evidence file.*

## The Made Thing

A deployed AI system with real users, an evaluation harness, and a documented failure analysis. A service with a model inside it, at an address, used for four weeks by at least ten people who are not in the course; a harness that has caught at least one regression before it shipped; and a failure analysis naming at least three failures found in the field. On the last day the system runs live, the harness runs live, two users say what it does for them, and the failure analysis is read aloud. It enters your portfolio and is reviewed at the annual gate.

## How You're Assessed

- **The deployed system**, judged by whether it works for its users, by its logs, and by what it does when it is wrong.
- **The evaluation harness**, judged by what it measures, what it hides, and whether it ran before every change.
- **The failure analysis**, defended out loud at the end of the course, with the system's users present.
- **Three studio critiques** — Days 5, 10, and 14 — in which the room runs your system, reads your logs, and tries to break it. You demonstrate a failure before anyone finds one.
- **An unassisted examination** on Day 11, tools closed: given logs and evaluation results from a system you have never seen, you diagnose it by hand and write a one-page failure analysis. The institution certifies the human; in this field the human's job is to know when the machine is wrong.
- Everything lands in your **portfolio**, reviewed against the five outcomes at the end-of-year gate.

<!-- sdit:weights:begin -->

| Component | Weight |
|---|---|
| The deployed system, its evaluation harness, and the failure analysis, defended with its users in the room | 45% |
| Weekly studio milestones: harness, logs, monitor, and critique days | 25% |
| Unassisted examination, Day 11: diagnosis from logs and an evaluation function written by hand | 20% |
| Bench review participation | 10% |
| **Total** | **100%** |

Grades follow the scale in the [academic policies](/curriculum/policies.html#grading).
<!-- sdit:weights:end -->

## The Daily Path

One session per course day — each one built to look easy and pull you in: one thing to experience, one idea, one question to carry. The schedule below is generated from the course's own day files.

<!-- sdit:days:begin -->
The fifteen days below are the open spine of the course, about ten minutes each. The hours in Course Information are the course.

### Day 01 — The Model Is the Smallest Part

Publishes Monday, 21 February 2028.

### Day 02 — Ship the Smallest True Thing

Publishes Monday, 28 February 2028.

### Day 03 — The Harness Before the Feature

Publishes Monday, 6 March 2028.

### Day 04 — The Horse Could Not Count

Publishes Monday, 13 March 2028.

### Day 05 — Show It Breaking

Publishes Monday, 20 March 2028.

### Day 06 — It Will Say Things That Are Not So

Publishes Monday, 27 March 2028.

### Day 07 — Someone Will Type Something Hostile

Publishes Monday, 3 April 2028.

### Day 08 — The World Moves Under the Model

Publishes Monday, 10 April 2028.

### Day 09 — An Agent Is a Loop With Hands

Publishes Monday, 17 April 2028.

### Day 10 — What It Did at Three in the Morning

Publishes Monday, 24 April 2028.

### Day 11 — With the Tools Closed

Publishes Monday, 1 May 2028.

### Day 12 — Cost Is a Design Constraint

Publishes Monday, 8 May 2028.

### Day 13 — Design the Day It Is Wrong

Publishes Monday, 15 May 2028.

### Day 14 — Write the Accident Report

Publishes Monday, 22 May 2028.

### Day 15 — Real Users, Live

Publishes Monday, 29 May 2028.
<!-- sdit:days:end -->


## Policies

<!-- sdit:policies:begin -->
- **Attendance and participation.** See [attendance](/curriculum/policies.html#attendance).
- **AI use.** Tools are open in every course, and the human is examined unaided. See [the AI policy](/curriculum/policies.html#ai).
- **Academic integrity.** See [academic integrity](/curriculum/policies.html#integrity).
- **Accommodations.** See [accommodations](/curriculum/policies.html#accommodations).
- **Late work.** See [late work](/curriculum/policies.html#late-work).
<!-- sdit:policies:end -->

---

*Every course here is built to one standard: it ends in a made thing you can show, and it ships day by day.*
