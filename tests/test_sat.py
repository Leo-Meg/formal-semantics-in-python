"""
Tests de la version 2 — formes normales et DPLL.

    python -m tests.test_sat
"""

from __future__ import annotations

from src.propositionnel import (
    Conj,
    Disj,
    Equiv,
    Impl,
    Neg,
    Var,
    est_satisfiable,
    est_valide,
    sont_equivalentes,
    tous_les_modeles,
)
from src.sat import (
    cnf_lisible,
    distribuer,
    dpll,
    eliminer_connecteurs,
    enigme_zebre_simplifiee,
    est_satisfiable_dpll,
    est_valide_dpll,
    pousser_negations,
    principe_des_tiroirs,
    resoudre,
    vers_cnf,
)

P, Q, R = Var("p"), Var("q"), Var("r")


# --------------------------------------------------------------------------- #
# Normalisation : chaque étape doit préserver la SÉMANTIQUE
# --------------------------------------------------------------------------- #


def test_elimination_des_connecteurs_preserve_le_sens() -> None:
    for phi in (Impl(P, Q), Equiv(P, Q), Impl(Conj(P, Q), R),
                Equiv(Impl(P, Q), Disj(Neg(P), Q))):
        assert sont_equivalentes(phi, eliminer_connecteurs(phi)), str(phi)


def test_elimination_supprime_bien_impl_et_equiv() -> None:
    resultat = eliminer_connecteurs(Equiv(P, Q))
    assert "→" not in str(resultat) and "↔" not in str(resultat)


def test_pousser_negations_preserve_le_sens() -> None:
    for phi in (Neg(Conj(P, Q)), Neg(Disj(P, Q)), Neg(Neg(P)),
                Neg(Conj(Disj(P, Q), Neg(R)))):
        sans_impl = eliminer_connecteurs(phi)
        assert sont_equivalentes(sans_impl, pousser_negations(sans_impl)), str(phi)


def test_negations_portent_sur_des_variables() -> None:
    """Après la forme normale négative, on n'a plus que des littéraux."""
    phi = pousser_negations(eliminer_connecteurs(Neg(Conj(Disj(P, Q), R))))

    def verifier(f) -> None:
        if isinstance(f, Neg):
            assert isinstance(f.phi, Var), f"négation sur {type(f.phi)}"
        elif not isinstance(f, Var):
            verifier(f.gauche)
            verifier(f.droite)

    verifier(phi)


def test_distribution_preserve_le_sens() -> None:
    for phi in (Disj(P, Conj(Q, R)), Disj(Conj(P, Q), Conj(Q, R)),
                Conj(Disj(P, Q), Disj(Q, R))):
        assert sont_equivalentes(phi, distribuer(phi)), str(phi)


def test_cnf_preserve_le_sens() -> None:
    """La chaîne complète de normalisation doit être sémantiquement neutre."""
    for phi in (Impl(Conj(P, Q), R), Equiv(P, Disj(Q, R)),
                Neg(Impl(P, Conj(Q, R)))):
        cnf = vers_cnf(phi)
        for modele in tous_les_modeles(phi.variables()):
            valeur_cnf = all(
                any(modele[nom] == signe for nom, signe in clause) for clause in cnf
            )
            assert phi.evaluer(modele) == valeur_cnf, (str(phi), modele)


def test_cnf_est_bien_une_conjonction_de_clauses() -> None:
    cnf = vers_cnf(Impl(Conj(P, Q), R))
    assert isinstance(cnf, list) and all(isinstance(c, list) for c in cnf)
    assert all(isinstance(l, tuple) and len(l) == 2 for c in cnf for l in c)


def test_explosion_de_la_distribution() -> None:
    """La distribution peut multiplier la taille par 2^n. D'où Tseitin."""
    tailles = []
    for n in (1, 2, 3, 4):
        blocs = [Conj(Var(f"a{i}"), Var(f"b{i}")) for i in range(n)]
        f = blocs[0]
        for b in blocs[1:]:
            f = Disj(f, b)
        tailles.append(len(vers_cnf(f)))
    assert tailles == sorted(tailles), tailles
    assert tailles[-1] >= tailles[0] * 8, tailles


def test_affichage_de_cnf() -> None:
    rendu = cnf_lisible([[("p", True), ("q", False)]])
    assert rendu == "(p ∨ ¬q)"


# --------------------------------------------------------------------------- #
# DPLL : correction
# --------------------------------------------------------------------------- #


def test_dpll_trouve_un_modele_valide() -> None:
    """Un solveur qui renvoie un modèle faux est pire qu'inutile."""
    formules = [
        Disj(P, Q),
        Conj(Disj(P, Q), Disj(Neg(P), R)),
        Impl(Conj(P, Q), R),
        Equiv(P, Neg(Q)),
        Conj(Conj(Disj(P, Q), Disj(Neg(P), R)), Disj(Neg(Q), Neg(R))),
    ]
    for phi in formules:
        modele, _ = resoudre(phi)
        assert modele is not None, str(phi)
        assert phi.evaluer(modele) is True, (str(phi), modele)


def test_dpll_detecte_les_contradictions() -> None:
    for phi in (Conj(P, Neg(P)),
                Conj(Conj(Disj(P, Q), Neg(P)), Neg(Q)),
                Neg(Disj(P, Neg(P)))):
        assert resoudre(phi)[0] is None, str(phi)


def test_dpll_accord_avec_l_enumeration() -> None:
    """Le test le plus important : DPLL doit répondre comme la force brute."""
    formules = [
        P, Neg(P), Disj(P, Q), Conj(P, Neg(P)), Impl(P, Q),
        Equiv(P, Q), Conj(Disj(P, Q), Conj(Disj(Neg(P), R), Disj(Neg(Q), Neg(R)))),
        Neg(Impl(Conj(P, Q), R)), Disj(Conj(P, Q), Conj(Neg(P), Neg(Q))),
    ]
    for phi in formules:
        assert est_satisfiable_dpll(phi) == est_satisfiable(phi), str(phi)


def test_validite_par_refutation() -> None:
    """φ valide ⟺ ¬φ insatisfiable — le principe de la démonstration automatique."""
    for phi in (Disj(P, Neg(P)), Impl(P, P), Conj(P, Q),
                Equiv(Neg(Conj(P, Q)), Disj(Neg(P), Neg(Q))),
                Impl(Conj(Impl(P, Q), P), Q)):
        assert est_valide_dpll(phi) == est_valide(phi), str(phi)


def test_modele_renvoye_est_total() -> None:
    """Toutes les variables de la formule doivent être assignées."""
    phi = Conj(Disj(P, Q), R)
    modele, _ = resoudre(phi)
    assert set(modele) >= phi.variables()


# --------------------------------------------------------------------------- #
# DPLL : efficacité
# --------------------------------------------------------------------------- #


def test_la_propagation_unitaire_evite_les_decisions() -> None:
    """Sur une chaîne d'implications, DPLL ne doit PAS avoir à parier.

    x0 est forcé, donc x1, donc x2… L'algorithme déduit au lieu de deviner.
    """
    n = 10
    variables = [Var(f"x{i}") for i in range(n)]
    phi = variables[0]
    for i in range(n - 1):
        phi = Conj(phi, Impl(variables[i], variables[i + 1]))

    modele, stats = resoudre(phi)
    assert modele is not None
    assert stats.decisions == 0, f"{stats.decisions} décisions, attendu 0"
    assert stats.propagations_unitaires > 0


def test_gain_exponentiel_sur_l_enumeration() -> None:
    """Le résultat central de cette version."""
    gains = []
    for n in (6, 10, 14):
        variables = [Var(f"x{i}") for i in range(n)]
        phi = variables[0]
        for i in range(n - 1):
            phi = Conj(phi, Impl(variables[i], variables[i + 1]))
        _, stats = resoudre(phi)
        gains.append(2 ** n / stats.appels)
    assert gains == sorted(gains), gains
    assert gains[-1] > 100 * gains[0] / 100  # le gain croît avec n
    assert gains[-1] > 500


def test_litteral_pur() -> None:
    """Une variable qui n'apparaît qu'avec un signe peut être fixée sans risque."""
    cnf = [[("p", True), ("q", True)], [("p", True), ("r", False)]]
    modele = dpll(cnf)
    assert modele is not None
    assert modele.get("p") is True


# --------------------------------------------------------------------------- #
# Problèmes concrets
# --------------------------------------------------------------------------- #


def test_enigme_a_une_solution_unique() -> None:
    """L'encodage doit déterminer complètement la réponse."""
    enigme, noms = enigme_zebre_simplifiee()
    modele, _ = resoudre(enigme)
    assert modele is not None
    assert enigme.evaluer(modele)

    vrais = {n for n in noms if modele.get(n)}
    assert vrais == {"anna_poisson", "bruno_chien", "clara_chat"}, vrais

    # Unicité : aucun autre modèle ne satisfait les contraintes.
    solutions = [m for m in tous_les_modeles(enigme.variables())
                 if enigme.evaluer(m)]
    assert len(solutions) == 1


def test_principe_des_tiroirs_est_insatisfiable() -> None:
    """n pigeons dans n−1 trous : théorème élémentaire, et mur pour les solveurs."""
    for nb in (3, 4, 5):
        assert resoudre(principe_des_tiroirs(nb))[0] is None, nb


def test_le_cout_des_tiroirs_explose() -> None:
    """Haken (1985) : aucune preuve par résolution polynomiale n'existe.

    Ce n'est pas un défaut de mon code — c'est un résultat démontré.
    """
    couts = []
    for nb in (3, 4, 5, 6):
        _, stats = resoudre(principe_des_tiroirs(nb))
        couts.append(stats.appels)
    assert couts == sorted(couts)
    assert couts[-1] > 10 * couts[0], couts


def executer_tous_les_tests() -> None:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    echecs = 0
    for test in tests:
        try:
            test()
            print(f"  [OK]     {test.__name__}")
        except AssertionError as e:
            echecs += 1
            print(f"  [ÉCHEC]  {test.__name__} : {e}")
    print(f"\n{len(tests) - echecs}/{len(tests)} tests passés.")
    if echecs:
        raise SystemExit(1)


if __name__ == "__main__":
    print("=== Tests — version 2 : DPLL ===\n")
    executer_tous_les_tests()
