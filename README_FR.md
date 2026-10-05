# Sémantique formelle, de la phrase à la valeur de vérité

Logique propositionnelle implémentée sans aucune dépendance, où chaque classe du programme est une clause de la définition mathématique.

**Léo Mégret**, Master Linguistique Informatique, Université Paris Cité

> **État du dépôt, version 2.** Je mène ce travail par étapes, chacune dans son
> propre dossier. Je publie au fur et à mesure plutôt qu'une fois tout terminé.

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

---

## Les versions publiées

| | Dossier | Contenu | Tests |
|---|---|---|---:|
| **1** | `1.logique_python_projet` | Logique propositionnelle, syntaxe, sémantique, model checking | 28 |
| **2** | `2.logique_python_projet` | Construire des modèles, formes normales et DPLL | 20 |

Soit **48 tests** au total. Chaque dossier contient tout le contenu du
précédent, plus une étape.

---

## Lancer la dernière version

```bash
cd 2.logique_python_projet
python -m src.sat
python -m tests.test_sat
```

---

## Ce qui reste ouvert

La logique propositionnelle ne dit rien de la structure interne d'une phrase.
« Tous les chiens aboient » et « Médor aboie » sont pour elle deux variables sans
rapport, alors que la première devrait entraîner la seconde.

Tant que je ne peux pas descendre sous la proposition, la moitié des inférences
du langage ordinaire m'échappe.

---

## Comment je travaille

Quatre règles que je me suis données en commençant, et que je compte tenir sur
tout le dépôt.

**Rien à télécharger.** Le corpus est écrit dans le code. Mes notebooks de master
commençaient tous par un `wget` vers un serveur universitaire ou un montage de
Google Drive. Deux ans plus tard, la moitié ne s'exécutent plus.

**Rien n'est affirmé sans mesure.** Chaque chiffre de ce fichier correspond à une
commande qu'on peut relancer.

**Les erreurs de mes rendus sont citées, pas effacées.** Quand un résultat que
j'avais rendu en cours était faux ou incomplet, je le dis et je donne le résultat
correct.

**Les résultats négatifs restent.** Quand une expérience montre l'inverse de ce
que j'attendais, j'écris ce que j'ai trouvé.

**Le code est commenté en français.**

---

---

*Version anglaise, [README.md](README.md).*
