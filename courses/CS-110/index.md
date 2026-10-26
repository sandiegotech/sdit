---
id: cs-110
title: "CS 110 — Programming Fundamentals"
course_code: CS 110
units: 4
thread: Computation & Intelligent Systems
semester: 1
status: day1
syllabus:
  level: lower
  prerequisites: []
  corequisites: []
  method: [lecture, laboratory]
  hours:
    instruction: 2
    studio_or_lab: 3
    independent: 7
  materials:
    - {title: "Python 3", author: "Python Software Foundation", edition: "current release, python.org", access: open, cost: 0}
    - {title: "An AI assistant of the learner's choice", access: open, cost: 0}
    - {title: "This Too Shall Pass (Rube Goldberg Machine)", author: "OK Go", edition: "official channel", access: open, cost: 0}
    - {title: "Mountain Interval", author: "Robert Frost", edition: "Project Gutenberg #29345", access: open, cost: 0}
    - {title: "The Boston Cooking-School Cook Book", author: "Fannie Merritt Farmer", edition: "1896, Project Gutenberg #65061", access: open, cost: 0}
    - {title: "The Iliad, Book 2", author: "Homer", edition: "Lectio edition", access: open, cost: 0}
    - {title: "The Mythical Man-Month", author: "Frederick P. Brooks Jr.", access: library, cost: 0}
  assessment:
    - {component: "Weekly builds, graded on whether they work and whether you can explain them", weight: 25}
    - {component: "Verification log, kept from Day 2", weight: 10}
    - {component: "Unassisted examinations in code, Day 8 and Day 14", weight: 20}
    - {component: "The shipped program, write-up, and line-by-line defense", weight: 45}
  exam: "Day 8 and Day 14, tools closed: read a fifteen-line program on paper and write exactly what it prints, write a small function by hand, then find and fix the bug in a program you are given and write a function from a one-sentence specification."
  rubric: working-system
  core_competencies:
    critical-thinking: I
    oral-communication: I
    written-communication: I
  outcome_levels:
    intelligence: I
    craft: I
---

# CS 110 — Programming Fundamentals

**Computation & Intelligent Systems** · 4 units · Semester 1 · Required core — everyone takes it

## Overview

Code is the most literal language ever invented — the machine does exactly what you say, which is how you find out what you actually said. This course is your first sustained conversation with that very fast, very literal apprentice: variables, control flow, functions, data, debugging — the moves every program is made of.

Taught **AI-native from the first hour**. The tools stay open on the table — instrumented, critiqued, never hidden — because pretending they don't exist would be training you for a world that's gone. The skill this course actually grades is **direction and verification**: telling the machine precisely what you want, and proving to yourself that what came back is right. That second skill is the one that survives every model release.

One day a week, about ten minutes a sitting, hands on the keys from Day 1, building toward a small program that does something you genuinely wanted done.

## The Two Registers

- **Catalog register:** Introduction to programming — variables, control flow, functions, data structures, debugging. Transfer-legible CS1.
- **Teaching frame:** Speaking to Machines — AI tools open, instrumented, and critiqued from day one. The graded skill is direction and verification.

## Course Information

<!-- sdit:info:begin -->
| | |
|---|---|
| Catalog number | CS 110 — Programming Fundamentals |
| Units | 4 semester units · 180 hours of work over 15 weeks |
| Each week | 2 h instruction · 3 h studio or laboratory · 7 h independent work |
| Level | Lower division |
| Offered | Semester 1 · Year 1 · Fall |
| Prerequisites | None |
| Corequisites | None |
| Instructional method | Lecture, Laboratory |
| Instructor | A practitioner-scholar with a body of work in the field: a terminal degree, or equivalent professional standing documented under the Institute's rubric (The Degree, section 9). |
| Rubric | [The working system (Computation and Engineering)](/curriculum/rubrics.html#working-system) |
| Core competencies | Written communication (introduced) · Oral communication (introduced) · Critical thinking (introduced) |
| Unassisted examination | Day 8 and Day 14, tools closed: read a fifteen-line program on paper and write exactly what it prints, write a small function by hand, then find and fix the bug in a program you are given and write a function from a one-sentence specification. |

**Required materials**

- *Python 3*, Python Software Foundation — current release, python.org · open, free
- *An AI assistant of the learner's choice* · open, free
- *This Too Shall Pass (Rube Goldberg Machine)*, OK Go — official channel · open, free
- *Mountain Interval*, Robert Frost — Project Gutenberg #29345 · open, free
- *The Boston Cooking-School Cook Book*, Fannie Merritt Farmer — 1896, Project Gutenberg #65061 · open, free
- *The Iliad, Book 2*, Homer — Lectio edition · open, free
- *The Mythical Man-Month*, Frederick P. Brooks Jr. · public library, free

Required materials cost: nothing. Every item is open, borrowable from a public library, or provided in the room.
<!-- sdit:info:end -->

## Learning Outcomes

By the end of this course you can:

1. Write, run, and debug programs using variables, control flow, functions, and basic data structures. → *Workmanship*
2. Decompose a real problem into steps a machine can execute, and explain the decomposition. → *Judgment*
3. Direct AI tools to produce code — and verify, test, and correct what comes back. → *Command of Intelligence* · *Critical thinking*
4. Explain any line of your program, unassisted, out loud or in writing. → *Articulation · Command of Intelligence* · *Oral communication*
5. Ship a small working program and document what it does and why. → *Workmanship* · *Written communication*

*Each outcome maps to the five institutional outcomes (Judgment, Command of Intelligence, Workmanship, Articulation, Breadth of Mind) — the assessment spine of the degree and its accreditation evidence file.*

## The Made Thing

A small working program that does something you actually wanted done — written with AI in the loop and verified without it, shipped with a short write-up of what it does and how you know it works.

## How You're Assessed

- **Weekly builds** — small programs, graded on whether they work and whether you can explain them.
- **The shipped program**, demonstrated and defended.
- **Unassisted examinations in code** — reading, writing, and debugging with the tools closed. The institution certifies the human.
- Everything lands in your **portfolio**, reviewed against the five outcomes at the end-of-year gate.

<!-- sdit:weights:begin -->

| Component | Weight |
|---|---|
| Weekly builds, graded on whether they work and whether you can explain them | 25% |
| Verification log, kept from Day 2 | 10% |
| Unassisted examinations in code, Day 8 and Day 14 | 20% |
| The shipped program, write-up, and line-by-line defense | 45% |
| **Total** | **100%** |

Grades follow the scale in the [academic policies](/curriculum/policies.html#grading).
<!-- sdit:weights:end -->

## The Daily Path

One session per course day — each one built to look easy and pull you in: one thing to experience, one idea, one question to carry. The schedule below is generated from the course's own day files.

<!-- sdit:days:begin -->
The fifteen days below are the open spine of the course, about ten minutes each. The hours in Course Information are the course.

### Day 01 — The Very Fast, Very Literal Apprentice

Ten minutes. One machine made of junk, one idea, one question. You will not install anything today.

[Begin Day 01 →](day-01.html)

### Day 02 — The First Program Was Written by Hand

Publishes Monday, 4 January 2027.

### Day 03 — A Name for a Thing

Publishes Monday, 11 January 2027.

### Day 04 — Again, Again, Until

Publishes Monday, 18 January 2027.

### Day 05 — If It's Raining

Publishes Monday, 25 January 2027.

### Day 06 — Give the Move a Name

Publishes Monday, 1 February 2027.

### Day 07 — Where the Bug Was

Publishes Monday, 8 February 2027.

### Day 08 — Tools Closed

Publishes Monday, 15 February 2027.

### Day 09 — Lists of Things

Publishes Monday, 22 February 2027.

### Day 10 — Pairs of Things

Publishes Monday, 1 March 2027.

### Day 11 — What Did You Actually Want?

Publishes Monday, 8 March 2027.

### Day 12 — Prove It Works

Publishes Monday, 15 March 2027.

### Day 13 — Plausible Is Not True

Publishes Monday, 22 March 2027.

### Day 14 — Tools Closed, Again

Publishes Monday, 29 March 2027.

### Day 15 — Ship It

Publishes Monday, 5 April 2027.
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
