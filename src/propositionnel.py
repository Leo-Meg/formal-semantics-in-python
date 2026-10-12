"""
Logique propositionnelle : syntaxe, sémantique, et vérification de modèles.

D'où ça vient
-------------
Devoir de M1 en sémantique computationnelle (Timothée Bernard) : *« PL — model
checking & building »*. Nous devions implémenter, en groupe de deux ou trois,
des fonctions de vérification de modèles pour la logique propositionnelle puis
pour la logique du premier ordre. L'énoncé insistait :

> *« Make sure that your code is clear and well commented. The quality of your
> code will be taken into account. »*

C'est le devoir qui m'a le plus appris sur la **conception** d'un programme, et
pas seulement sur la logique. La raison est que l'énoncé imposait une
architecture : une classe par clause de la définition inductive du langage.

Pourquoi cette architecture est la bonne
-----------------------------------------
Le langage de la logique propositionnelle se définit inductivement :

    φ ::=  p            (variable propositionnelle)
        |  ¬φ           (négation)
        |  (φ ∧ ψ)      (conjonction)
        |  (φ ∨ ψ)      (disjonction)
        |  (φ → ψ)      (implication)
        |  (φ ↔ ψ)      (équivalence)

Une classe par clause, et une méthode ``evaluer`` par classe. La sémantique
devient alors une **traduction ligne à ligne** de la définition mathématique, et
la récursion structurelle du code suit exactement la récursion de la
définition. Il n'y a aucun `if` sur le type de formule nulle part — c'est le
polymorphisme qui s'en charge.

C'est la première fois que j'ai vu une correspondance aussi exacte entre une
définition mathématique et un programme. Je la retrouve depuis partout : le
`check` d'une formule, le `forward` d'une couche de réseau, l'évaluation d'un
terme — c'est toujours la même idée.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from itertools import product

# Un modèle (ou « valuation ») associe une valeur de vérité à chaque variable
# propositionnelle. C'est tout ce dont on a besoin pour évaluer une formule.
Modele = dict[str, bool]


# --------------------------------------------------------------------------- #
# Syntaxe
# --------------------------------------------------------------------------- #


class Formule(ABC):
    """Classe mère de toutes les formules.

    Elle ne fait presque rien : c'est chaque sous-classe qui porte sa propre
    clause sémantique. C'est le principe de l'énoncé du devoir, et il rend le
    code extensible — ajouter un connecteur, c'est ajouter une classe, sans
    toucher à une seule ligne existante.
    """

    @abstractmethod
    def evaluer(self, modele: Modele) -> bool:
        """Valeur de vérité de la formule dans ``modele``."""

    @abstractmethod
    def variables(self) -> set[str]:
        """Ensemble des variables propositionnelles apparaissant dans la formule."""

    def est_satisfaite_par(self, modele: Modele) -> bool:
        """Alias lisible de ``evaluer``, pour les énoncés du type « M ⊨ φ »."""
        return self.evaluer(modele)

    def __and__(self, autre: Formule) -> Formule:
        return Conj(self, autre)

    def __or__(self, autre: Formule) -> Formule:
        return Disj(self, autre)

    def __invert__(self) -> Formule:
        return Neg(self)

    def __rshift__(self, autre: Formule) -> Formule:
        """``a >> b`` se lit « a implique b ». Sucre syntaxique très pratique."""
        return Impl(self, autre)


class Var(Formule):
    """Variable propositionnelle : « il pleut », « Anna dort »…

    C'est le cas de base de la récursion. Sa valeur ne se calcule pas : elle se
    **lit** dans le modèle. Un modèle qui ne l'assigne pas rend la formule
    ininterprétable, et je lève une erreur explicite plutôt que de renvoyer
    silencieusement `False` — une valeur manquante n'est pas une valeur fausse.
    """

    def __init__(self, nom: str):
        assert isinstance(nom, str) and nom, "une variable a besoin d'un nom"
        self.nom = nom

    def evaluer(self, modele: Modele) -> bool:
        if self.nom not in modele:
            raise KeyError(
                f"la variable « {self.nom} » n'est pas définie dans le modèle "
                f"{sorted(modele)}"
            )
        return modele[self.nom]

    def variables(self) -> set[str]:
        return {self.nom}

    def __str__(self) -> str:
        return self.nom

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, autre: object) -> bool:
        return isinstance(autre, Var) and self.nom == autre.nom

    def __hash__(self) -> int:
        return hash(("Var", self.nom))


class Neg(Formule):
    """Négation : ``¬φ`` est vraie si et seulement si ``φ`` est fausse."""

    def __init__(self, phi: Formule):
        assert isinstance(phi, Formule), f"attendu une Formule, reçu {type(phi)}"
        self.phi = phi

    def evaluer(self, modele: Modele) -> bool:
        return not self.phi.evaluer(modele)

    def variables(self) -> set[str]:
        return self.phi.variables()

    def __str__(self) -> str:
        return f"¬{self.phi}"

    def __repr__(self) -> str:
        return str(self)


class _Binaire(Formule):
    """Facteur commun aux connecteurs binaires (constructeur, variables, affichage)."""

    symbole = "?"

    def __init__(self, gauche: Formule, droite: Formule):
        assert isinstance(gauche, Formule) and isinstance(droite, Formule)
        self.gauche = gauche
        self.droite = droite

    def variables(self) -> set[str]:
        return self.gauche.variables() | self.droite.variables()

    def __str__(self) -> str:
        return f"({self.gauche} {self.symbole} {self.droite})"

    def __repr__(self) -> str:
        return str(self)


class Conj(_Binaire):
    """Conjonction : vraie si les deux le sont."""

    symbole = "∧"

    def evaluer(self, modele: Modele) -> bool:
        return self.gauche.evaluer(modele) and self.droite.evaluer(modele)


class Disj(_Binaire):
    """Disjonction **inclusive** : vraie si au moins une des deux l'est.

    Point de vocabulaire qui compte pour un linguiste : le « ou » du français
    est souvent compris comme exclusif (« fromage ou dessert »). Le ∨ de la
    logique est toujours inclusif. Le ou exclusif s'écrit ``¬(φ ↔ ψ)``, et je le
    fournis plus bas.
    """

    symbole = "∨"

    def evaluer(self, modele: Modele) -> bool:
        return self.gauche.evaluer(modele) or self.droite.evaluer(modele)


class Impl(_Binaire):
    """Implication matérielle : ``φ → ψ`` est fausse **uniquement** si φ est vraie
    et ψ fausse.

    C'est le connecteur qui déroute le plus, et à juste titre : « s'il pleut,
    alors 2 + 2 = 4 » est logiquement **vrai**, alors qu'aucun locuteur ne
    l'accepterait. L'implication matérielle ne capture aucune notion de
    pertinence ni de causalité — elle ne dit rien de plus que « il n'arrive pas
    que φ soit vraie et ψ fausse ».

    C'est précisément l'écart entre la logique et le langage qui rend la
    sémantique formelle intéressante : on sait exactement ce que le formalisme
    capture, donc exactement ce qu'il rate.
    """

    symbole = "→"

    def evaluer(self, modele: Modele) -> bool:
        return (not self.gauche.evaluer(modele)) or self.droite.evaluer(modele)


class Equiv(_Binaire):
    """Équivalence : vraie si les deux formules ont la même valeur."""

    symbole = "↔"

    def evaluer(self, modele: Modele) -> bool:
        return self.gauche.evaluer(modele) == self.droite.evaluer(modele)


def ou_exclusif(gauche: Formule, droite: Formule) -> Formule:
    """Le « ou » exclusif du langage courant : ``¬(φ ↔ ψ)``."""
    return Neg(Equiv(gauche, droite))


# --------------------------------------------------------------------------- #
# Vérification de modèles
# --------------------------------------------------------------------------- #


def tous_les_modeles(variables: set[str]) -> list[Modele]:
    """Énumère les ``2^n`` valuations possibles.

    C'est brutal et c'est assumé : la vérification de modèles par énumération
    est exponentielle. Avec 20 variables cela fait déjà un million de modèles.
    C'est exactement pourquoi les solveurs SAT existent — j'en implémente un à
    la version 2.
    """
    ordonnees = sorted(variables)
    return [dict(zip(ordonnees, valeurs))
            for valeurs in product([False, True], repeat=len(ordonnees))]


def table_de_verite(formule: Formule) -> list[tuple[Modele, bool]]:
    """Toutes les valuations avec la valeur de la formule."""
    return [(m, formule.evaluer(m)) for m in tous_les_modeles(formule.variables())]


def afficher_table(formule: Formule) -> str:
    """Rend la table de vérité lisible dans un terminal."""
    variables = sorted(formule.variables())
    lignes = ["  " + " | ".join(f"{v:>5}" for v in variables)
              + " || " + str(formule)]
    lignes.append("  " + "-" * (len(lignes[0]) - 2))
    for modele, valeur in table_de_verite(formule):
        cellules = " | ".join(f"{'V' if modele[v] else 'F':>5}" for v in variables)
        lignes.append(f"  {cellules} || {'V' if valeur else 'F'}")
    return "\n".join(lignes)


def est_satisfiable(formule: Formule) -> bool:
    """Existe-t-il **au moins un** modèle qui rend la formule vraie ?"""
    return any(valeur for _, valeur in table_de_verite(formule))


def est_valide(formule: Formule) -> bool:
    """La formule est-elle vraie dans **tous** les modèles ? (tautologie)

    Dualité fondamentale, et l'idée qui fonde toute la démonstration
    automatique : ``φ`` est valide si et seulement si ``¬φ`` est insatisfiable.
    Vérifier une preuve revient donc à chercher une contradiction.
    """
    return all(valeur for _, valeur in table_de_verite(formule))


def est_contradiction(formule: Formule) -> bool:
    """Fausse dans tous les modèles."""
    return not est_satisfiable(formule)


def modeles_satisfaisants(formule: Formule) -> list[Modele]:
    """Tous les modèles qui rendent la formule vraie."""
    return [m for m, valeur in table_de_verite(formule) if valeur]


def sont_equivalentes(phi: Formule, psi: Formule) -> bool:
    """Deux formules ont-elles la même table de vérité ?"""
    return est_valide(Equiv(phi, psi))


def consequence_logique(premisses: list[Formule], conclusion: Formule) -> bool:
    """``Γ ⊨ φ`` : la conclusion est-elle vraie dans **tout** modèle des prémisses ?

    C'est la notion centrale de toute la logique, et sa définition sémantique
    est d'une simplicité qui m'avait frappé : *il n'existe aucun modèle où les
    prémisses sont vraies et la conclusion fausse*. Rien de plus.

    Un raisonnement valide, ce n'est donc pas « la conclusion découle » au sens
    intuitif — c'est « aucun contre-exemple n'existe ».
    """
    variables = set().union(*(p.variables() for p in premisses),
                            conclusion.variables()) if premisses else conclusion.variables()
    for modele in tous_les_modeles(variables):
        if all(p.evaluer(modele) for p in premisses) and not conclusion.evaluer(modele):
            return False
    return True


def contre_exemple(premisses: list[Formule], conclusion: Formule) -> Modele | None:
    """Renvoie un modèle qui invalide le raisonnement, ou ``None`` s'il n'y en a pas.

    Je trouve cette fonction bien plus utile que ``consequence_logique`` : quand
    un raisonnement est faux, on veut savoir **pourquoi**. Un solveur qui répond
    seulement « non » est frustrant ; un solveur qui exhibe le contre-exemple
    est un outil de diagnostic.
    """
    variables = set().union(*(p.variables() for p in premisses),
                            conclusion.variables()) if premisses else conclusion.variables()
    for modele in tous_les_modeles(variables):
        if all(p.evaluer(modele) for p in premisses) and not conclusion.evaluer(modele):
            return modele
    return None


if __name__ == "__main__":
    print("=== Logique propositionnelle : syntaxe et sémantique ===\n")

    pluie = Var("pluie")
    parapluie = Var("parapluie")
    mouille = Var("mouillé")

    # -- 1. Construction et affichage --------------------------------------- #
    print("--- Construire des formules ---\n")
    formule = Impl(Conj(pluie, Neg(parapluie)), mouille)
    print(f"  {formule}")
    print(f"  variables : {sorted(formule.variables())}\n")

    print("  Avec le sucre syntaxique des opérateurs Python :")
    identique = (pluie & ~parapluie) >> mouille
    print(f"  {identique}")
    print(f"  équivalente à la précédente : {sont_equivalentes(formule, identique)}\n")

    # -- 2. Évaluation dans un modèle ---------------------------------------- #
    print("--- Évaluer dans un modèle donné ---\n")
    for description, modele in [
        ("il pleut, pas de parapluie, je suis mouillé",
         {"pluie": True, "parapluie": False, "mouillé": True}),
        ("il pleut, pas de parapluie, je suis sec",
         {"pluie": True, "parapluie": False, "mouillé": False}),
        ("il ne pleut pas",
         {"pluie": False, "parapluie": False, "mouillé": False}),
    ]:
        print(f"  {'V' if formule.evaluer(modele) else 'F'}  {description}")

    print(
        "\n  Le troisième cas illustre l'implication matérielle : quand il ne\n"
        "  pleut pas, la formule est VRAIE quoi qu'il arrive ensuite. C'est\n"
        "  logiquement correct et linguistiquement déroutant.\n"
    )

    # -- 3. Table de vérité --------------------------------------------------- #
    print("--- Table de vérité ---\n")
    print(afficher_table(Impl(pluie, mouille)))

    # -- 4. Les trois statuts logiques ---------------------------------------- #
    print("\n--- Satisfiable, valide, contradictoire ---\n")
    exemples = [
        ("p", pluie),
        ("p ∨ ¬p (tiers exclu)", Disj(pluie, Neg(pluie))),
        ("p ∧ ¬p (contradiction)", Conj(pluie, Neg(pluie))),
        ("(p → q) ↔ (¬q → ¬p) (contraposée)",
         Equiv(Impl(pluie, mouille), Impl(Neg(mouille), Neg(pluie)))),
        ("¬(p ∧ q) ↔ (¬p ∨ ¬q) (De Morgan)",
         Equiv(Neg(Conj(pluie, mouille)), Disj(Neg(pluie), Neg(mouille)))),
    ]
    print(f"  {'formule':>36} | {'satisf.':>8} | {'valide':>7} | {'contrad.':>9}")
    print("  " + "-" * 68)
    for nom, phi in exemples:
        print(f"  {nom:>36} | {str(est_satisfiable(phi)):>8} | "
              f"{str(est_valide(phi)):>7} | {str(est_contradiction(phi)):>9}")

    print(
        "\n  La dualité qui fonde la démonstration automatique : φ est VALIDE si\n"
        "  et seulement si ¬φ est INSATISFIABLE. Prouver revient donc à chercher\n"
        "  une contradiction — c'est le principe de la réfutation.\n"
    )

    # -- 5. Raisonnements valides et invalides -------------------------------- #
    print("--- Conséquence logique : Γ ⊨ φ ---\n")
    raisonnements = [
        ("modus ponens", [Impl(pluie, mouille), pluie], mouille),
        ("modus tollens", [Impl(pluie, mouille), Neg(mouille)], Neg(pluie)),
        ("AFFIRMATION DU CONSÉQUENT (sophisme)",
         [Impl(pluie, mouille), mouille], pluie),
        ("NÉGATION DE L'ANTÉCÉDENT (sophisme)",
         [Impl(pluie, mouille), Neg(pluie)], Neg(mouille)),
        ("syllogisme hypothétique",
         [Impl(pluie, parapluie), Impl(parapluie, mouille)], Impl(pluie, mouille)),
    ]
    for nom, premisses, conclusion in raisonnements:
        valide = consequence_logique(premisses, conclusion)
        print(f"  {'VALIDE ' if valide else 'INVALIDE'}  {nom}")
        print(f"            {' , '.join(str(p) for p in premisses)}  ⊨  {conclusion}")
        if not valide:
            m = contre_exemple(premisses, conclusion)
            lisible = ", ".join(f"{k}={'V' if v else 'F'}" for k, v in sorted(m.items()))
            print(f"            contre-exemple : {lisible}")
        print()

    print(
        "  Les deux sophismes sont exactement ceux que les humains commettent le\n"
        "  plus. « Le sol est mouillé, donc il a plu » est une inférence naturelle\n"
        "  — et logiquement invalide : l'arrosage automatique existe. Le\n"
        "  contre-exemple affiché EST cette situation.\n"
        "\n"
        "  C'est ce que j'ai trouvé de plus intéressant dans ce devoir : le\n"
        "  programme ne dit pas seulement « faux », il produit la situation qui\n"
        "  fait échouer le raisonnement. C'est un outil de diagnostic, pas un\n"
        "  simple juge."
    )
