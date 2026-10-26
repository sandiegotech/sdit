---
id: cs-120
title: "CS 120 — Computational Thinking & Systems"
course_code: CS 120
units: 4
thread: Computation & Intelligent Systems
status: syllabus
syllabus:
  level: lower
  prerequisites: [CS 110]
  corequisites: []
  method: [lecture, laboratory]
  hours:
    instruction: 2
    studio_or_lab: 3
    independent: 7
  materials:
    - {title: "Nand2Tetris web IDE", author: "Nisan and Schocken (nand2tetris.org)", edition: "browser-based, MIT-licensed, no account", access: open, cost: 0}
    - {title: "The Elements of Computing Systems, Chapters 1 and 4 (free chapters)", author: "Noam Nisan and Shimon Schocken", edition: "posted free at nand2tetris.org", access: open, cost: 0}
    - {title: "An AI assistant of the learner's choice", access: open, cost: 0}
    - {title: "Building an 8-bit computer on a breadboard (video series)", author: "Ben Eater", edition: "official YouTube channel", access: open, cost: 0}
    - {title: "The self-organizing computer course (TED, 2012)", author: "Shimon Schocken", edition: "TED official channel", access: open, cost: 0}
    - {title: "An Investigation of the Laws of Thought", author: "George Boole", edition: "Project Gutenberg #15114", access: open, cost: 0}
  assessment:
    - {component: "Weekly builds: chips written, tested, and wired from the ones before", weight: 25}
    - {component: "Unassisted examinations on paper, Day 8 and Day 14", weight: 20}
    - {component: "The computer and its program, demonstrated and defended chip by chip", weight: 45}
    - {component: "One-page account of each layer, in your own words", weight: 10}
  exam: "Day 8 and Day 14, tools closed, on paper: draw a full adder from gates, add four-bit numbers in two's complement, explain why a latch remembers, then translate five lines of Hack assembly to binary, trace them, and explain what the operating system does between a double-click and an open file."
  rubric: working-system
  core_competencies:
    quantitative-reasoning: I
    critical-thinking: I
    oral-communication: I
  outcome_levels:
    intelligence: I
    judgment: I
---

# CS 120 — Computational Thinking & Systems

**Computation & Intelligent Systems** · 4 units · Semester 2 · Required core — everyone takes it

## Overview

There is no magic anywhere in the stack. Between your finger and the page you are reading there is a transistor, a gate, an adder, a register, a processor, an operating system, and a network — and every one of them was built by a person out of the layer below. This course walks that stack from the bottom, and you build each layer before you move up: a switch that flips a switch, then NAND, then everything from NAND, then arithmetic, memory, a clock, a machine language, a CPU. By the end, the computer that runs your program is one you understand all the way down.

The teaching frame is How Machines Think. The default build is simulated, in a free browser-based hardware simulator, chip by chip, each one tested before the next is wired from it; a breadboard door stays open every day for those who want to hold the gates in their hands. The AI assistant is open from Day 2 — it will draft a chip for you — and the rule of the course is that the test script, not the assistant, says whether a chip works. You learn to make the assistant's chip fail before you trust it, and by Day 12 you can say where in the stack the assistant itself lives.

One day a week, about ten minutes a sitting, and the course ends the way every SDIT course ends: in a made thing. Yours is a computer, built upward from gates, running a program you wrote.

## The Two Registers

- **Catalog register:** Computer organization and systems — logic gates, memory, processors, operating systems, networks.
- **Teaching frame:** How Machines Think — how machines actually work, from logic gates up, every layer explained by building it.

## Course Information

<!-- sdit:info:begin -->
| | |
|---|---|
| Catalog number | CS 120 — Computational Thinking & Systems |
| Units | 4 semester units · 180 hours of work over 15 weeks |
| Each week | 2 h instruction · 3 h studio or laboratory · 7 h independent work |
| Level | Lower division |
| Offered | Semester 2 · Year 1 · Spring |
| Prerequisites | [CS 110](/courses/CS-110/index.html) |
| Corequisites | None |
| Instructional method | Lecture, Laboratory |
| Instructor | A practitioner-scholar with a body of work in the field: a terminal degree, or equivalent professional standing documented under the Institute's rubric (The Degree, section 9). |
| Rubric | [The working system (Computation and Engineering)](/curriculum/rubrics.html#working-system) |
| Core competencies | Oral communication (introduced) · Quantitative reasoning (introduced) · Critical thinking (introduced) |
| Unassisted examination | Day 8 and Day 14, tools closed, on paper: draw a full adder from gates, add four-bit numbers in two's complement, explain why a latch remembers, then translate five lines of Hack assembly to binary, trace them, and explain what the operating system does between a double-click and an open file. |

**Required materials**

- *Nand2Tetris web IDE*, Nisan and Schocken (nand2tetris.org) — browser-based, MIT-licensed, no account · open, free
- *The Elements of Computing Systems, Chapters 1 and 4 (free chapters)*, Noam Nisan and Shimon Schocken — posted free at nand2tetris.org · open, free
- *An AI assistant of the learner's choice* · open, free
- *Building an 8-bit computer on a breadboard (video series)*, Ben Eater — official YouTube channel · open, free
- *The self-organizing computer course (TED, 2012)*, Shimon Schocken — TED official channel · open, free
- *An Investigation of the Laws of Thought*, George Boole — Project Gutenberg #15114 · open, free

Required materials cost: nothing. Every item is open, borrowable from a public library, or provided in the room.
<!-- sdit:info:end -->

## Learning Outcomes

By the end of this course you can:

1. Build, from a single gate type, the combinational and sequential chips of a working computer — gates, adders, an ALU, registers, RAM, a program counter, a CPU — and test each one. → *Command of Intelligence*
2. Add and subtract in binary and two's complement by hand, and explain why a latch remembers, with the tools closed. → *Judgment* · *Quantitative reasoning*
3. Write a program in a machine language, assemble it, and trace its execution tick by tick through the processor you built. → *Command of Intelligence*
4. Explain what an operating system and a network do between a program and the hardware, and place the AI assistant you use within that stack. → *Judgment* · *Critical thinking*
5. Defend any chip in your computer by explaining it from the chips below it, on request. → *Command of Intelligence · Judgment* · *Oral communication*

*Each outcome maps to the five institutional outcomes (Judgment, Command of Intelligence, Workmanship, Articulation, Breadth of Mind) — the assessment spine of the degree and its accreditation evidence file.*

## The Made Thing

A working computer built upward from gates — simulated or breadboarded — that runs a program you wrote. Every chip passes its test; the program is written by hand in the machine's own language; the whole thing ships with a one-page account of each layer in your own words. It is exhibited by running it in front of someone who picks any chip and asks you to explain it from the ones below. It enters your portfolio and is reviewed at the annual gate.

## How You're Assessed

- **Weekly builds** — chips written, tested, and wired from the ones before; graded on whether they pass and whether you can explain them.
- **The computer and its program**, demonstrated and defended chip by chip.
- **Unassisted examinations on paper** — drawing a full adder, adding in two's complement, tracing a machine-language program by hand. The institution certifies the human, so part of this course happens with the tools closed.
- Everything lands in your **portfolio**, reviewed against the five outcomes at the end-of-year gate.

<!-- sdit:weights:begin -->

| Component | Weight |
|---|---|
| Weekly builds: chips written, tested, and wired from the ones before | 25% |
| Unassisted examinations on paper, Day 8 and Day 14 | 20% |
| The computer and its program, demonstrated and defended chip by chip | 45% |
| One-page account of each layer, in your own words | 10% |
| **Total** | **100%** |

Grades follow the scale in the [academic policies](/curriculum/policies.html#grading).
<!-- sdit:weights:end -->

## The Daily Path

One session per course day — each one built to look easy and pull you in: one thing to experience, one idea, one question to carry. The schedule below is generated from the course's own day files.

<!-- sdit:days:begin -->
The fifteen days below are the open spine of the course, about ten minutes each. The hours in Course Information are the course.

### Day 01 — No Magic Anywhere

Publishes Monday, 12 April 2027.

### Day 02 — A Switch That Flips a Switch

Publishes Monday, 19 April 2027.

### Day 03 — Everything from NAND

Publishes Monday, 26 April 2027.

### Day 04 — Adding with Switches

Publishes Monday, 3 May 2027.

### Day 05 — Negative Numbers and One Clever Box

Publishes Monday, 10 May 2027.

### Day 06 — Remembering Is a Loop

Publishes Monday, 17 May 2027.

### Day 07 — Numbered Houses

Publishes Monday, 24 May 2027.

### Day 08 — Tools Closed: Draw It

Publishes Monday, 31 May 2027.

### Day 09 — The Heartbeat

Publishes Monday, 7 June 2027.

### Day 10 — Holes in a Card Are an Order

Publishes Monday, 14 June 2027.

### Day 11 — Wiring the CPU

Publishes Monday, 21 June 2027.

### Day 12 — The Program That Runs the Programs

Publishes Monday, 28 June 2027.

### Day 13 — Packets Across the Sea

Publishes Monday, 5 July 2027.

### Day 14 — Tools Closed: Trace It

Publishes Monday, 12 July 2027.

### Day 15 — The Oldest Computer

Publishes Monday, 19 July 2027.
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
