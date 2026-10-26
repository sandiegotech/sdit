---
id: engr-320
title: "ENGR 320 — Embedded Systems & Sensors"
course_code: ENGR 320
units: 4
thread: The Depths
status: syllabus
syllabus:
  level: upper
  prerequisites: [HUM 202, MATH 220, CS 220, RHET 210, WKSP 202, CS 120]
  corequisites: []
  method: [studio]
  hours:
    instruction: 1
    studio_or_lab: 6
    independent: 5
  materials:
    - {title: "Shore Stations Program description and daily temperature record", author: "Scripps Institution of Oceanography", access: open, cost: 0}
    - {title: "Datasheet for the course temperature sensor, read start to finish", author: "the sensor's manufacturer", access: open, cost: 0}
    - {title: "Tides & Currents, La Jolla station 9410230", author: "NOAA", edition: "station page and observed water-level plots", access: open, cost: 0}
    - {title: "Apollo 11 guidance computer source code", author: "Virtual AGC project", access: open, cost: 0}
    - {title: "A Walk Through Time", author: "NIST", access: open, cost: 0}
    - {title: "Voyager mission status", author: "NASA", access: open, cost: 0}
    - {title: "Argo program overview", author: "Argo program", access: open, cost: 0}
    - {title: "Account of the Mars Pathfinder priority-inversion bug", author: "Glenn Reeves", edition: "author's web page", access: open, cost: 0}
    - {title: "Moby-Dick, Chapters 118 and 125", author: "Herman Melville", edition: "Project Gutenberg", access: open, cost: 0}
    - {title: "Life on the Mississippi, Chapters 8-9", author: "Mark Twain", edition: "Project Gutenberg", access: open, cost: 0}
    - {title: "Seven Miles Down", author: "Jacques Piccard and Robert Dietz", access: library, cost: 0}
    - {title: "The Visual Display of Quantitative Information, chapter on data integrity", author: "Edward Tufte", access: library, cost: 0}
    - {title: "Oscilloscopes, bench supply, soldering station, seawater tank, pressure chamber, and O-rings", author: "San Diego Institute of Technology", access: provided, cost: 0, note: "Open learner: hobby microcontroller, waterproof probes, lunchbox, and a bucket of seawater."}
  assessment:
    - {component: "Weekly firmware, calibration, and bench-log work", weight: 20}
    - {component: "Three critiques: raw-trace bench, wet test, data against reference", weight: 15}
    - {component: "Unassisted examination: read the trace, diagnose the log, sketch the circuit", weight: 20}
    - {component: "The deployed instrument, data against reference, log, and autopsy, exhibited", weight: 45}
  exam: "Day 11, tools closed, ninety minutes by hand: convert a raw voltage trace to engineering units from a datasheet curve, diagnose the noise, dropout, and drift in a faulty log, and sketch the circuit that produced it."
  rubric: working-system
  core_competencies:
    quantitative-reasoning: D
    critical-thinking: D
  outcome_levels:
    craft: D
    intelligence: D
---

# ENGR 320 — Embedded Systems & Sensors

**The Depths** · 4 units · Semester 6 · Depth studio — Design & Engineering · the Crossing for others

## Overview

Computers that live in things — and in this curriculum, things that live in saltwater. Since 1916 someone has walked out on Scripps Pier nearly every day, lowered a bucket, and read a thermometer, and that bucket is one of the longest ocean records on Earth. In this studio you build an instrument and set it beside that record. The ocean is the examiner. Salt, pressure, fouling, cold, and the one gap you did not seal: it finds them all, and it does not grade on a curve.

The catalog says embedded computing: microcontrollers, firmware, sensors, signal acquisition. The room says: a computer the size of a stamp, two sensors you calibrated yourself, a clock you set and checked, a power budget written before the battery is bought, a watchdog, a sealed enclosure with every penetration listed, and forty-eight hours in the Pacific. Each week on the page is one idea and one thing to experience — the Moon lander's computer, a bathyscaphe that left San Diego for the deepest water on Earth, a tide gauge drawing a tsunami on paper, a rotted log-line parting under its first strain. Each week at the bench you solder, flash, seal, and test.

This is a depth studio: a room with oscilloscopes, a tank of seawater, a shelf of flooded housings, and a master who has built instruments for the ocean and lost one to it. The page is the brief. The course ends in a made thing — an instrument that went in, came back, and brought data you can defend against a hundred-year record.

## The Two Registers

- **Catalog register:** Embedded computing — microcontrollers, firmware, sensors, signal acquisition.
- **Teaching frame:** Firmware, ocean sensors, instruments that survive saltwater.

## Course Information

<!-- sdit:info:begin -->
| | |
|---|---|
| Catalog number | ENGR 320 — Embedded Systems & Sensors |
| Units | 4 semester units · 180 hours of work over 15 weeks |
| Each week | 1 h instruction · 6 h studio or laboratory · 5 h independent work |
| Level | Upper division |
| Offered | Semester 6 · Year 3 · Spring |
| Prerequisites | [HUM 202](/courses/HUM-202/index.html), [MATH 220](/courses/MATH-220/index.html), [CS 220](/courses/CS-220/index.html), [RHET 210](/courses/RHET-210/index.html), [WKSP 202](/courses/WKSP-202/index.html), [CS 120](/courses/CS-120/index.html) |
| Corequisites | None |
| Instructional method | Studio |
| Instructor | A practitioner-scholar with a body of work in the field: a terminal degree, or equivalent professional standing documented under the Institute's rubric (The Degree, section 9). |
| Rubric | [The working system (Computation and Engineering)](/curriculum/rubrics.html#working-system) |
| Core competencies | Quantitative reasoning (developed) · Critical thinking (developed) |
| Unassisted examination | Day 11, tools closed, ninety minutes by hand: convert a raw voltage trace to engineering units from a datasheet curve, diagnose the noise, dropout, and drift in a faulty log, and sketch the circuit that produced it. |

**Required materials**

- *Shore Stations Program description and daily temperature record*, Scripps Institution of Oceanography · open, free
- *Datasheet for the course temperature sensor, read start to finish*, the sensor's manufacturer · open, free
- *Tides & Currents, La Jolla station 9410230*, NOAA — station page and observed water-level plots · open, free
- *Apollo 11 guidance computer source code*, Virtual AGC project · open, free
- *A Walk Through Time*, NIST · open, free
- *Voyager mission status*, NASA · open, free
- *Argo program overview*, Argo program · open, free
- *Account of the Mars Pathfinder priority-inversion bug*, Glenn Reeves — author's web page · open, free
- *Moby-Dick, Chapters 118 and 125*, Herman Melville — Project Gutenberg · open, free
- *Life on the Mississippi, Chapters 8-9*, Mark Twain — Project Gutenberg · open, free
- *Seven Miles Down*, Jacques Piccard and Robert Dietz · public library, free
- *The Visual Display of Quantitative Information, chapter on data integrity*, Edward Tufte · public library, free
- *Oscilloscopes, bench supply, soldering station, seawater tank, pressure chamber, and O-rings*, San Diego Institute of Technology · provided in the room; open learner: hobby microcontroller, waterproof probes, lunchbox, and a bucket of seawater

Required materials cost: nothing. Every item is open, borrowable from a public library, or provided in the room.
<!-- sdit:info:end -->

## Learning Outcomes

By the end of this course you can:

1. Write firmware for a microcontroller with no operating system beneath it — sensing, logging, sleeping, and recovering from a crash by watchdog — and verify it against the hardware. → *Workmanship*
2. Calibrate a sensor against a known, convert its raw signal to engineering units from the datasheet's curve, and state the measurement's uncertainty. → *Command of Intelligence* · *Quantitative reasoning*
3. Design an instrument for a hostile environment: a power budget, a timekeeping plan, a telemetry plan that never depends on the link, and a sealed enclosure with every penetration accounted for. → *Workmanship*
4. Deploy, retrieve, and clean field data honestly — every cleaning step stated — and compare it against a reference record, explaining the differences. → *Command of Intelligence*
5. Read a raw trace and a faulty log by hand, diagnose noise, dropout, and drift, and sketch the circuit that produced them — with the tools closed. → *Command of Intelligence · Workmanship* · *Critical thinking*

*Each outcome maps to the five institutional outcomes (Judgment, Command of Intelligence, Workmanship, Articulation, Breadth of Mind) — the assessment spine of the degree and its accreditation evidence file.*

## The Made Thing

A working instrument deployed in the field, gathering real data in a hostile environment. A microcontroller, at least two calibrated sensors, a clock, storage, power for forty-eight hours, and a sealed enclosure — deployed in saltwater off Scripps Pier, in Mission Bay, in a tide pool, or in a bucket of seawater on a balcony — and retrieved with data that is plotted against the NOAA La Jolla tide gauge and the Scripps Pier temperature record. On the last day the instrument sits open on the table beside its data, the reference, the deployment log, and the autopsy: what leaked, what drifted, what lied. It enters your portfolio for review at the annual gate.

## How You're Assessed

- **The instrument**, judged by whether it went in, stayed in, came out, and brought data back.
- **The data**, judged against the reference record hour by hour, with every cleaning step stated under the plot.
- **The deployment log and the autopsy**, judged by their honesty about what failed and why.
- **Three studio critiques** — Day 5 (the bench, raw traces only), Day 10 (the wet test, the tank opened in front of the room), Day 14 (every trace beside the reference). The raw trace is always shown first.
- **An unassisted examination** on Day 11, tools closed: given a raw voltage trace, a datasheet, and a faulty log, you convert, diagnose, and sketch the circuit by hand. The dashboard is downstream of everything; the institution certifies the human who can read what is upstream.
- Everything lands in your **portfolio**, reviewed against the five outcomes at the end-of-year gate.

<!-- sdit:weights:begin -->

| Component | Weight |
|---|---|
| Weekly firmware, calibration, and bench-log work | 20% |
| Three critiques: raw-trace bench, wet test, data against reference | 15% |
| Unassisted examination: read the trace, diagnose the log, sketch the circuit | 20% |
| The deployed instrument, data against reference, log, and autopsy, exhibited | 45% |
| **Total** | **100%** |

Grades follow the scale in the [academic policies](/curriculum/policies.html#grading).
<!-- sdit:weights:end -->

## The Daily Path

One session per course day — each one built to look easy and pull you in: one thing to experience, one idea, one question to carry. The schedule below is generated from the course's own day files.

<!-- sdit:days:begin -->
The fifteen days below are the open spine of the course, about ten minutes each. The hours in Course Information are the course.

### Day 01 — A Bucket on a Rope

Publishes Monday, 5 June 2028.

### Day 02 — A Computer the Size of a Stamp

Publishes Monday, 12 June 2028.

### Day 03 — What a Sensor Actually Returns

Publishes Monday, 19 June 2028.

### Day 04 — Seal It

Publishes Monday, 26 June 2028.

### Day 05 — Show the Raw Trace

Publishes Monday, 3 July 2028.

### Day 06 — Time Is the Hardest Sensor

Publishes Monday, 10 July 2028.

### Day 07 — Power Is the Budget

Publishes Monday, 17 July 2028.

### Day 08 — Radio Is a Sensor Pointed at Air

Publishes Monday, 24 July 2028.

### Day 09 — Assume It Will Crash

Publishes Monday, 31 July 2028.

### Day 10 — The Line Had Rotted

Publishes Monday, 7 August 2028.

### Day 11 — Read the Trace

Publishes Monday, 14 August 2028.

### Day 12 — Deploy Day

Publishes Monday, 21 August 2028.

### Day 13 — The Data Comes Home Dirty

Publishes Monday, 28 August 2028.

### Day 14 — Read the River

Publishes Monday, 4 September 2028.

### Day 15 — Your Number Enters the Record

Publishes Monday, 11 September 2028.
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
