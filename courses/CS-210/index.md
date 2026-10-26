---
id: cs-210
title: "CS 210 — Data Structures & Algorithms"
course_code: CS 210
units: 4
thread: Computation & Intelligent Systems
status: syllabus
syllabus:
  level: lower
  prerequisites: [CS 120]
  corequisites: []
  method: [lecture, laboratory]
  hours:
    instruction: 2
    studio_or_lab: 3
    independent: 7
  materials:
    - {title: "Python 3, with its cProfile profiler", author: "Python Software Foundation", edition: "current release, python.org", access: open, cost: 0}
    - {title: "An AI assistant of the learner's choice", access: open, cost: 0}
    - {title: "Coastal Data Information Program buoy archive", author: "Scripps Institution of Oceanography", edition: "cdip.ucsd.edu, text download", access: open, cost: 0}
    - {title: "San Diego MTS transit feed (GTFS)", author: "San Diego Metropolitan Transit System", edition: "open data", access: open, cost: 0}
    - {title: "Mathematical Recreations and Essays", author: "W. W. Rouse Ball", edition: "1892, Project Gutenberg #26839", access: open, cost: 0}
    - {title: "The First Six Books of the Elements of Euclid", author: "Oliver Byrne", edition: "1847, Wikimedia Commons scan", access: open, cost: 0}
    - {title: "The Thirteen Books of Euclid's Elements, vol. 2", author: "Thomas L. Heath", edition: "1908 translation, Internet Archive", access: open, cost: 0}
  assessment:
    - {component: "Weekly measured builds, timed on the same inputs", weight: 20}
    - {component: "Benchmark log of the assistant's speed claims, measured and kept", weight: 15}
    - {component: "Unassisted examinations on paper, Day 8 and Day 14", weight: 20}
    - {component: "The measurably faster program, chart, and written proof, defended live", weight: 45}
  exam: "Day 8 and Day 14, tools closed, on paper: state how three code fragments grow with input size, trace binary search by hand, then write binary search from memory, read a profiler output, and give the growth-rate argument for one sort."
  rubric: working-system
  core_competencies:
    quantitative-reasoning: D
    critical-thinking: D
    oral-communication: D
  outcome_levels:
    intelligence: D
    judgment: D
---

# CS 210 — Data Structures & Algorithms

**Computation & Intelligent Systems** · 4 units · Semester 3 · Required core — everyone takes it

## Overview

The difference between code that works and code that works at scale is the subject of this course, and it is a difference you can measure. Lists, stacks, queues, hash tables, trees, graphs; searching and sorting; how running time grows when the input doubles — the classic course, with every structure arriving as a physical thing first. A phone book is a binary search. The border crossing at San Ysidro is a queue. A card catalog is a hash table. Euler's map of Königsberg is a graph. Only after you have measured the shape of a cost on your own data does the notation for it arrive.

The teaching frame is Making Things Fast. The first tool you build is a stopwatch around a function, and you use it every week. You choose a real dataset — the Institute's suggestion is decades of wave measurements from the Scripps buoys off Point Loma and Torrey Pines — write the honest slow version of a program that answers a question about it, and then make it fast, with the chart and the proof to show why. The AI assistant is open throughout; it is good at proposing structures and confident about running times it has never measured. Every claim of speed in this course is a measurement, and every measurement is yours.

One day a week, about ten minutes a sitting, and it ends in a made thing: a program measurably faster than it was, defended with a stopwatch and a proof.

## The Two Registers

- **Catalog register:** Data structures, algorithm design and analysis, complexity.
- **Teaching frame:** Making Things Fast — the classic course, taught against real performance problems you can measure.

## Course Information

<!-- sdit:info:begin -->
| | |
|---|---|
| Catalog number | CS 210 — Data Structures & Algorithms |
| Units | 4 semester units · 180 hours of work over 15 weeks |
| Each week | 2 h instruction · 3 h studio or laboratory · 7 h independent work |
| Level | Lower division |
| Offered | Semester 3 · Year 2 · Fall |
| Prerequisites | [CS 120](/courses/CS-120/index.html) |
| Corequisites | None |
| Instructional method | Lecture, Laboratory |
| Instructor | A practitioner-scholar with a body of work in the field: a terminal degree, or equivalent professional standing documented under the Institute's rubric (The Degree, section 9). |
| Rubric | [The working system (Computation and Engineering)](/curriculum/rubrics.html#working-system) |
| Core competencies | Oral communication (developed) · Quantitative reasoning (developed) · Critical thinking (developed) |
| Unassisted examination | Day 8 and Day 14, tools closed, on paper: state how three code fragments grow with input size, trace binary search by hand, then write binary search from memory, read a profiler output, and give the growth-rate argument for one sort. |

**Required materials**

- *Python 3, with its cProfile profiler*, Python Software Foundation — current release, python.org · open, free
- *An AI assistant of the learner's choice* · open, free
- *Coastal Data Information Program buoy archive*, Scripps Institution of Oceanography — cdip.ucsd.edu, text download · open, free
- *San Diego MTS transit feed (GTFS)*, San Diego Metropolitan Transit System — open data · open, free
- *Mathematical Recreations and Essays*, W. W. Rouse Ball — 1892, Project Gutenberg #26839 · open, free
- *The First Six Books of the Elements of Euclid*, Oliver Byrne — 1847, Wikimedia Commons scan · open, free
- *The Thirteen Books of Euclid's Elements, vol. 2*, Thomas L. Heath — 1908 translation, Internet Archive · open, free

Required materials cost: nothing. Every item is open, borrowable from a public library, or provided in the room.
<!-- sdit:info:end -->

## Learning Outcomes

By the end of this course you can:

1. Choose and implement the right data structure — list, stack, queue, hash table, tree, or graph — for a real problem, and say why it is the right one. → *Command of Intelligence*
2. Measure a program's running time against input size, read the growth rate off the measurements, and name it in standard notation. → *Judgment* · *Quantitative reasoning*
3. Write binary search and a divide-and-conquer sort from memory, correctly, and argue their running times, with the tools closed. → *Judgment* · *Critical thinking*
4. Profile a program, redesign it, and benchmark the result — including testing the assistant's performance claims and rejecting the ones that do not hold. → *Command of Intelligence*
5. Defend a speedup to a skeptic with a live demonstration, a chart, and a written proof. → *Judgment · Command of Intelligence* · *Oral communication*

*Each outcome maps to the five institutional outcomes (Judgment, Command of Intelligence, Workmanship, Articulation, Breadth of Mind) — the assessment spine of the degree and its accreditation evidence file.*

## The Made Thing

A measurably faster program — profiled, redesigned, and benchmarked, with the analysis to show why. Five things ship together: the slow version, timed; the fast version, timed on the same inputs; a chart of running time against input size for both; a written argument in standard notation for why the growth rates differ; and the profile before and after. It is defended by running both versions live on the largest input, and by questioning on the proof. It enters your portfolio and is reviewed at the annual gate.

## How You're Assessed

- **Weekly measurements** — each structure implemented, timed on your own data, and explained.
- **The faster program**, demonstrated live and defended with its chart and proof.
- **Unassisted examinations on paper** — stating growth rates, tracing and writing binary search, reading a profiler's output. The institution certifies the human, so part of this course happens with the tools closed.
- Everything lands in your **portfolio**, reviewed against the five outcomes at the end-of-year gate.

<!-- sdit:weights:begin -->

| Component | Weight |
|---|---|
| Weekly measured builds, timed on the same inputs | 20% |
| Benchmark log of the assistant's speed claims, measured and kept | 15% |
| Unassisted examinations on paper, Day 8 and Day 14 | 20% |
| The measurably faster program, chart, and written proof, defended live | 45% |
| **Total** | **100%** |

Grades follow the scale in the [academic policies](/curriculum/policies.html#grading).
<!-- sdit:weights:end -->

## The Daily Path

One session per course day — each one built to look easy and pull you in: one thing to experience, one idea, one question to carry. The schedule below is generated from the course's own day files.

<!-- sdit:days:begin -->
The fifteen days below are the open spine of the course, about ten minutes each. The hours in Course Information are the course.

### Day 01 — Fast Is a Measurement

Publishes Monday, 26 July 2027.

### Day 02 — Twice the Input, How Much Longer?

Publishes Monday, 2 August 2027.

### Day 03 — Half the Phone Book

Publishes Monday, 9 August 2027.

### Day 04 — Lines and Stacks

Publishes Monday, 16 August 2027.

### Day 05 — The Baseline

Publishes Monday, 23 August 2027.

### Day 06 — A Number for Every Name

Publishes Monday, 30 August 2027.

### Day 07 — Sorting on the Floor

Publishes Monday, 6 September 2027.

### Day 08 — Tools Closed: Say How Fast

Publishes Monday, 13 September 2027.

### Day 09 — Trees

Publishes Monday, 20 September 2027.

### Day 10 — The Redesign

Publishes Monday, 27 September 2027.

### Day 11 — Maps Are Graphs

Publishes Monday, 4 October 2027.

### Day 12 — Memory Is Also Time

Publishes Monday, 11 October 2027.

### Day 13 — Measure, Don't Trust

Publishes Monday, 18 October 2027.

### Day 14 — Tools Closed: Prove It

Publishes Monday, 25 October 2027.

### Day 15 — Show the Speedup

Publishes Monday, 1 November 2027.
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
