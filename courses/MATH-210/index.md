---
id: math-210
title: "MATH 210 — Linear Algebra"
course_code: MATH 210
units: 4
thread: Mathematics & Science
status: syllabus
syllabus:
  level: lower
  prerequisites: [MATH 120]
  corequisites: []
  method: [lecture]
  hours:
    instruction: 3
    studio_or_lab: 0
    independent: 9
  materials:
    - {title: "Essence of Linear Algebra (video series)", author: "Grant Sanderson (3Blue1Brown)", edition: "Official 3Blue1Brown channel", access: open, cost: 0}
    - {title: "But what is a neural network? Deep learning, chapter 1", author: "Grant Sanderson (3Blue1Brown)", edition: "Official 3Blue1Brown channel", access: open, cost: 0}
    - {title: "First digital image (1957 scan)", author: "Russell Kirsch, National Bureau of Standards", edition: "Wikimedia Commons, public domain", access: open, cost: 0}
    - {title: "Tartan Ribbon, the first color photograph (1861)", author: "James Clerk Maxwell", edition: "Wikimedia Commons, public domain", access: open, cost: 0}
    - {title: "Man Drawing a Lute (1525)", author: "Albrecht Dürer", edition: "Wikimedia Commons, public domain", access: open, cost: 0}
    - {title: "Chladni figures, plate scans from Entdeckungen über die Theorie des Klanges (1787)", author: "Ernst Chladni", edition: "Wikimedia Commons, public domain", access: open, cost: 0}
    - {title: "Sobel edge detection, before and after (Bikesgray pair)", author: "Wikimedia Commons", edition: "Public domain", access: open, cost: 0}
    - {title: "JPEG quality steps on one image (Felis silvestris silvestris)", author: "Wikimedia Commons", edition: "CC BY-SA", access: open, cost: 0}
    - {title: "A free image editor that shows pixel values", author: "Various", edition: "Any free editor", access: open, cost: 0}
    - {title: "A code notebook environment", author: "Various", edition: "Any free notebook; matrices written out explicitly", access: open, cost: 0}
    - {title: "A small pretrained convolutional network with open weights, first layer", author: "Open-weights release", edition: "Permissive license; the course's standing reference model", access: open, cost: 0}
    - {title: "Singular-value reconstruction notebook", author: "SDIT", access: provided, cost: 0, note: "Open learner follows the Wikipedia image-compression example instead."}
  assessment:
    - {component: "Weekly problem sets, checked by hand", weight: 20}
    - {component: "Unassisted written examinations, two sittings", weight: 25}
    - {component: "The transformation built by hand and found in the model, defended in seminar", weight: 45}
    - {component: "Class participation and the daily path", weight: 10}
  exam: "Two sittings, tools closed: after Day 8, vector arithmetic, a dot product and projection, a two-by-two transformation drawn before it is computed, a matrix product in the right order, a three-unknown system solved by elimination, and a determinant with what its sign and size mean; after Day 14, a change of basis carried through, an eigenvector found and checked, the rank and null space of a small matrix named with what they destroy, and a least-squares line set up."
  rubric: quantitative-study
  core_competencies:
    quantitative-reasoning: D
  outcome_levels:
    judgment: D
    intelligence: D
---

# MATH 210 — Linear Algebra

**Mathematics & Science** · 4 units · Semester 3 · Required core — everyone takes it

## Overview

A photograph is a grid of numbers. So is a recording; so is every layer of every AI model. Linear algebra is what you can do to a grid of numbers — rotate it, blend it, project it, compress it, undo it — and this course does all of it by hand to your own photographs and recordings before it shows you the same operations inside a working model. The transform tool in a photo editor is four numbers. A mix is a weighted sum. Grayscale is a dot product. JPEG is a change of basis followed by keeping the big coefficients. A neural network's layer is a matrix times a vector, plus a bend.

Taught as **The Mathematics of Images**: every photograph, every mix session, every AI model is matrices. Every concept arrives physical before formal — you shear the photograph before you see the matrix, hear mid and side before you see the change of basis, dust the plate with sand and bow it before you see the eigenvector. This is the secret on-ramp to machine learning: by the end you read a model's insides because you have built the operations yourself.

One day a week, about ten minutes a sitting. AI tools stay open — the course is partly about what is inside them — and your own unassisted command of the operations is examined, because the degree certifies you, not your tools. The course ends the way every SDIT course ends: in a made thing — a transformation built by hand and found again in a model — presented and defended.

## The Two Registers

- **Catalog register:** Vector spaces, matrices, linear transformations, eigenvalues. Transfer-legible introductory linear algebra.
- **Teaching frame:** The Mathematics of Images — every photograph, every mix session, every AI model is matrices. The secret on-ramp to machine learning.

## Course Information

<!-- sdit:info:begin -->
| | |
|---|---|
| Catalog number | MATH 210 — Linear Algebra |
| Units | 4 semester units · 180 hours of work over 15 weeks |
| Each week | 3 h instruction · 0 h studio or laboratory · 9 h independent work |
| Level | Lower division |
| Offered | Semester 3 · Year 2 · Fall |
| Prerequisites | [MATH 120](/courses/MATH-120/index.html) |
| Corequisites | None |
| Instructional method | Lecture |
| Instructor | A practitioner-scholar with a body of work in the field: a terminal degree, or equivalent professional standing documented under the Institute's rubric (The Degree, section 9). |
| Rubric | [The quantitative study (Mathematics and Science)](/curriculum/rubrics.html#quantitative-study) |
| Core competencies | Quantitative reasoning (developed) |
| Unassisted examination | Two sittings, tools closed: after Day 8, vector arithmetic, a dot product and projection, a two-by-two transformation drawn before it is computed, a matrix product in the right order, a three-unknown system solved by elimination, and a determinant with what its sign and size mean; after Day 14, a change of basis carried through, an eigenvector found and checked, the rank and null space of a small matrix named with what they destroy, and a least-squares line set up. |

**Required materials**

- *Essence of Linear Algebra (video series)*, Grant Sanderson (3Blue1Brown) — Official 3Blue1Brown channel · open, free
- *But what is a neural network? Deep learning, chapter 1*, Grant Sanderson (3Blue1Brown) — Official 3Blue1Brown channel · open, free
- *First digital image (1957 scan)*, Russell Kirsch, National Bureau of Standards — Wikimedia Commons, public domain · open, free
- *Tartan Ribbon, the first color photograph (1861)*, James Clerk Maxwell — Wikimedia Commons, public domain · open, free
- *Man Drawing a Lute (1525)*, Albrecht Dürer — Wikimedia Commons, public domain · open, free
- *Chladni figures, plate scans from Entdeckungen über die Theorie des Klanges (1787)*, Ernst Chladni — Wikimedia Commons, public domain · open, free
- *Sobel edge detection, before and after (Bikesgray pair)*, Wikimedia Commons — Public domain · open, free
- *JPEG quality steps on one image (Felis silvestris silvestris)*, Wikimedia Commons — CC BY-SA · open, free
- *A free image editor that shows pixel values*, Various — Any free editor · open, free
- *A code notebook environment*, Various — Any free notebook; matrices written out explicitly · open, free
- *A small pretrained convolutional network with open weights, first layer*, Open-weights release — Permissive license; the course's standing reference model · open, free
- *Singular-value reconstruction notebook*, SDIT · provided in the room; open learner follows the Wikipedia image-compression example instead

Required materials cost: nothing. Every item is open, borrowable from a public library, or provided in the room.
<!-- sdit:info:end -->

## Learning Outcomes

By the end of this course you can:

1. Compute with vectors and matrices by hand — combinations, dot products and projections, products in the right order, elimination, determinants, inverses — and catch a machine's error at a glance. → *Judgment* · *Quantitative reasoning*
2. Read a matrix as a transformation: say what it does to a picture or a signal, what it keeps, what it destroys (rank and null space), and whether it can be undone. → *Judgment* · *Quantitative reasoning*
3. Change basis deliberately — left/right to mid/side, RGB to luma and chroma, pixels to frequencies — and say what the new coordinates make simple. → *Command of Intelligence* · *Quantitative reasoning*
4. Find eigenvectors and singular values of a small matrix, and use them to compress an image or explain where a repeated transformation settles. → *Command of Intelligence* · *Quantitative reasoning*
5. Build an image or audio transformation from explicit matrix operations and locate the same operation in a working model's weights; demonstrate the underlying computation unassisted in periodic written examinations. → *Command of Intelligence · Judgment* · *Quantitative reasoning*

*Each outcome maps to the five institutional outcomes (Judgment, Command of Intelligence, Workmanship, Articulation, Breadth of Mind) — the assessment spine of the degree and its accreditation evidence file.*

## The Made Thing

An image or audio transformation built by hand from matrix operations — then found again inside a working model. You choose one: a blur, an edge detector, a color-space change, a rotation with perspective, a stereo widener, a compression that keeps the biggest singular values. You build it as explicit matrices with no library call hiding the multiplication, apply it to your own photograph or recording, and show before and after. Then you open a small pretrained model and find the same operation in its first layer — the kernel that is your blur, the weights that are your edge detector — and write two pages on what matches, what does not, and why. It is presented and defended in seminar; the room names a pixel and you trace it through every matrix.

## How You're Assessed

- **Weekly problem sets** — AI tools open; what's graded is your setup, your verification, and your explanation.
- **The transformation**, presented and defended with the model's weights beside your own.
- **Unassisted written examinations** — hand computation and reading transformations after the first half; change of basis, eigenvectors, rank, and least squares after the second. AI-native, not AI-dependent.
- Everything lands in your **portfolio**, reviewed against the five outcomes at the end-of-year gate.

<!-- sdit:weights:begin -->

| Component | Weight |
|---|---|
| Weekly problem sets, checked by hand | 20% |
| Unassisted written examinations, two sittings | 25% |
| The transformation built by hand and found in the model, defended in seminar | 45% |
| Class participation and the daily path | 10% |
| **Total** | **100%** |

Grades follow the scale in the [academic policies](/curriculum/policies.html#grading).
<!-- sdit:weights:end -->

## The Daily Path

One session per course day — each one built to look easy and pull you in: one thing to experience, one idea, one question to carry. The schedule below is generated from the course's own day files.

<!-- sdit:days:begin -->
The fifteen days below are the open spine of the course, about ten minutes each. The hours in Course Information are the course.

### Day 01 — A Photograph Is a Spreadsheet

Publishes Monday, 26 July 2027.

### Day 02 — Arrows and Pixels

Publishes Monday, 2 August 2027.

### Day 03 — Any Color From Three

Publishes Monday, 9 August 2027.

### Day 04 — Brightness Is a Dot Product

Publishes Monday, 16 August 2027.

### Day 05 — The Transform Tool

Publishes Monday, 23 August 2027.

### Day 06 — Order Matters

Publishes Monday, 30 August 2027.

### Day 07 — Three Unknowns, Three Knobs

Publishes Monday, 6 September 2027.

### Day 08 — How Much Did It Stretch

Publishes Monday, 13 September 2027.

### Day 09 — Flatten

Publishes Monday, 20 September 2027.

### Day 10 — Undo, If You Can

Publishes Monday, 27 September 2027.

### Day 11 — Mid and Side

Publishes Monday, 4 October 2027.

### Day 12 — The Directions That Stay Put

Publishes Monday, 11 October 2027.

### Day 13 — Keep the Big Ones

Publishes Monday, 18 October 2027.

### Day 14 — The Layer

Publishes Monday, 25 October 2027.

### Day 15 — Built by Hand, Found in the Model

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
