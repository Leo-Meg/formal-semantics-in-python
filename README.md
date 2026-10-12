# Formal semantics, from sentence to truth value

Logic implemented with no dependencies, where each class in the program is a clause of the mathematical definition.

**Léo Mégret** — implementation, French technical notes.  
**Haeeul Hwang** — English documentation, Korean documentation, review.

> **Repository status** — step 2 of 5, landed by Léo Mégret.

---

## Why this repository

This is the part of Léo's Master's where he saw the exact correspondence between a
mathematical definition and a program. A language defined inductively, a semantics
defined clause by clause, and code that is its line-by-line translation.

The original assignment was marked on the code as much as on the result, with an
oral defence. The brief insisted, *"Make sure that your code is clear and well
commented. The quality of your code will be taken into account."* It is the
assignment that taught him the most about program design, and not only about
logic.

The chain runs end to end: a French sentence goes in, a truth value comes out.

---

## Steps

| | Step | Modules | Tests | Landed by | Detailed note (French) |
|---|---|---|---:|---|---|
| **1** | Propositional logic: syntax, semantics, model checking | `src/propositionnel.py` | 28 | Léo | [`logique-propositionnelle`](notes/logique-propositionnelle.md) |
| **2** | Building models: normal forms and DPLL | `src/sat.py` | 20 | Léo | [`formes-normales-et-dpll`](notes/formes-normales-et-dpll.md) |

**48** tests in total.

---

## What each step found

**1. Propositional logic: syntax, semantics, model checking**  
The solver does not answer *false*, it exhibits the counter-example: the ground is wet and it has not rained. That is the sprinkler.

**2. Building models: normal forms and DPLL**  
On a chain of implications DPLL makes zero decisions, a ×315 speed-up. On the pigeonhole principle it hits the wall — and Haken proved in 1985 that no resolution proof of polynomial size exists.

---

## Running it

```bash
python -m src.sat

python -m tests.test_propositionnel
python -m tests.test_sat
```

---

## How we work

**Nothing to download.** The corpus is written into the code. All of
Léo's Master's notebooks began with a `wget` to a university server or a Google
Drive mount. Two years later, half of them no longer run.

**Nothing is claimed without a measurement.** Every figure in this file
corresponds to a command you can re-run.

**Mistakes in the original coursework are quoted, not erased.** Where a result
that was handed in was wrong or incomplete, we say so and give the correct one.

**Negative results stay.** When an experiment shows the opposite of what we
expected, we write down what we found.

**The code is commented in French**, because that is the language it was thought
out in. The documentation is in English, and in Korean where Haeeul has caught
up.

---

*Français : [README_FR.md](README_FR.md) · [CONTRIBUTORS.md](CONTRIBUTORS.md)*
