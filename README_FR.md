# Sémantique formelle, de la phrase à la valeur de vérité

La logique implémentée sans aucune dépendance, où chaque classe du programme est une clause de la définition mathématique.

**Léo Mégret** — implémentation, notes techniques en français.  
**Haeeul Hwang** — documentation anglaise, documentation coréenne, relecture.

> **État du dépôt** — étape 2 sur 5, publiée par Léo Mégret.

---

## Pourquoi ce dépôt

C'est la partie de mon master où j'ai vu la correspondance exacte entre une
définition mathématique et un programme. Un langage défini inductivement, une
sémantique définie clause par clause, et un code qui en est la traduction ligne à
ligne.

Le devoir d'origine était noté sur le code autant que sur le résultat, avec un
oral. L'énoncé insistait, *« Make sure that your code is clear and well commented.
The quality of your code will be taken into account. »* C'est le devoir qui m'a le
plus appris sur la conception d'un programme, et pas seulement sur la logique.

La chaîne va d'un bout à l'autre : une phrase française entre, une valeur de
vérité sort.

---

## Les étapes

| | Étape | Modules | Tests | Publiée par | Note détaillée (français) |
|---|---|---|---:|---|---|
| **1** | Logique propositionnelle : syntaxe, sémantique, model checking | `src/propositionnel.py` | 28 | Léo | [`logique-propositionnelle`](notes/logique-propositionnelle.md) |
| **2** | Construire des modèles : formes normales et DPLL | `src/sat.py` | 20 | Léo | [`formes-normales-et-dpll`](notes/formes-normales-et-dpll.md) |

**48** tests au total.

---

## Ce que chaque étape a trouvé

**1. Logique propositionnelle : syntaxe, sémantique, model checking**  
Le solveur ne répond pas *faux*, il exhibe le contre-exemple : le sol est mouillé et il n'a pas plu. C'est l'arrosage automatique.

**2. Construire des modèles : formes normales et DPLL**  
Sur une chaîne d'implications, DPLL prend zéro décision, gain ×315. Sur le principe des tiroirs il bute — et Haken a démontré en 1985 qu'aucune preuve par résolution de taille polynomiale n'existe.

---

## Lancer le code

```bash
python -m src.sat

python -m tests.test_propositionnel
python -m tests.test_sat
```

---

## Comment nous travaillons

**Rien à télécharger.** Le corpus est écrit dans le code. Tous mes
notebooks de master commençaient par un `wget` vers un serveur universitaire ou
un montage de Google Drive ; deux ans plus tard, la moitié ne s'exécutent plus.

**Rien n'est affirmé sans mesure.** Chaque chiffre de ce fichier correspond à
une commande qu'on peut relancer.

**Les erreurs de mes rendus sont citées, pas effacées.** Quand un résultat que
j'avais rendu était faux ou incomplet, je le dis et je donne le bon.

**Les résultats négatifs restent.** Quand une expérience montre l'inverse de ce
que j'attendais, j'écris ce que j'ai trouvé.

**Le code est commenté en français**, parce que c'est la langue dans laquelle je
l'ai pensé. La documentation est en anglais, et en coréen quand Haeeul est
passée dessus.

---

*English: [README.md](README.md) · [CONTRIBUTORS.md](CONTRIBUTORS.md)*
