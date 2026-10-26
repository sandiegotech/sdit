---
id: cs-220
title: "CS 220 — Machine Learning I"
course_code: CS 220
units: 4
thread: Computation & Intelligent Systems
status: syllabus
---

# CS 220 — Machine Learning I

**Computation & Intelligent Systems** · 4 units · Semester 4 · Required core — everyone takes it

## Overview

The machine that learned to finish your sentences is not a mystery. It is matrices, gradients, and data — the linear algebra you did in MATH 210, the derivative from MATH 110, and a great deal of text. This course builds a small one from scratch so the big ones stop being magic. A model is a guess with knobs; training is turning the knobs until the guesses stop being wrong; evaluation is finding out, honestly, where they are still wrong. Every idea arrives physically first — a ruler through a scatter of points, a hot-and-cold game down a hillside, a horse that learned to read its examiner's face — and only then as notation.

The teaching frame is Teaching Machines. The data is yours: starting in the second week you gather and label it — one honest observation a day for the whole course, or a few hundred photographs or messages labelled in an afternoon. The gradient is yours too: plain code, no training library, so every number the model learns passed through lines you can point to. The AI assistant is open throughout, and the course's method for checking its code is the same method for checking your own — perturb a weight and see whether the loss moves the way the gradient said. By the last week you build the smallest version of the assistant itself and watch it produce almost-English.

One day a week, about ten minutes a sitting, and it ends in a made thing: a model you trained on data you gathered, with a report that says exactly where it fails and who it fails.

## The Two Registers

- **Catalog register:** Foundations of machine learning — models, training, evaluation, limits.
- **Teaching frame:** Teaching Machines — what a model is, how it trains, what it can and cannot know.

## Learning Outcomes

By the end of this course you can:

1. Gather and label a dataset of your own, and account for how it was collected and what it leaves out. → *Judgment*
2. Implement gradient descent and a small neural network from scratch, and verify every gradient numerically. → *Command of Intelligence*
3. Compute a loss and one gradient step by hand, and explain why a model must be tested on data it has never seen, with the tools closed. → *Judgment*
4. Evaluate a model with held-out data and a confusion matrix, examine each failure, and say which errors matter and to whom. → *Judgment*
5. Explain what the AI assistant you use is — a model of the same kind, at scale — and what that implies about trusting its explanations. → *Command of Intelligence*

*Each outcome maps to the five institutional outcomes (Judgment, Command of Intelligence, Workmanship, Articulation, Breadth of Mind) — the assessment spine of the degree and its accreditation evidence file.*

## The Made Thing

A model trained from scratch on data you gathered — with an honest evaluation of where it fails. Four things ship together: the data and an account of how it was gathered; the model, its training code, and its loss curve; the evaluation on held-out data, with every wrong prediction examined; and the failure report — what the model cannot know, who it fails, and what would have to be true of the data for it to be trusted. It is defended by predicting on a new example the examiner brings, and by questioning on the report. It enters your portfolio and is reviewed at the annual gate.

## How You're Assessed

- **Weekly builds** — the data log, the first fit, the network, the evaluation — each one run on your own data and explained.
- **The model and its failure report**, demonstrated on a new example and defended.
- **Unassisted examinations on paper** — one gradient step by hand, reading a confusion matrix, saying what a model cannot know. The institution certifies the human, so part of this course happens with the tools closed.
- Everything lands in your **portfolio**, reviewed against the five outcomes at the end-of-year gate.

## The Daily Path

One session per course day — each one built to look easy and pull you in: one thing to experience, one idea, one question to carry. The schedule below is generated from the course's own day files.

<!-- sdit:days:begin -->
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

---

*Every course here is built to one standard: it ends in a made thing you can show, and it ships day by day.*
