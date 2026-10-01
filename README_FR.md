# Sémantique formelle — de la phrase à la valeur de vérité

Logique propositionnelle implémentée sans aucune dépendance, où chaque classe du programme est une clause de la définition mathématique.

**Léo Mégret** — Master Linguistique Informatique, Université Paris Cité

> **État du dépôt : version 1.** C'est la première étape d'un travail que je
> mène par étapes, chacune dans son propre dossier. Seule la version 1 existe à
> ce jour. Je publie au fur et à mesure plutôt qu'une fois tout terminé, parce
> que l'intérêt de ce travail est justement l'enchaînement des questions.

---

## Pourquoi ce dépôt

C'est la partie de mon master où j'ai vu la correspondance exacte entre une
définition mathématique et un programme. Un langage défini inductivement, une
sémantique définie clause par clause, et un code qui en est la traduction ligne
à ligne.

Le devoir d'origine était noté sur le code autant que sur le résultat, avec un
oral. L'énoncé insistait : *« Make sure that your code is clear and well
commented. The quality of your code will be taken into account. »* C'est le
devoir qui m'a le plus appris sur la conception d'un programme, et pas seulement
sur la logique.

---

## Ce qui existe aujourd'hui

### Version 1 — Logique propositionnelle : syntaxe, sémantique, model checking

| Fichier | Ce que j'y fais |
|---|---|
| `src/propositionnel.py` | Une classe par clause du langage, `Var`, `Neg`, `Conj`, `Disj`, `Impl` et `Equiv`. Évaluation dans un modèle, tables de vérité, satisfiabilité, validité, contradiction, conséquence logique et génération de contre-exemples. |
| `tests/test_propositionnel.py` | 28 tests, dont toutes les tables de vérité de référence et les lois classiques. |

Origine universitaire : devoir de M1 en sémantique computationnelle,
*PL — model checking and building* (Timothée Bernard), réalisé en groupe.

---

## Lancer le code

```bash
cd 1.logique_python_projet
python -m src.propositionnel
python -m tests.test_propositionnel
```

Aucune dépendance.

---

## Ce que je retiens de cette étape

**Une définition inductive se traduit en une classe par clause, et le programme
devient lisible comme la définition.** Ce n'est pas une astuce de conception,
c'est la structure du problème qui apparaît dans le code.

**Un contre-exemple vaut mieux qu'un verdict.** Dire qu'une formule n'est pas
valide n'apprend rien ; donner la valuation qui la met en défaut montre
exactement où le raisonnement casse. C'est aussi ce qui rend les tests faciles à
écrire.

**Le model checking par énumération est exact, et c'est tout ce qu'on peut en
dire de bien.** Il ne se trompe jamais et il ne passe pas à l'échelle.

---

## Ce qui reste ouvert

Mon `tous_les_modeles()` énumère `2ⁿ` valuations. Avec 20 variables cela fait un
million, avec 50 c'est hors de portée.

Tant que je n'ai pas de méthode qui évite cette explosion, le model checking
reste un jouet. Je sais que les solveurs SAT y parviennent ; je ne sais pas
encore comment.

---

## Comment je travaille

Quatre règles que je me suis données en commençant, et que je compte tenir sur
tout le dépôt.

**Rien à télécharger.** Le corpus est dans le code. Mes notebooks de master
commençaient tous par un `wget` vers un serveur universitaire ou un montage de
Google Drive ; deux ans plus tard, la moitié ne s'exécutent plus.

**Rien n'est affirmé sans mesure.** Chaque chiffre de ce fichier correspond à une
commande qu'on peut relancer.

**Les erreurs de mes rendus sont citées, pas effacées.** Quand un résultat que
j'avais rendu en cours était faux ou incomplet, je le dis et je donne le résultat
correct.

**Les résultats négatifs restent.** Quand une expérience montre l'inverse de ce
que j'attendais, je change la conclusion, pas l'expérience.

**Le code est commenté en français.** C'est un dépôt à lire autant qu'à exécuter.

---

*Version anglaise : [README.md](README.md).*
