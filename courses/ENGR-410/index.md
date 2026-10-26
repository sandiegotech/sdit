---
id: engr-410
title: "ENGR 410 — Robotics & Autonomous Systems"
course_code: ENGR 410
units: 4
thread: The Depths
status: syllabus
syllabus:
  level: upper
  prerequisites: [HUM 202, MATH 220, CS 220, RHET 210, WKSP 202, ENGR 310]
  corequisites: []
  method: [studio]
  hours:
    instruction: 1
    studio_or_lab: 6
    independent: 5
  materials:
    - {title: "Stanley: The Robot That Won the DARPA Grand Challenge", author: "Sebastian Thrun et al.", edition: "Journal of Field Robotics, 2006; author's copy", access: open, cost: 0}
    - {title: "Elephants Don't Play Chess", author: "Rodney Brooks", edition: "1990; author's copy at MIT", access: open, cost: 0}
    - {title: "Intelligence Without Representation", author: "Rodney Brooks", edition: "1991; author's copy at MIT", access: open, cost: 0}
    - {title: "The American Practical Navigator, dead reckoning chapter", author: "Nathaniel Bowditch", edition: "National Geospatial-Intelligence Agency", access: open, cost: 0}
    - {title: "Perseverance AutoNav description", author: "NASA", access: open, cost: 0}
    - {title: "On Governors", author: "James Clerk Maxwell", edition: "1868", access: open, cost: 0}
    - {title: "Introduction to A*", author: "Amit Patel", edition: "Red Blob Games", access: open, cost: 0}
    - {title: "DARPA Robotics Challenge final report", author: "DARPA", access: open, cost: 0}
    - {title: "Autonomous Driving in Urban Environments: Boss and the Urban Challenge", author: "Chris Urmson et al.", edition: "2008; author's copy at CMU", access: open, cost: 0}
    - {title: "Apollo 11 air-to-ground transcript, final descent", author: "NASA", access: open, cost: 0}
    - {title: "Small unmanned aircraft rules, 14 CFR Part 107", author: "Federal Aviation Administration", access: open, cost: 0}
    - {title: "Opportunity mission summary", author: "NASA", access: open, cost: 0}
    - {title: "Closed parking lot, Mission Bay access, range safety officer, and rover platforms", author: "San Diego Institute of Technology", access: provided, cost: 0, note: "Open learner: a small wheeled robot kit, a camera, a hallway or driveway."}
  assessment:
    - {component: "Weekly platform, log, and written exercises", weight: 20}
    - {component: "Signed safety case and three critiques: moving, rehearsal, failures", weight: 15}
    - {component: "Unassisted examination: step response, hand-planned path, odometry fix", weight: 20}
    - {component: "The live demonstration, logs, and account", weight: 45}
  exam: "Day 11, tools closed, ninety minutes with a pencil: diagnose a controller's step response, plan a path by hand on a grid map, and state where a robot is and how sure you are from odometry and one landmark fix."
  rubric: working-system
  core_competencies:
    quantitative-reasoning: D
    written-communication: D
    oral-communication: D
  outcome_levels:
    intelligence: M
    craft: M
    judgment: M
---

# ENGR 410 — Robotics & Autonomous Systems

**The Depths** · 4 units · Semester 7 · Depth studio — Engineering · the Crossing for others

## Overview

In 2004, DARPA offered a million dollars to any vehicle that could cross 142 miles of the Mojave by itself. The best went seven and a half miles. A year later five finished, and what had changed was not the hardware: the teams stopped trusting the demo and started trusting the desert. That gap — between the demo and the world — is this studio's subject. Everything you have made converges here: the mechanism from ENGR 310, the instrument from ENGR 320, the system from CS 310, and the unforgiving physical world. The machine has to work in the parking lot, not the slide deck.

The catalog says robotics: perception, control, planning, autonomy. The room says: a team of two or three, a platform the size of a cooler, a job written in one sentence a stranger could judge, ten logged rehearsals, a safety case, and one live run with an obstacle placed by someone outside the team. Each week on the page is one idea and one thing to experience — a robot that thought too slowly for the world, a lighthouse that resets a sailor's error, an autopilot flown hands-off over the Seine in 1914, the best robots on Earth falling over in public. Each week in the lot you rehearse.

This is a depth studio: a parking lot you can close, a stretch of bay you can use, a range safety officer, platforms that have been crashed before, and a master who has fielded unmanned systems and watched one fail in front of a customer. The page is the brief. The course ends in a made thing — an autonomous system demonstrated live, one take, in the world, doing its job.

## The Two Registers

- **Catalog register:** Robotics — perception, control, planning, autonomy.
- **Teaching frame:** Perception, control, autonomy in the physical world — where the demo meets the parking lot.

## Course Information

<!-- sdit:info:begin -->
| | |
|---|---|
| Catalog number | ENGR 410 — Robotics & Autonomous Systems |
| Units | 4 semester units · 180 hours of work over 15 weeks |
| Each week | 1 h instruction · 6 h studio or laboratory · 5 h independent work |
| Level | Upper division |
| Offered | Semester 7 · Year 4 · Fall |
| Prerequisites | [HUM 202](/courses/HUM-202/index.html), [MATH 220](/courses/MATH-220/index.html), [CS 220](/courses/CS-220/index.html), [RHET 210](/courses/RHET-210/index.html), [WKSP 202](/courses/WKSP-202/index.html), [ENGR 310](/courses/ENGR-310/index.html) |
| Corequisites | None |
| Instructional method | Studio |
| Instructor | A practitioner-scholar with a body of work in the field: a terminal degree, or equivalent professional standing documented under the Institute's rubric (The Degree, section 9). |
| Rubric | [The working system (Computation and Engineering)](/curriculum/rubrics.html#working-system) |
| Core competencies | Written communication (developed) · Oral communication (developed) · Quantitative reasoning (developed) |
| Unassisted examination | Day 11, tools closed, ninety minutes with a pencil: diagnose a controller's step response, plan a path by hand on a grid map, and state where a robot is and how sure you are from odometry and one landmark fix. |

**Required materials**

- *Stanley: The Robot That Won the DARPA Grand Challenge*, Sebastian Thrun et al. — Journal of Field Robotics, 2006; author's copy · open, free
- *Elephants Don't Play Chess*, Rodney Brooks — 1990; author's copy at MIT · open, free
- *Intelligence Without Representation*, Rodney Brooks — 1991; author's copy at MIT · open, free
- *The American Practical Navigator, dead reckoning chapter*, Nathaniel Bowditch — National Geospatial-Intelligence Agency · open, free
- *Perseverance AutoNav description*, NASA · open, free
- *On Governors*, James Clerk Maxwell — 1868 · open, free
- *Introduction to A**, Amit Patel — Red Blob Games · open, free
- *DARPA Robotics Challenge final report*, DARPA · open, free
- *Autonomous Driving in Urban Environments: Boss and the Urban Challenge*, Chris Urmson et al. — 2008; author's copy at CMU · open, free
- *Apollo 11 air-to-ground transcript, final descent*, NASA · open, free
- *Small unmanned aircraft rules, 14 CFR Part 107*, Federal Aviation Administration · open, free
- *Opportunity mission summary*, NASA · open, free
- *Closed parking lot, Mission Bay access, range safety officer, and rover platforms*, San Diego Institute of Technology · provided in the room; open learner: a small wheeled robot kit, a camera, a hallway or driveway

Required materials cost: nothing. Every item is open, borrowable from a public library, or provided in the room.
<!-- sdit:info:end -->

## Learning Outcomes

By the end of this course you can:

1. Build a perception and localization pipeline that turns sensors into a position and a map, carries its uncertainty forward, and resets its drift against landmarks. → *Command of Intelligence* · *Quantitative reasoning*
2. Design and tune a feedback controller for a physical platform, diagnose its response, and explain where the error came from. → *Workmanship*
3. Plan a path through a mapped space and replan when the space changes, choosing where a learned component earns its place and where plain code must remain. → *Command of Intelligence · Judgment*
4. Write and sign a safety case for an unmanned system — emergency stop, geofence, speed limit, lost-link behavior — and run every test under it. → *Judgment* · *Written communication*
5. Demonstrate an autonomous system doing a stated job live, in an uncontrolled space, with a recorded success rate, and account for what it saw, decided, and got wrong. → *Workmanship* · *Oral communication*

*Each outcome maps to the five institutional outcomes (Judgment, Command of Intelligence, Workmanship, Articulation, Breadth of Mind) — the assessment spine of the degree and its accreditation evidence file.*

## The Made Thing

An autonomous system demonstrated live, in the world, doing its job. A ground robot or a small unmanned surface vessel, built or adapted by a team of two or three, given a job in one sentence and a real, uncontrolled space — the Institute's parking lot or a stretch of Mission Bay — that completes the job without a human on the controls while handling an obstacle placed after the last rehearsal. Ten rehearsals logged with a success rate; an emergency stop, a geofence, and a signed safety case; and on the last day, one take in front of the room with a range safety officer's hand on the stop, followed by the logs and the account. It enters your portfolio for review at the annual gate.

## How You're Assessed

- **The live demonstration**, one take, judged by whether the machine does the job stated on Day 2, and by how it handles what was not there at rehearsal.
- **The rehearsal record** — ten logged runs with a success rate, and the fix for every failure.
- **The safety case**, signed before any autonomous run, judged by what the machine does when it loses contact with you.
- **Three studio critiques** — Day 5 (it moves, and why it did not go straight), Day 10 (full rehearsal in the venue, video and log played together), Day 14 (every fall from ten rehearsals, and the fix for each).
- **An unassisted examination** on Day 11, tools closed: a step response to diagnose, a map to plan a path through by hand, odometry to localize from. The autonomy you build will hand you the problem at the worst moment; the institution certifies the human who can take it.
- Everything lands in your **portfolio**, reviewed against the five outcomes at the end-of-year gate.

<!-- sdit:weights:begin -->

| Component | Weight |
|---|---|
| Weekly platform, log, and written exercises | 20% |
| Signed safety case and three critiques: moving, rehearsal, failures | 15% |
| Unassisted examination: step response, hand-planned path, odometry fix | 20% |
| The live demonstration, logs, and account | 45% |
| **Total** | **100%** |

Grades follow the scale in the [academic policies](/curriculum/policies.html#grading).
<!-- sdit:weights:end -->

## The Daily Path

One session per course day — each one built to look easy and pull you in: one thing to experience, one idea, one question to carry. The schedule below is generated from the course's own day files.

<!-- sdit:days:begin -->
The fifteen days below are the open spine of the course, about ten minutes each. The hours in Course Information are the course.

### Day 01 — Seven Miles Into the Desert

Publishes Monday, 18 September 2028.

### Day 02 — Sense, Think, Act, Sense Again

Publishes Monday, 25 September 2028.

### Day 03 — Where Am I?

Publishes Monday, 2 October 2028.

### Day 04 — Seeing Is Guessing

Publishes Monday, 9 October 2028.

### Day 05 — Drive in a Straight Line

Publishes Monday, 16 October 2028.

### Day 06 — Control Is a Conversation With Error

Publishes Monday, 23 October 2028.

### Day 07 — Plan the Path, Expect the Cone

Publishes Monday, 30 October 2028.

### Day 08 — Wheels, Legs, Hulls, Rotors

Publishes Monday, 6 November 2028.

### Day 09 — When to Let It Learn

Publishes Monday, 13 November 2028.

### Day 10 — Rehearsal in the Lot

Publishes Monday, 20 November 2028.

### Day 11 — Fly It by Hand

Publishes Monday, 27 November 2028.

### Day 12 — Safety Is the First Feature

Publishes Monday, 4 December 2028.

### Day 13 — The Job, Not the Demo

Publishes Monday, 11 December 2028.

### Day 14 — Robots Fall Down

Publishes Monday, 18 December 2028.

### Day 15 — Live, One Take, in the Lot

Publishes Monday, 25 December 2028.
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
