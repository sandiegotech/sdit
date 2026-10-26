---
id: cs-220
title: "CS 220 — Machine Learning I"
course_code: CS 220
units: 4
thread: Computation & Intelligent Systems
status: syllabus
syllabus:
  level: lower
  prerequisites: [CS 210, MATH 210]
  corequisites: []
  method: [lecture, laboratory]
  hours:
    instruction: 2
    studio_or_lab: 3
    independent: 7
  materials:
    - {title: "Python 3", author: "Python Software Foundation", edition: "current release, python.org", access: open, cost: 0}
    - {title: "NumPy", author: "NumPy developers", edition: "open-source array library", access: open, cost: 0}
    - {title: "An AI assistant of the learner's choice", access: open, cost: 0}
    - {title: "Coastal Data Information Program buoy archive", author: "Scripps Institution of Oceanography", edition: "cdip.ucsd.edu, text download", access: open, cost: 0}
    - {title: "NOAA weather and ocean observations", author: "National Oceanic and Atmospheric Administration", edition: "public data", access: open, cost: 0}
    - {title: "An Enquiry Concerning Human Understanding", author: "David Hume", edition: "Project Gutenberg #9662", access: open, cost: 0}
    - {title: "Eugene Onegin", author: "Alexander Pushkin", edition: "Spalding translation, Project Gutenberg #23997", access: open, cost: 0}
  assessment:
    - {component: "Weekly data log and gradient-check notebook", weight: 20}
    - {component: "Unassisted examinations on paper, Day 8 and Day 14", weight: 20}
    - {component: "The data, model, evaluation, and failure report, defended on a new example", weight: 45}
    - {component: "Weekly written answers on what the model can and cannot know", weight: 15}
  exam: "Day 8 and Day 14, tools closed, on paper: compute a squared-error loss and take one gradient step by hand, explain why a model must be tested on unseen data, then read a confusion matrix, sketch where the gradient flows in a two-layer network, and say what your own model cannot know."
  rubric: working-system
  core_competencies:
    quantitative-reasoning: D
    critical-thinking: D
    information-literacy: D
  outcome_levels:
    intelligence: D
    judgment: D
---

# CS 220 — Machine Learning I

**Computation & Intelligent Systems** · 4 units · Semester 4 · Required core — everyone takes it

## Overview

The machine that learned to finish your sentences is not a mystery. It is matrices, gradients, and data — the linear algebra you did in MATH 210, the derivative from MATH 110, and a great deal of text. This course builds a small one from scratch so the big ones stop being magic. A model is a guess with knobs; training is turning the knobs until the guesses stop being wrong; evaluation is finding out, honestly, where they are still wrong. Every idea arrives physically first — a ruler through a scatter of points, a hot-and-cold game down a hillside, a horse that learned to read its examiner's face — and only then as notation.

The teaching frame is Teaching Machines. The data is yours: starting in the second week you gather and label it — one honest observation a day for the whole course, or a few hundred photographs or messages labelled in an afternoon. The gradient is yours too: plain code, no training library, so every number the model learns passed through lines you can point to. The AI assistant is open throughout, and the course's method for checking its code is the same method for checking your own — perturb a weight and see whether the loss moves the way the gradient said. By the last week you build the smallest version of the assistant itself and watch it produce almost-English.

One page a week opens the day, about ten minutes to read, and it ends in a made thing: a model you trained on data you gathered, with a report that says exactly where it fails and who it fails.

## The Two Registers

- **Catalog register:** Foundations of machine learning — models, training, evaluation, limits.
- **Teaching frame:** Teaching Machines — what a model is, how it trains, what it can and cannot know.

## Course Information

<!-- sdit:info:begin -->
| | |
|---|---|
| Catalog number | CS 220 — Machine Learning I |
| Units | 4 semester units · 180 hours of work over 15 weeks |
| Each week | 2 h instruction · 3 h studio or laboratory · 7 h independent work |
| Level | Lower division |
| Offered | Semester 4 · Year 2 · Spring |
| Prerequisites | [CS 210](/courses/CS-210/index.html), [MATH 210](/courses/MATH-210/index.html) |
| Corequisites | None |
| Instructional method | Lecture, Laboratory |
| Instructor | A practitioner-scholar with a body of work in the field: a terminal degree, or equivalent professional standing documented under the Institute's rubric (The Degree, section 9). |
| Rubric | [The working system (Computation and Engineering)](/curriculum/rubrics.html#working-system) |
| Core competencies | Quantitative reasoning (developed) · Information literacy (developed) · Critical thinking (developed) |
| Unassisted examination | Day 8 and Day 14, tools closed, on paper: compute a squared-error loss and take one gradient step by hand, explain why a model must be tested on unseen data, then read a confusion matrix, sketch where the gradient flows in a two-layer network, and say what your own model cannot know. |

**Required materials**

- *Python 3*, Python Software Foundation — current release, python.org · open, free
- *NumPy*, NumPy developers — open-source array library · open, free
- *An AI assistant of the learner's choice* · open, free
- *Coastal Data Information Program buoy archive*, Scripps Institution of Oceanography — cdip.ucsd.edu, text download · open, free
- *NOAA weather and ocean observations*, National Oceanic and Atmospheric Administration — public data · open, free
- *An Enquiry Concerning Human Understanding*, David Hume — Project Gutenberg #9662 · open, free
- *Eugene Onegin*, Alexander Pushkin — Spalding translation, Project Gutenberg #23997 · open, free

Required materials cost: nothing. Every item is open, borrowable from a public library, or provided in the room.
<!-- sdit:info:end -->

## Learning Outcomes

By the end of this course you can:

1. Gather and label a dataset of your own, and account for how it was collected and what it leaves out. → *Judgment* · *Information literacy*
2. Implement gradient descent and a small neural network from scratch, and verify every gradient numerically. → *Command of Intelligence*
3. Compute a loss and one gradient step by hand, and explain why a model must be tested on data it has never seen, with the tools closed. → *Judgment* · *Quantitative reasoning*
4. Evaluate a model with held-out data and a confusion matrix, examine each failure, and say which errors matter and to whom. → *Judgment* · *Critical thinking*
5. Explain what the AI assistant you use is — a model of the same kind, at scale — and what that implies about trusting its explanations. → *Command of Intelligence*

*Each outcome maps to the five institutional outcomes (Judgment, Command of Intelligence, Workmanship, Articulation, Breadth of Mind) — the assessment spine of the degree and its accreditation evidence file.*

## The Made Thing

A model trained from scratch on data you gathered — with an honest evaluation of where it fails. Four things ship together: the data and an account of how it was gathered; the model, its training code, and its loss curve; the evaluation on held-out data, with every wrong prediction examined; and the failure report — what the model cannot know, who it fails, and what would have to be true of the data for it to be trusted. It is defended by predicting on a new example the examiner brings, and by questioning on the report. It enters your portfolio and is reviewed at the annual gate.

## How You're Assessed

- **Weekly builds** — the data log, the first fit, the network, the evaluation — each one run on your own data and explained.
- **The model and its failure report**, demonstrated on a new example and defended.
- **Unassisted examinations on paper** — one gradient step by hand, reading a confusion matrix, saying what a model cannot know. The institution certifies the human, so part of this course happens with the tools closed.
- Everything lands in your **portfolio**, reviewed against the five outcomes at the end-of-year gate.

<!-- sdit:weights:begin -->

| Component | Weight |
|---|---|
| Weekly data log and gradient-check notebook | 20% |
| Unassisted examinations on paper, Day 8 and Day 14 | 20% |
| The data, model, evaluation, and failure report, defended on a new example | 45% |
| Weekly written answers on what the model can and cannot know | 15% |
| **Total** | **100%** |

Grades follow the scale in the [academic policies](/curriculum/policies.html#grading).
<!-- sdit:weights:end -->

## The Daily Path

One session per course day — each one built to look easy and pull you in: one thing to experience, one idea, one question to carry. The schedule below is generated from the course's own day files.

<!-- sdit:days:begin -->
The fifteen days below are the course's spine: one page a week, about ten minutes to read, each opening that week's work. The hours in Course Information are the course.

### Day 01 — A Line Through the Points

Publishes Monday, 8 November 2027.

### Day 02 — One Honest Measurement a Day

Publishes Monday, 15 November 2027.

### Day 03 — Warmer, Colder

Publishes Monday, 22 November 2027.

### Day 04 — What the Model Is Allowed to See

Publishes Monday, 29 November 2027.

### Day 05 — The First Fit

Publishes Monday, 6 December 2027.

### Day 06 — The Horse That Learned the Examiner

Publishes Monday, 13 December 2027.

### Day 07 — A Neuron Is a Weighted Vote

Publishes Monday, 20 December 2027.

### Day 08 — Tools Closed: One Step by Hand

Publishes Monday, 27 December 2027.

### Day 09 — Stack the Votes

Publishes Monday, 3 January 2028.

### Day 10 — Four Kinds of Right and Wrong

Publishes Monday, 10 January 2028.

### Day 11 — What It Cannot Know

Publishes Monday, 17 January 2028.

### Day 12 — Look at Every One

Publishes Monday, 24 January 2028.

### Day 13 — The Big Ones Are the Same Thing

Publishes Monday, 31 January 2028.

### Day 14 — Tools Closed: Read the Matrix

Publishes Monday, 7 February 2028.

### Day 15 — Eight Minutes of Arc

Publishes Monday, 14 February 2028.
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
