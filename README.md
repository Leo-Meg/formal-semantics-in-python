# Formal semantics — from sentence to truth value

Propositional logic implemented with no dependencies, where each class in the program is a clause of the mathematical definition.

**Léo Mégret** — MSc Computational Linguistics, Université Paris Cité

> **Repository status: version 1.** This is the first step of a piece of work I
> am doing in stages, each in its own folder. Only version 1 exists so far. I am
> publishing as I go rather than once everything is finished, because the point
> of this work is precisely the way one question leads to the next.

---

## Why this repository

This is the part of my Master's where I saw the exact correspondence between a
mathematical definition and a program. A language defined inductively, a
semantics defined clause by clause, and code that is its line-by-line
translation.

The original assignment was marked on the code as much as on the result, with an
oral defence. The brief insisted: *"Make sure that your code is clear and well
commented. The quality of your code will be taken into account."* It is the
assignment that taught me the most about program design, and not only about
logic.

---

## What exists today

### Version 1 — Propositional logic: syntax, semantics, model checking

| File | What I do in it |
|---|---|
| `src/propositionnel.py` | One class per clause of the language: `Var`, `Neg`, `Conj`, `Disj`, `Impl` and `Equiv`. Evaluation in a model, truth tables, satisfiability, validity, contradiction, logical consequence and counter-example generation. |
| `tests/test_propositionnel.py` | 28 tests, including every reference truth table and the classical laws. |

Academic origin: a first-year Master's assignment in computational semantics,
*PL — model checking and building* (Timothée Bernard), done as a group.

---

## Running the code

```bash
cd 1.logique_python_projet
python -m src.propositionnel
python -m tests.test_propositionnel
```

No dependencies.

---

## What I take from this step

**An inductive definition translates into one class per clause, and the program
becomes as readable as the definition.** This is not a design trick, it is the
structure of the problem showing through the code.

**A counter-example is worth more than a verdict.** Saying that a formula is not
valid teaches nothing; giving the valuation that defeats it shows exactly where
the reasoning breaks. It also makes the tests easy to write.

**Model checking by enumeration is exact, and that is all one can say for it.**
It is never wrong, and it does not scale.

---

## What is still open

My `tous_les_modeles()` enumerates `2ⁿ` valuations. With 20 variables that is a
million, with 50 it is out of reach.

As long as I have no method that avoids this explosion, model checking stays a
toy. I know SAT solvers manage it; I do not yet know how.

---

## How I work

Four rules I set myself at the start, and intend to keep across the whole
repository.

**Nothing to download.** The corpus lives in the code. All of my Master's
notebooks began with a `wget` to a university server or a Google Drive mount.
Two years later, half of them no longer run.

**Nothing is claimed without a measurement.** Every figure in this file
corresponds to a command you can re-run.

**Mistakes in my submitted coursework are quoted, not erased.** Where a result I
handed in was wrong or incomplete, I say so and give the correct one.

**Negative results stay.** When an experiment shows the opposite of what I
expected, I change the conclusion, not the experiment.

**The code is commented in French.** This is a repository meant to be read as
much as run.

---

*French version, and the one I wrote first: [README_FR.md](README_FR.md).*
