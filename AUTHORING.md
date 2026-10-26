# Writing the days

This is the only document you need to write lessons for the San Diego Institute of Technology's open curriculum. Read it once, fully, before you write anything. Then follow it exactly. The validator enforces most of it; the rest is judgment, and the examples here are the standard.

---

## 1. What you are writing for

SDIT is an institution founded on one claim: technology, art, craft, science, and philosophy are one discipline, artificially divided by the industrial university. It teaches through real work, physical before formal, with San Diego as the laboratory: the ocean teaches physics, the culture teaches media, the terrain teaches engineering. Everything it certifies reduces to five outcomes: Judgment, Command of Intelligence, Workmanship, Articulation, Breadth of Mind.

The curriculum is a four-year degree framework: 44 courses, fifteen days each, published one week at a time. A day is about ten minutes: one thing to experience, one idea, one question to carry. Every course already has an **arc** (`courses/<DIR>/arc.md`), the approved plan for its fifteen days. You do not design days. You write the day the arc already describes.

## 2. The Nine Laws

1. **The Founder's Test.** Would the founder genuinely want to take this? If not, it is not done.
2. **The Dual Register.** Keep the names, transform the delivery. The catalog says Calculus I; the day is the ramp.
3. **Physical Before Formal.** No concept arrives as notation first. Force is a bottom turn before it is a vector.
4. **The Double Feature.** Ideas travel in company: a text, a film, an album, as one conversation.
5. **It Ends in a Made Thing.** Every course closes with an artifact, defended or exhibited.
6. **A Day Looks Easy.** One idea, one thing to experience, one question, in minutes. Depth waits behind optional doors.
7. **AI-Native, Not AI-Dependent.** The tools stay open, and the human is examined unaided.
8. **Open to Everyone.** Readable without an account, by anyone.
9. **Day by Day, or It Doesn't Ship.** Nothing is live until a learner knows exactly what to do each day.

## 3. The order of work

Write a whole week at a time, every course in it, in the weekday order. Never write a course ahead of its week.

```bash
python3 scripts/status.py --next
```

prints the next week to write: each day's course, number, title, question, and the command to scaffold it. Do that week. Then run it again.

## 4. Writing one day

```bash
python3 scripts/scaffold_day.py HUM-101 2
```

creates `courses/HUM-101/day-02.md`, already filled from the arc: the title, the question, and the arc's notes on the thing to experience, the idea, and the doors (as HTML comments above the sections they inform). The scaffold refuses a day out of order or outside the course's plan.

You write four things, and delete every comment and placeholder as you go:

1. **The dek.** The line under the title. One line, under fifteen words, naming what the day holds. "Ten minutes. One painted cup, eight lines of poetry, one question."
2. **The thing to experience.** One section, titled `## Look`, `## Watch`, `## Listen`, or `## Read`. The thing goes *on the page*: a figure with an image, an embedded video, or a quotation. Then one short paragraph on why it matters to the reader today.
3. **One idea.** Under `## One idea`. A few hundred words. One idea only; if you have two, one of them is a door.
4. **The three doors.** Under `## If you're still curious`: something to read, something to watch or hear, someone to ask. The third door always begins `**Ask someone.**`

The question section is already written for you: the bold question, the answer line, the answer marker, and the done line. Do not change its wording. For a Workshop course, the question section may be titled `## Now make something` and hold the making instruction before the question.

The day's structure, exactly:

```markdown
---
id: hum101-day-02
title: "Day 02 — My Name Is Nobody"
day: 2
course: HUM 101 — The Ancient World
question: "When did needing credit for something cost you more than the thing was worth?"
---

# Day 02 — My Name Is Nobody

<the dek>

---

## Look                       (or Watch, Listen, Read: exactly one)

<the thing, on the page, then why it matters today>

---

## One idea

<the idea>

---

## Carry the question

For the rest of today, carry this one:

**<the question, exactly as in the front matter>**

Answer in a line or a page, or not at all. What you write is kept in your Notebook.

<!-- sdit:answer -->

That's it. **Day 2 is done.**

---

## If you're still curious

Three doors. Open one, or none — they'll be here tomorrow too.

**Read the real thing.** …

**Watch (or listen to) the other half.** …

**Ask someone.** Tonight, ask someone you trust: *"…"* …
```

## 5. The checklist (the validator enforces every item marked ✓)

- ✓ Front matter has `id`, `title`, `day`, `course`, `question`.
- ✓ The H1 is the title, exactly.
- ✓ The title is the arc's title for that day. If the day truly needs a different title, change the arc's row in the same commit.
- ✓ Exactly one of Look, Watch, Listen, Read; then One idea; then the question section; and `## If you're still curious` last. No other sections.
- ✓ The experience section holds a `<figure>`, an `<iframe>`, or a quotation (`>`).
- ✓ The bold question is the front-matter question, word for word.
- ✓ The answer marker `<!-- sdit:answer -->` sits under the question.
- ✓ The done line: `That's it. **Day N is done.**` with the right N.
- ✓ Three doors; the third begins `**Ask someone.**`
- ✓ The main path (everything before the doors) is 200 to 550 words.
- ✓ Images come from `upload.wikimedia.org` (or this site), with `alt`, `loading="lazy"`, and `referrerpolicy="no-referrer"`.
- ✓ Embeds come from `https://www.youtube-nocookie.com/embed/` only.
- ✓ None of the scaffold's placeholders remain.
- ✓ None of these words: revolutionary, disruptive, game-changing, incredible, amazing, unlock, delve, dive into, journey.
- Physical before formal: the first appearance of any concept is a thing you can see, hear, or feel.
- One idea. If you can name two, cut one.
- The catalog register (the formal course content, from the course page) is named once, so a transcript reader can place the day.

## 6. Rights

The thing on the page must be **public domain, openly licensed, or embeddable by its publisher**. Never invent a source.

- **Images:** Wikimedia Commons only. Open the file's Commons page and confirm it exists and its license allows reuse before you use it. Use the `upload.wikimedia.org` image address from that page. Give the maker and date in the caption.
- **Texts:** Project Gutenberg, the Internet Archive's public-domain scans, or a Lectio edition. Lectio editions exist for The Odyssey, The Iliad, The Republic, Meditations, The Aeneid, The Divine Comedy, The Prince, Confessions, Nicomachean Ethics, Gilgamesh, The Analects, and Hamlet; when the text is one of these, quote the Lectio edition.
- **Video:** an official channel's video, embedded through `youtube-nocookie.com`. If you cannot confirm the channel is the rights holder, make it a door, not the thing on the page.
- **Anything in copyright** (most books after 1929, nearly all films and albums): quote under fifteen words at most, and send the reader to buy, borrow, or stream it. It is a door.
- The arc's "Rights and sources" section lists what still needs confirming. Confirm it, or choose differently.

## 7. The voice

Declarative, not exclamatory. Short sentences. Serious without solemn. Classical references are organic, not decorative. San Diego is grounding, not marketing. Assume the reader is capable. Write "you".

In the voice:

1. That's not a story about boats. That's a story about you and your phone.
2. The Greeks were doing systems thinking about human weakness three thousand years before anyone called it that.
3. Calculus has a reputation: a wall of symbols guarding the gates of every technical field.
4. Zoom in.
5. It will do exactly what you said, millions of times a second, and never what you meant.
6. Physics is not in the textbook. It's in the water.
7. Quality is not the assignment. Finishing is the assignment.
8. He gets the experience and survives it, because he engineered the situation in advance.
9. The phrase "right now" is the whole subject.
10. Look for the seam at the horizon.

Not the voice:

1. Get ready to embark on an incredible journey through ancient literature!
2. In today's lesson, we will explore the fascinating world of derivatives.
3. Let's dive into why this matters.
4. It's important to note that physics is everywhere around us.
5. Unlock your potential as a maker.
6. This revolutionary approach will change how you think about code.
7. Homer, arguably one of the greatest poets of all time, wrote two epic poems.
8. As we've learned, learning is a lifelong process.
9. In conclusion, the Odyssey teaches us many valuable lessons.
10. Don't worry if this seems hard at first; you've got this!

Read the five published Day 1s (`courses/*/day-01.md`) before your first day, and read one again before each week. They are the standard.

## 8. Before you commit

```bash
python3 scripts/build_site.py --out .
python3 scripts/validate.py
python3 scripts/tests/run_tests.py
```

All three must pass. Then preview the week:

```bash
python3 -m http.server 3001
```

open `http://localhost:3001/curriculum/day-by-day.html`, and read each new day on the page, start to finish, as a learner would. Then commit the whole week in one commit: `Semester 1, Week 2: <the five titles>`. Commit every regenerated file the build changed; CI rebuilds the site and fails if anything is out of date.

A person reads and line-edits every week before it publishes. Your job is a draft good enough that the edit is small.

Committing a week does not publish it. The release gate in `knowledge/calendar.yaml` (`released_through`) decides which weeks are live: a written day after the gate is built locally, shown on its course page and the Path as "Publishes <date>", and left out of the deploy and the sitemap. On the Monday a week releases, move `released_through` forward, build, commit, and deploy. `python3 scripts/status.py --next` reports how many days sit written ahead of the gate.

## 9. Writing a course's syllabus block

Every course page already carries a `syllabus:` block in its front matter; the build generates Course Information, the assessment weights, and Policies from it. If a course's plan changes (a material, a weight, the exam), change the block, never the generated sections. The rules: weekly hours sum to units × 3; weights are integers summing to 100 and include an "Unassisted" component; prerequisites are real course codes from earlier semesters; every material has `access` (open, library, purchase, provided) and `cost`; every core competency claimed appears on a learning-outcome line. `validate.py` checks all of it. The full specification is in `PLAN.md`, section 13.
