# Formal semantics, from sentence to truth value

Propositional logic implemented with no dependencies, where each class in the program is a clause of the mathematical definition.

**Léo Mégret**, MSc Computational Linguistics, Université Paris Cité

> **Repository status, version 2.** I am doing this work in stages, each in its
> own folder. I publish as I go rather than once everything is finished.

---

## Why this repository

This is the part of my Master's where I saw the exact correspondence between a
mathematical definition and a program. A language defined inductively, a semantics
defined clause by clause, and code that is its line-by-line translation.

The original assignment was marked on the code as much as on the result, with an
oral defence. The brief insisted, *"Make sure that your code is clear and well
commented. The quality of your code will be taken into account."* It is the
assignment that taught me the most about program design, and not only about
logic.

---

## Published versions

| | Folder | Contents | Tests |
|---|---|---|---:|
| **1** | `1.logique_python_projet` | Propositional logic, syntax, semantics, model checking | 28 |
| **2** | `2.logique_python_projet` | Building models, normal forms and DPLL | 20 |

That is **48 tests** in total. Each folder contains everything the previous
one had, plus one step.

---

## Running the latest version

```bash
cd 2.logique_python_projet
python -m src.sat
python -m tests.test_sat
```

---

## What is still open

Propositional logic says nothing about the internal structure of a sentence. For
it, « Tous les chiens aboient » and « Médor aboie » are two unrelated variables,
when the first should entail the second.

As long as I cannot go below the proposition, half of the inferences of ordinary
language are out of reach.

---

## How I work

Four rules I set myself at the start, and intend to keep across the whole
repository.

**Nothing to download.** The corpus is written into the code. All of my Master's
notebooks began with a `wget` to a university server or a Google Drive mount. Two
years later, half of them no longer run.

**Nothing is claimed without a measurement.** Every figure in this file
corresponds to a command you can re-run.

**Mistakes in my coursework are quoted, not erased.** Where a result I handed in
was wrong or incomplete, I say so and give the correct one.

**Negative results stay.** When an experiment shows the opposite of what I
expected, I write down what I found.

**The code is commented in French.**

---

---

*French version, which I wrote first, [README_FR.md](README_FR.md).*
