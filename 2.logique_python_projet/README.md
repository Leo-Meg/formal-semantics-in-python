# Version 2, construire des modèles. Formes normales et DPLL

> **Où j'en suis.** La version 1 vérifiait des modèles en énumérant `2ⁿ`
> valuations. Cette version s'attaque à la seconde moitié du titre du devoir,
> *model **building***, et implémente l'algorithme qui est encore aujourd'hui
> le squelette de tous les solveurs SAT.

---

## Nouveautés par rapport à la version 1

| Fichier | Ce que j'ajoute |
|---|---|
| `src/sat.py` | Mise en forme normale conjonctive en trois étapes (élimination de → et ↔, forme normale négative, distribution), **DPLL** complet avec propagation unitaire et littéraux purs, compteurs d'appels, générateur du principe des tiroirs, énigme de logique. |
| `tests/test_sat.py` | 20 tests, dont la vérification que chaque étape de normalisation **préserve la sémantique**. |

## Origine universitaire

Même devoir de M1 (Timothée Bernard). *« PL, model **checking & building** »*.
La seconde moitié du titre était la partie que je n'avais pas vraiment traitée.

## Lancer le code

```bash
python -m src.sat
```

```bash
python -m tests.test_sat
```

---

## Checking et building. Deux problèmes, deux mondes

| | ce qu'on donne | ce qu'on demande | difficulté |
|---|---|---|---|
| **checking** | φ et un modèle M | « M ⊨ φ ? » | linéaire |
| **building** | φ seule | trouver M, ou prouver qu'il n'en existe aucun | **NP-complet** |

Le second, c'est **SAT**, le premier problème dont on a démontré la
NP-complétude (Cook, 1971). Mon `tous_les_modeles()` de la version 1 le résolvait
par force brute. `2ⁿ` valuations. Avec 20 variables, un million, avec 50, plus
que d'atomes dans une pièce.

---

## La normalisation, et son coût caché

```
formule          : ((p ∧ q) → r)
sans → ni ↔      : (¬(p ∧ q) ∨ r)
négations en bas : ((¬p ∨ ¬q) ∨ r)
CNF              : (¬p ∨ ¬q ∨ r)
```

Chaque étape est testée pour **préserver la sémantique**, je vérifie
l'équivalence sur toutes les valuations, pas seulement que le code tourne.

Mais la distribution a un coût.

| formule | clauses produites |
|---|---:|
| disjonction de 1 conjonction | 2 |
| disjonction de 2 conjonctions | 4 |
| disjonction de 3 conjonctions | 8 |
| disjonction de 4 conjonctions | **16** |

**2ⁿ clauses.** C'est exactement la raison d'être de la transformation de
Tseitin, qui produit une CNF de taille **linéaire** au prix de variables
auxiliaires, et qui n'est pas *équivalente* mais seulement
*équisatisfiable*, ce qui suffit quand on cherche seulement un modèle.

---

## DPLL. Deux règles qui font presque tout le travail

L'algorithme tient en quatre lignes.

1. formule vide → **satisfaite**,
2. clause vide → **contradiction**, retour arrière,
3. **propagation unitaire** et **littéraux purs** tant que possible,
4. sinon, **parier** sur une variable et essayer les deux valeurs.

Ce qui le distingue de l'énumération, ce sont les étapes 2 et 3, l'une coupe
une branche **dès qu'elle est perdue**, l'autre **déduit au lieu de deviner**.

### La propagation unitaire, mesurée

Sur une chaîne d'implications `x₀ ∧ (x₀→x₁) ∧ (x₁→x₂) ∧ …`.

| variables | 2ⁿ modèles | appels DPLL | gain |
|---:|---:|---:|---:|
| 4 | 16 | 5 | ×3 |
| 8 | 256 | 9 | ×28 |
| 12 | 4 096 | 13 | **×315** |

**Zéro décision.** `x₀` est forcé, donc `x₁`, donc `x₂`… DPLL ne parie jamais.
il déduit. Le gain est exponentiel, et il croît avec `n`.

Vérifié par `test_la_propagation_unitaire_evite_les_decisions`, qui exige
littéralement `stats.decisions == 0`.

---

## Une énigme, résolue par déduction

```
Trois personnes, trois animaux, quatre indices.
16 appels | 1 décision | 13 propagations unitaires

    anna a le poisson
   bruno a le chien
   clara a le chat
```

**Une anecdote que je garde**, parce qu'elle illustre l'intérêt d'avoir deux
implémentations indépendantes, ma première version de l'énigme n'avait que
trois indices, et mon solveur DPLL renvoyait bien une solution. Le test
d'unicité, écrit avec l'énumération exhaustive de la version 1, a montré qu'il
en existait **trois**.

Le solveur n'avait pas tort. C'est mon énigme qui était sous-contrainte. Sans le
vérificateur indépendant, je n'aurais jamais vu le problème.

---

## Le mur. Le principe des tiroirs

`n` pigeons dans `n−1` trous. C'est insatisfiable, un enfant le comprend.

| pigeons | variables | appels DPLL | temps |
|---:|---:|---:|---:|
| 3 | 6 | 12 | 0,2 ms |
| 4 | 12 | 51 | 0,6 ms |
| 5 | 20 | 230 | 2,3 ms |
| **6** | **30** | **1 190** | **11,2 ms** |

Le coût est multiplié par ~5 à chaque pigeon ajouté.

**Ce n'est pas un défaut de mon code.** Haken a démontré en 1985 qu'**aucune
preuve par résolution de taille polynomiale n'existe** pour ce problème. Les
solveurs SAT industriels butent dessus exactement de la même façon.

> C'est le rappel que je retiens de ce devoir, la NP-complétude n'est pas une
> abstraction théorique. Elle se mesure, sur un portable, en quelques
> millisecondes qui deviennent des heures.

---

## Ce que les tests garantissent

Le test que je considère comme le plus important est
`test_dpll_accord_avec_l_enumeration`, sur neuf formules, **DPLL doit répondre
exactement comme la force brute**. Un solveur rapide qui répond faux est pire
qu'inutile.

Et `test_dpll_trouve_un_modele_valide` va plus loin, il ne vérifie pas que le
solveur dit « satisfiable », il **évalue la formule dans le modèle renvoyé**.

---

## Ce que je n'ai pas implémenté, et pourquoi je le signale

- **La transformation de Tseitin.** Je mesure l'explosion qu'elle évite, mais
  je ne l'implémente pas.
- **Le CDCL** (*Conflict-Driven Clause Learning*), qui est ce qui sépare
  vraiment un solveur des années 1960 d'un solveur moderne, apprendre une
  clause à chaque conflit pour ne jamais refaire la même erreur.
- **VSIDS.** Mon heuristique de choix est « la variable la plus fréquente ».
  Les solveurs modernes privilégient les variables impliquées dans les conflits
  récents, ce qui est bien plus fin.
- **Les littéraux surveillés** (*watched literals*), qui évitent de reparcourir
  toutes les clauses à chaque affectation.

Ces quatre techniques expliquent l'essentiel de l'écart entre mon solveur et un
solveur industriel, qui traite couramment des instances à un million de
variables.

---

## Ce qui reste ouvert

La logique propositionnelle ne dit rien de la structure interne d'une phrase.
« Tous les chiens aboient » et « Médor aboie » sont pour elle deux variables sans
rapport, alors que la première devrait entraîner la seconde.

Tant que je ne peux pas descendre sous la proposition, la moitié des inférences
du langage ordinaire m'échappe.
