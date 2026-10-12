# Logique propositionnelle. Syntaxe, sémantique, model checking

> Étape 1 sur 5 du dépôt.

> **Où j'en suis.** C'est le point de départ de la sémantique formelle. Un
> langage défini inductivement, une sémantique définie clause par clause, et un
> programme qui en est la traduction ligne à ligne.

---

## Ce que contient cette étape

| Fichier | Ce que j'y fais |
|---|---|
| `src/propositionnel.py` | Une classe par clause du langage, `Var`, `Neg`, `Conj`, `Disj`, `Impl` et `Equiv`. Évaluation dans un modèle, tables de vérité, satisfiabilité, validité, contradiction, conséquence logique et génération de contre-exemples. |
| `tests/test_propositionnel.py` | 28 tests, dont toutes les tables de vérité de référence et les lois classiques. |

## Origine universitaire

Devoir de M1 en sémantique computationnelle (Timothée Bernard), *PL, model
checking and building*. Réalisé en groupe, noté sur le code et sur un oral.
L'énoncé insistait.

> *« Make sure that your code is clear and well commented. The quality of your
> code will be taken into account. »*

C'est le devoir qui m'a le plus appris sur la **conception d'un programme**, et
pas seulement sur la logique.

## Lancer le code

```bash
python -m src.propositionnel
```

```bash
python -m tests.test_propositionnel
```

**Aucune dépendance.**

---

## L'architecture, et pourquoi elle est imposée par les mathématiques

Le langage se définit inductivement.

```
φ ::=  p  |  ¬φ  |  (φ ∧ ψ)  |  (φ ∨ ψ)  |  (φ → ψ)  |  (φ ↔ ψ)
```

Une classe par clause, une méthode `evaluer` par classe. La sémantique devient
une traduction ligne à ligne de la définition mathématique.

```python
class Impl(_Binaire):
    def evaluer(self, modele):
        return (not self.gauche.evaluer(modele)) or self.droite.evaluer(modele)
```

Il n'y a aucun `if` sur le type de formule nulle part, c'est le polymorphisme qui
s'en charge, et la récursion du code suit la récursion de la définition.

C'est la première fois que j'ai vu une correspondance aussi exacte entre une
définition mathématique et un programme. Je la retrouve depuis dans le `check`
d'une formule, dans le `forward` d'une couche de réseau, dans l'évaluation d'un
terme.

En pratique, ajouter un connecteur revient à ajouter une classe, sans toucher à
une ligne existante.

---

## Le connecteur qui déroute

L'implication matérielle `φ → ψ` est fausse uniquement si φ est vraie et ψ
fausse. Il s'ensuit que « s'il pleut, alors 2 + 2 = 4 » est logiquement vrai.

Aucun locuteur n'accepterait cette phrase. L'implication matérielle ne capture ni
la pertinence ni la causalité, elle dit seulement qu'il n'arrive pas que φ soit
vraie et ψ fausse.

C'est cet écart qui rend la sémantique formelle intéressante. On sait exactement
ce que le formalisme capture, donc exactement ce qu'il rate. Dans un modèle
statistique on ne sait ni l'un ni l'autre.

Autre exemple, plus proche du linguiste. Le `∨` logique est inclusif, alors que le
« ou » du français est le plus souvent compris comme exclusif, comme dans
« fromage ou dessert ». J'ai donc ajouté `ou_exclusif(φ, ψ) = ¬(φ ↔ ψ)`.

---

## Le contre-exemple

Mon `contre_exemple()` ne se contente pas de dire qu'un raisonnement est faux, il
produit la situation qui le fait échouer.

```
INVALIDE  AFFIRMATION DU CONSÉQUENT (sophisme)
          (pluie → mouillé) , mouillé  ⊨  pluie
          contre-exemple, mouillé=V, pluie=F
```

Traduit en français, le sol est mouillé mais il n'a pas plu. C'est l'arrosage
automatique. Le programme a produit la situation qui invalide l'inférence.

Les deux sophismes que je teste, l'affirmation du conséquent et la négation de
l'antécédent, sont ceux que les humains commettent le plus souvent. « Le sol est
mouillé, donc il a plu » est une inférence naturelle et logiquement invalide.

Un solveur qui répond seulement non n'aide pas. Un solveur qui donne le
contre-exemple sert au diagnostic.

---

## Ce que les tests garantissent

| propriété | test |
|---|---|
| toutes les tables de vérité de référence | `test_conjonction`, `test_implication_materielle`, … |
| lois de De Morgan, contraposée, double négation, distributivité | 4 tests |
| φ valide équivaut à ¬φ insatisfiable | `test_dualite_validite_insatisfiabilite` |
| le contre-exemple est bien un contre-exemple | `test_le_contre_exemple_est_reellement_un_contre_exemple` |
| *ex falso quodlibet* | `test_premisses_contradictoires_impliquent_tout` |
| une variable manquante lève une erreur | `test_variable_non_definie_leve_une_erreur` |

Ce dernier point est un choix de conception auquel je tiens. Une valeur manquante
n'est pas une valeur fausse. Renvoyer silencieusement `False` pour une variable
non assignée transformerait un modèle incomplet en modèle valide, et masquerait le
bug.

---

## La dualité qui fonde la démonstration automatique

```
φ est VALIDE  ⟺  ¬φ est INSATISFIABLE
```

Prouver un théorème revient donc à chercher une contradiction. C'est le principe
de la réfutation, et c'est ce qui rend la démonstration automatique possible. Au
lieu de vérifier une infinité de cas, on cherche un seul objet.

C'est aussi la limite sur laquelle je bute. Mon `tous_les_modeles()` énumère `2ⁿ`
valuations. Avec 20 variables cela fait un million, avec 50 c'est hors de
portée.

---

## Ce qui reste ouvert

Mon `tous_les_modeles()` énumère `2ⁿ` valuations. Avec 20 variables cela fait un
million, avec 50 c'est hors de portée.

Tant que je n'ai pas de méthode qui évite cette explosion, le model checking reste
un jouet. Je sais que les solveurs SAT y parviennent, je ne sais pas encore
comment.
