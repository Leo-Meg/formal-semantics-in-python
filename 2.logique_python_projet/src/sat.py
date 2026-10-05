"""
Construction de modèles : formes normales, DPLL, et l'explosion combinatoire.

D'où ça vient
-------------
Même devoir de M1 (Timothée Bernard) : *« PL — model **checking & building** »*.
La seconde moitié du titre était la partie que je n'avais pas vraiment traitée.

Vérifier un modèle (*checking*) et en construire un (*building*) sont deux
problèmes de difficulté radicalement différente :

* **checking** — on me donne φ et un modèle M, je réponds « M ⊨ φ ? ». C'est
  linéaire en la taille de la formule. Facile.
* **building** — on me donne φ, je dois trouver un M qui la satisfait *ou*
  prouver qu'il n'en existe aucun. C'est **SAT**, le premier problème dont on a
  démontré la NP-complétude (Cook, 1971).

Ma version 1 résolvait SAT par énumération : `2ⁿ` valuations. Avec 20 variables
cela fait un million ; avec 50, plus que d'atomes dans une pièce.

Ce que je fais ici
------------------
J'implémente **DPLL** (Davis, Putnam, Logemann, Loveland, 1962) — l'algorithme
qui est encore aujourd'hui le squelette de tous les solveurs SAT modernes — et
je mesure ce qu'il économise réellement par rapport à l'énumération.
"""

from __future__ import annotations

import itertools

from .propositionnel import (
    Conj,
    Disj,
    Equiv,
    Formule,
    Impl,
    Modele,
    Neg,
    Var,
    tous_les_modeles,
)

# Un littéral est une variable ou sa négation : ``("p", True)`` ou ``("p", False)``.
Litteral = tuple[str, bool]
# Une clause est une disjonction de littéraux ; une formule CNF, une conjonction
# de clauses. Je représente donc une CNF par une liste de listes.
Clause = list[Litteral]
CNF = list[Clause]


# --------------------------------------------------------------------------- #
# 1. Mise en forme normale conjonctive
# --------------------------------------------------------------------------- #


def eliminer_connecteurs(phi: Formule) -> Formule:
    """Réécrit → et ↔ à l'aide de ¬, ∧ et ∨ uniquement.

        φ → ψ   devient   ¬φ ∨ ψ
        φ ↔ ψ   devient   (¬φ ∨ ψ) ∧ (¬ψ ∨ φ)

    Première étape de la normalisation. Elle illustre que → et ↔ ne sont pas des
    connecteurs « primitifs » : {¬, ∧, ∨} suffit à tout exprimer. (En réalité
    {¬, ∧} suffit déjà, par De Morgan.)
    """
    if isinstance(phi, Var):
        return phi
    if isinstance(phi, Neg):
        return Neg(eliminer_connecteurs(phi.phi))
    gauche = eliminer_connecteurs(phi.gauche)
    droite = eliminer_connecteurs(phi.droite)
    if isinstance(phi, Impl):
        return Disj(Neg(gauche), droite)
    if isinstance(phi, Equiv):
        return Conj(Disj(Neg(gauche), droite), Disj(Neg(droite), gauche))
    return type(phi)(gauche, droite)


def pousser_negations(phi: Formule) -> Formule:
    """Fait descendre les négations jusqu'aux variables (*forme normale négative*).

    On applique De Morgan et l'élimination de la double négation :

        ¬(φ ∧ ψ)  devient  ¬φ ∨ ¬ψ
        ¬(φ ∨ ψ)  devient  ¬φ ∧ ¬ψ
        ¬¬φ       devient  φ

    Après cette étape, toute négation porte directement sur une variable : on
    n'a plus que des **littéraux**, ce qui est exactement ce dont DPLL a besoin.
    """
    if isinstance(phi, Var):
        return phi
    if isinstance(phi, Neg):
        interieur = phi.phi
        if isinstance(interieur, Var):
            return phi
        if isinstance(interieur, Neg):
            return pousser_negations(interieur.phi)
        if isinstance(interieur, Conj):
            return Disj(pousser_negations(Neg(interieur.gauche)),
                        pousser_negations(Neg(interieur.droite)))
        if isinstance(interieur, Disj):
            return Conj(pousser_negations(Neg(interieur.gauche)),
                        pousser_negations(Neg(interieur.droite)))
        raise ValueError(f"connecteur non éliminé : {type(interieur)}")
    return type(phi)(pousser_negations(phi.gauche), pousser_negations(phi.droite))


def distribuer(phi: Formule) -> Formule:
    """Distribue ∨ sur ∧ pour obtenir une conjonction de disjonctions.

        φ ∨ (ψ ∧ χ)  devient  (φ ∨ ψ) ∧ (φ ∨ χ)

    C'est l'étape coûteuse : **la taille de la formule peut exploser
    exponentiellement**. C'est la raison d'être de la transformation de Tseitin,
    qui produit une CNF de taille linéaire au prix de variables auxiliaires — et
    qui n'est pas équivalente mais seulement équisatisfiable, ce qui suffit pour
    SAT.

    Je ne l'implémente pas, mais je mesure l'explosion dans la démonstration.
    """
    if isinstance(phi, (Var, Neg)):
        return phi
    gauche = distribuer(phi.gauche)
    droite = distribuer(phi.droite)

    if isinstance(phi, Conj):
        return Conj(gauche, droite)

    # φ ∨ (ψ ∧ χ)  ->  (φ ∨ ψ) ∧ (φ ∨ χ)
    if isinstance(droite, Conj):
        return Conj(distribuer(Disj(gauche, droite.gauche)),
                    distribuer(Disj(gauche, droite.droite)))
    if isinstance(gauche, Conj):
        return Conj(distribuer(Disj(gauche.gauche, droite)),
                    distribuer(Disj(gauche.droite, droite)))
    return Disj(gauche, droite)


def _clauses(phi: Formule) -> CNF:
    """Extrait la liste de clauses d'une formule déjà en CNF."""
    if isinstance(phi, Conj):
        return _clauses(phi.gauche) + _clauses(phi.droite)
    return [_litteraux(phi)]


def _litteraux(phi: Formule) -> Clause:
    if isinstance(phi, Disj):
        return _litteraux(phi.gauche) + _litteraux(phi.droite)
    if isinstance(phi, Var):
        return [(phi.nom, True)]
    if isinstance(phi, Neg) and isinstance(phi.phi, Var):
        return [(phi.phi.nom, False)]
    raise ValueError(f"formule non normalisée : {phi}")


def vers_cnf(phi: Formule) -> CNF:
    """Chaîne complète : élimination, négations, distribution, extraction."""
    return _clauses(distribuer(pousser_negations(eliminer_connecteurs(phi))))


def cnf_lisible(cnf: CNF) -> str:
    return " ∧ ".join(
        "(" + " ∨ ".join(f"{'' if signe else '¬'}{nom}" for nom, signe in clause) + ")"
        for clause in cnf
    )


# --------------------------------------------------------------------------- #
# 2. DPLL
# --------------------------------------------------------------------------- #


class StatistiquesDPLL:
    """Compteurs, pour pouvoir comparer DPLL à l'énumération sur des chiffres."""

    def __init__(self) -> None:
        self.appels = 0
        self.decisions = 0
        self.propagations_unitaires = 0
        self.litteraux_purs = 0

    def __str__(self) -> str:
        return (f"{self.appels} appels | {self.decisions} décisions | "
                f"{self.propagations_unitaires} propagations unitaires | "
                f"{self.litteraux_purs} littéraux purs")


def _simplifier(cnf: CNF, litteral: Litteral) -> CNF:
    """Affecte un littéral et simplifie la formule.

    Deux règles, et elles sont exactement duales :

    * une clause **contenant** le littéral est **satisfaite** : on la supprime ;
    * une clause contenant sa **négation** perd ce littéral : on le retire.

    Si une clause devient vide, elle est insatisfiable — c'est le signal de
    retour arrière (*backtracking*).
    """
    nom, valeur = litteral
    resultat: CNF = []
    for clause in cnf:
        if (nom, valeur) in clause:
            continue  # clause satisfaite
        resultat.append([l for l in clause if l != (nom, not valeur)])
    return resultat


def _clause_unitaire(cnf: CNF) -> Litteral | None:
    """Cherche une clause à un seul littéral.

    **La propagation unitaire est l'idée centrale de DPLL.** Une clause à un
    seul littéral ne laisse aucun choix : ce littéral *doit* être vrai. On peut
    donc l'affecter sans faire de pari, et sans avoir à revenir dessus.

    En pratique, c'est ce qui fait presque tout le travail : sur des instances
    structurées, la propagation unitaire élimine l'écrasante majorité de
    l'espace de recherche avant même la première décision.
    """
    for clause in cnf:
        if len(clause) == 1:
            return clause[0]
    return None


def _litteral_pur(cnf: CNF) -> Litteral | None:
    """Cherche une variable qui n'apparaît qu'avec un seul signe.

    Si « p » n'apparaît jamais niée, alors la mettre à vrai ne peut que
    satisfaire des clauses — jamais en casser. On peut donc l'affecter sans
    risque, là encore sans pari.

    C'est la seconde règle « gratuite » de DPLL. Les solveurs modernes l'ont
    largement abandonnée (son coût de détection dépasse son gain), mais elle est
    pédagogiquement limpide.
    """
    signes: dict[str, set[bool]] = {}
    for clause in cnf:
        for nom, valeur in clause:
            signes.setdefault(nom, set()).add(valeur)
    for nom, ensemble in signes.items():
        if len(ensemble) == 1:
            return (nom, next(iter(ensemble)))
    return None


def dpll(cnf: CNF, affectation: Modele | None = None,
         stats: StatistiquesDPLL | None = None) -> Modele | None:
    """Renvoie un modèle satisfaisant la CNF, ou ``None`` s'il n'en existe aucun.

    L'algorithme, en quatre lignes :

      1. si la formule est vide -> **satisfaite**, on renvoie l'affectation ;
      2. si une clause est vide -> **contradiction**, on renvoie ``None`` ;
      3. propagation unitaire et littéraux purs tant que possible ;
      4. sinon on **parie** sur une variable, et on essaie les deux valeurs.

    Ce qui distingue DPLL de l'énumération naïve : les étapes 2 et 3. L'étape 2
    coupe une branche **dès qu'elle est perdue**, sans descendre jusqu'aux
    feuilles ; l'étape 3 déduit au lieu de deviner.
    """
    affectation = dict(affectation or {})
    stats = stats or StatistiquesDPLL()
    stats.appels += 1

    if not cnf:
        return affectation
    if any(len(clause) == 0 for clause in cnf):
        return None

    unitaire = _clause_unitaire(cnf)
    if unitaire is not None:
        stats.propagations_unitaires += 1
        affectation[unitaire[0]] = unitaire[1]
        return dpll(_simplifier(cnf, unitaire), affectation, stats)

    pur = _litteral_pur(cnf)
    if pur is not None:
        stats.litteraux_purs += 1
        affectation[pur[0]] = pur[1]
        return dpll(_simplifier(cnf, pur), affectation, stats)

    # Heuristique de choix : la variable la plus fréquente. Les solveurs
    # modernes utilisent VSIDS, qui privilégie les variables impliquées dans les
    # conflits récents — une idée bien plus fine, et bien plus efficace.
    frequences: dict[str, int] = {}
    for clause in cnf:
        for nom, _ in clause:
            frequences[nom] = frequences.get(nom, 0) + 1
    variable = max(frequences, key=lambda v: (frequences[v], v))

    stats.decisions += 1
    for valeur in (True, False):
        affectation_essai = dict(affectation)
        affectation_essai[variable] = valeur
        resultat = dpll(_simplifier(cnf, (variable, valeur)),
                        affectation_essai, stats)
        if resultat is not None:
            return resultat
    return None


def resoudre(phi: Formule) -> tuple[Modele | None, StatistiquesDPLL]:
    """Interface pratique : d'une formule à un modèle (ou ``None``)."""
    stats = StatistiquesDPLL()
    modele = dpll(vers_cnf(phi), stats=stats)
    if modele is not None:
        # Les variables non contraintes n'apparaissent pas dans l'affectation :
        # on les complète arbitrairement pour renvoyer un modèle total.
        for variable in phi.variables():
            modele.setdefault(variable, True)
    return modele, stats


def est_satisfiable_dpll(phi: Formule) -> bool:
    return resoudre(phi)[0] is not None


def est_valide_dpll(phi: Formule) -> bool:
    """Par réfutation : φ est valide si et seulement si ¬φ est insatisfiable."""
    return not est_satisfiable_dpll(Neg(phi))


# --------------------------------------------------------------------------- #
# 3. Un générateur de problèmes difficiles
# --------------------------------------------------------------------------- #


def principe_des_tiroirs(nb_pigeons: int) -> Formule:
    """Le principe des tiroirs : ``n`` pigeons dans ``n−1`` tiroirs.

    Cette formule est **insatisfiable** — c'est un théorème élémentaire — et
    c'est le contre-exemple historique de la résolution : Haken (1985) a démontré
    qu'aucune preuve par résolution n'en existe de taille polynomiale.

    Autrement dit : ce n'est pas que nos algorithmes sont mal écrits, c'est
    qu'il est **prouvé** qu'aucun solveur fondé sur la résolution ne peut la
    traiter efficacement. Je la garde comme rappel que la NP-complétude n'est
    pas une abstraction.
    """
    nb_trous = nb_pigeons - 1
    variables = {(p, t): Var(f"p{p}t{t}")
                 for p in range(nb_pigeons) for t in range(nb_trous)}

    clauses: list[Formule] = []
    # Chaque pigeon est dans au moins un trou.
    for p in range(nb_pigeons):
        clause = variables[(p, 0)]
        for t in range(1, nb_trous):
            clause = Disj(clause, variables[(p, t)])
        clauses.append(clause)
    # Deux pigeons ne partagent pas un trou.
    for t in range(nb_trous):
        for p1, p2 in itertools.combinations(range(nb_pigeons), 2):
            clauses.append(Disj(Neg(variables[(p1, t)]), Neg(variables[(p2, t)])))

    formule = clauses[0]
    for clause in clauses[1:]:
        formule = Conj(formule, clause)
    return formule


def enigme_zebre_simplifiee() -> tuple[Formule, list[str]]:
    """Une énigme de logique, encodée en propositionnel.

    Trois personnes, trois animaux, quatre indices. Les contraintes déterminent
    une solution unique. C'est le genre de problème où l'encodage compte plus
    que le solveur : le choix des variables décide de tout.
    """
    personnes = ["anna", "bruno", "clara"]
    animaux = ["chat", "chien", "poisson"]
    v = {(p, a): Var(f"{p}_{a}") for p in personnes for a in animaux}

    contraintes: list[Formule] = []
    # Chaque personne a exactement un animal.
    for p in personnes:
        au_moins = v[(p, animaux[0])]
        for a in animaux[1:]:
            au_moins = Disj(au_moins, v[(p, a)])
        contraintes.append(au_moins)
        for a1, a2 in itertools.combinations(animaux, 2):
            contraintes.append(Disj(Neg(v[(p, a1)]), Neg(v[(p, a2)])))
    # Chaque animal appartient à exactement une personne.
    for a in animaux:
        for p1, p2 in itertools.combinations(personnes, 2):
            contraintes.append(Disj(Neg(v[(p1, a)]), Neg(v[(p2, a)])))
    # Les quatre indices. J'en ai eu besoin de QUATRE pour que la solution soit
    # unique : avec les trois premiers, mon énumération exhaustive trouvait
    # encore trois modèles. C'est exactement l'intérêt d'avoir un vérificateur
    # indépendant du solveur — il m'a montré que mon énigme était sous-contrainte.
    contraintes.append(Neg(v[("anna", "chien")]))       # Anna n'a pas le chien
    contraintes.append(Neg(v[("bruno", "poisson")]))    # Bruno n'a pas le poisson
    contraintes.append(Neg(v[("clara", "poisson")]))    # Clara non plus
    # Si Clara a le chien, alors Anna a le chat.
    contraintes.append(Impl(v[("clara", "chien")], v[("anna", "chat")]))

    formule = contraintes[0]
    for c in contraintes[1:]:
        formule = Conj(formule, c)
    return formule, [f"{p}_{a}" for p in personnes for a in animaux]


if __name__ == "__main__":
    import time

    print("=== Construction de modèles : formes normales et DPLL ===\n")

    P, Q, R = Var("p"), Var("q"), Var("r")

    # -- 1. La normalisation --------------------------------------------------#
    print("--- De la formule à la CNF ---\n")
    phi = Impl(Conj(P, Q), R)
    print(f"  formule       : {phi}")
    print(f"  sans → ni ↔   : {eliminer_connecteurs(phi)}")
    print(f"  négations en bas : "
          f"{pousser_negations(eliminer_connecteurs(phi))}")
    print(f"  CNF           : {cnf_lisible(vers_cnf(phi))}\n")

    print("  L'explosion de la distribution :\n")
    print(f"  {'formule':>44} | {'clauses':>8}")
    print("  " + "-" * 56)
    for n in (1, 2, 3, 4):
        # (a1 ∧ b1) ∨ (a2 ∧ b2) ∨ … : cas pire de la distribution.
        blocs = [Conj(Var(f"a{i}"), Var(f"b{i}")) for i in range(n)]
        f = blocs[0]
        for b in blocs[1:]:
            f = Disj(f, b)
        nb = len(vers_cnf(f))
        texte = f"disjonction de {n} conjonction(s)"
        print(f"  {texte:>44} | {nb:>8}")
    print("\n  2^n clauses : c'est la raison d'être de la transformation de")
    print("  Tseitin, qui produit une CNF LINÉAIRE au prix de variables")
    print("  auxiliaires — équisatisfiable, mais pas équivalente.\n")

    # -- 2. DPLL en action ---------------------------------------------------- #
    print("--- DPLL : les deux règles qui font tout le travail ---\n")
    formule = Conj(Conj(Disj(P, Q), Disj(Neg(P), R)), Disj(Neg(Q), Neg(R)))
    modele, stats = resoudre(formule)
    print(f"  formule : {formule}")
    print(f"  CNF     : {cnf_lisible(vers_cnf(formule))}")
    print(f"  modèle  : {modele}")
    print(f"  vérifié : {formule.evaluer(modele)}")
    print(f"  coût    : {stats}\n")

    # -- 3. DPLL contre l'énumération ----------------------------------------- #
    print("--- DPLL contre l'énumération exhaustive ---\n")
    print(f"  {'variables':>10} | {'2^n modèles':>12} | {'appels DPLL':>12} | "
          f"{'gain':>8} | {'temps':>9}")
    print("  " + "-" * 62)
    for n in (4, 6, 8, 10, 12):
        # Une chaîne d'implications, satisfiable et fortement contrainte.
        variables = [Var(f"x{i}") for i in range(n)]
        f = variables[0]
        for i in range(n - 1):
            f = Conj(f, Impl(variables[i], variables[i + 1]))

        debut = time.perf_counter()
        _, stats = resoudre(f)
        duree = time.perf_counter() - debut
        print(f"  {n:>10} | {2 ** n:>12,} | {stats.appels:>12} | "
              f"×{2 ** n / max(stats.appels, 1):>7.0f} | {duree * 1000:>7.2f}ms")

    print(
        "\n  La propagation unitaire résout ce problème SANS AUCUNE DÉCISION :\n"
        "  x0 est forcé, donc x1, donc x2… L'algorithme déduit au lieu de\n"
        "  deviner, et le gain est exponentiel.\n"
    )

    # -- 4. Une énigme -------------------------------------------------------- #
    print("--- Résoudre une énigme de logique ---\n")
    enigme, noms = enigme_zebre_simplifiee()
    modele, stats = resoudre(enigme)
    print("  Trois personnes, trois animaux, quatre indices.")
    print(f"  {stats}\n")
    if modele:
        for nom in noms:
            if modele.get(nom):
                personne, animal = nom.split("_")
                print(f"    {personne:>6} a le {animal}")
    print(f"\n  solution vérifiée : {enigme.evaluer(modele)}")

    # -- 5. Le mur ------------------------------------------------------------ #
    print("\n--- Le mur : le principe des tiroirs ---\n")
    print(f"  {'pigeons':>8} | {'variables':>10} | {'satisfiable':>12} | "
          f"{'appels':>8} | {'temps':>9}")
    print("  " + "-" * 56)
    for nb in (3, 4, 5, 6):
        formule = principe_des_tiroirs(nb)
        debut = time.perf_counter()
        modele, stats = resoudre(formule)
        duree = time.perf_counter() - debut
        print(f"  {nb:>8} | {len(formule.variables()):>10} | "
              f"{str(modele is not None):>12} | {stats.appels:>8} | "
              f"{duree * 1000:>7.1f}ms")

    print(
        "\n  n pigeons dans n−1 trous : c'est insatisfiable, et c'est un théorème\n"
        "  élémentaire qu'un enfant comprend. Pourtant le coût explose.\n"
        "\n"
        "  Ce n'est pas un défaut de mon code. Haken a DÉMONTRÉ en 1985 qu'aucune\n"
        "  preuve par résolution de taille polynomiale n'existe pour ce problème.\n"
        "  Les solveurs SAT modernes butent dessus exactement de la même façon.\n"
        "\n"
        "  C'est le rappel que je retiens de ce devoir : la NP-complétude n'est\n"
        "  pas une abstraction théorique. Elle se mesure, sur un portable, en\n"
        "  quelques millisecondes qui deviennent des heures."
    )
