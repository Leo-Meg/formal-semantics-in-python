"""
Tests de la version 1 — logique propositionnelle.

    python -m tests.test_propositionnel
"""

from __future__ import annotations

from src.propositionnel import (
    Conj,
    Disj,
    Equiv,
    Impl,
    Neg,
    Var,
    afficher_table,
    consequence_logique,
    contre_exemple,
    est_contradiction,
    est_satisfiable,
    est_valide,
    modeles_satisfaisants,
    ou_exclusif,
    sont_equivalentes,
    table_de_verite,
    tous_les_modeles,
)

P, Q, R = Var("p"), Var("q"), Var("r")


# --------------------------------------------------------------------------- #
# Syntaxe
# --------------------------------------------------------------------------- #


def test_variables_collectees_recursivement() -> None:
    assert Conj(P, Neg(Disj(Q, R))).variables() == {"p", "q", "r"}
    assert Neg(Neg(P)).variables() == {"p"}


def test_affichage_lisible() -> None:
    assert str(P) == "p"
    assert str(Neg(P)) == "¬p"
    assert str(Conj(P, Q)) == "(p ∧ q)"
    assert str(Impl(P, Q)) == "(p → q)"


def test_sucre_syntaxique_equivalent_aux_constructeurs() -> None:
    assert sont_equivalentes(P & Q, Conj(P, Q))
    assert sont_equivalentes(P | Q, Disj(P, Q))
    assert sont_equivalentes(~P, Neg(P))
    assert sont_equivalentes(P >> Q, Impl(P, Q))


def test_variable_non_definie_leve_une_erreur() -> None:
    """Une valeur manquante n'est pas une valeur fausse."""
    try:
        P.evaluer({"q": True})
    except KeyError as erreur:
        assert "p" in str(erreur)
        return
    raise AssertionError("une variable absente du modèle aurait dû lever KeyError")


# --------------------------------------------------------------------------- #
# Sémantique : les tables de vérité de référence
# --------------------------------------------------------------------------- #


def test_negation() -> None:
    assert Neg(P).evaluer({"p": True}) is False
    assert Neg(P).evaluer({"p": False}) is True


def test_conjonction() -> None:
    attendu = {(True, True): True, (True, False): False,
               (False, True): False, (False, False): False}
    for (a, b), resultat in attendu.items():
        assert Conj(P, Q).evaluer({"p": a, "q": b}) is resultat


def test_disjonction_est_inclusive() -> None:
    """Le ∨ logique est inclusif, contrairement au « ou » du français."""
    assert Disj(P, Q).evaluer({"p": True, "q": True}) is True
    assert Disj(P, Q).evaluer({"p": False, "q": False}) is False


def test_ou_exclusif_differe_de_la_disjonction() -> None:
    modele = {"p": True, "q": True}
    assert Disj(P, Q).evaluer(modele) is True
    assert ou_exclusif(P, Q).evaluer(modele) is False


def test_implication_materielle() -> None:
    """Fausse dans un seul cas : antécédent vrai, conséquent faux."""
    attendu = {(True, True): True, (True, False): False,
               (False, True): True, (False, False): True}
    for (a, b), resultat in attendu.items():
        assert Impl(P, Q).evaluer({"p": a, "q": b}) is resultat


def test_equivalence() -> None:
    for a in (True, False):
        for b in (True, False):
            assert Equiv(P, Q).evaluer({"p": a, "q": b}) is (a == b)


# --------------------------------------------------------------------------- #
# Énumération
# --------------------------------------------------------------------------- #


def test_nombre_de_modeles_est_exponentiel() -> None:
    for n in (1, 2, 3, 5):
        variables = {f"v{i}" for i in range(n)}
        assert len(tous_les_modeles(variables)) == 2 ** n


def test_tous_les_modeles_sont_distincts() -> None:
    modeles = tous_les_modeles({"a", "b", "c"})
    signatures = {tuple(sorted(m.items())) for m in modeles}
    assert len(signatures) == len(modeles) == 8


def test_table_de_verite_complete() -> None:
    table = table_de_verite(Conj(P, Q))
    assert len(table) == 4
    assert sum(valeur for _, valeur in table) == 1  # une seule ligne vraie


def test_affichage_de_table() -> None:
    rendu = afficher_table(Impl(P, Q))
    assert "p" in rendu and "q" in rendu
    assert rendu.count("\n") == 5  # en-tête + séparateur + 4 lignes


# --------------------------------------------------------------------------- #
# Statuts logiques
# --------------------------------------------------------------------------- #


def test_tiers_exclu_est_valide() -> None:
    assert est_valide(Disj(P, Neg(P)))


def test_contradiction() -> None:
    contradiction = Conj(P, Neg(P))
    assert est_contradiction(contradiction)
    assert not est_satisfiable(contradiction)
    assert modeles_satisfaisants(contradiction) == []


def test_dualite_validite_insatisfiabilite() -> None:
    """φ est valide si et seulement si ¬φ est insatisfiable.

    C'est le principe de la réfutation, qui fonde toute la démonstration
    automatique.
    """
    for phi in (Disj(P, Neg(P)), Impl(P, P), Conj(P, Q), P,
                Equiv(Neg(Conj(P, Q)), Disj(Neg(P), Neg(Q)))):
        assert est_valide(phi) == est_contradiction(Neg(phi)), str(phi)


def test_lois_de_de_morgan() -> None:
    assert sont_equivalentes(Neg(Conj(P, Q)), Disj(Neg(P), Neg(Q)))
    assert sont_equivalentes(Neg(Disj(P, Q)), Conj(Neg(P), Neg(Q)))


def test_contraposee() -> None:
    assert sont_equivalentes(Impl(P, Q), Impl(Neg(Q), Neg(P)))


def test_implication_comme_disjonction() -> None:
    """``p → q`` équivaut à ``¬p ∨ q`` — la définition de l'implication matérielle."""
    assert sont_equivalentes(Impl(P, Q), Disj(Neg(P), Q))


def test_double_negation() -> None:
    assert sont_equivalentes(Neg(Neg(P)), P)


def test_distributivite() -> None:
    assert sont_equivalentes(Conj(P, Disj(Q, R)), Disj(Conj(P, Q), Conj(P, R)))
    assert sont_equivalentes(Disj(P, Conj(Q, R)), Conj(Disj(P, Q), Disj(P, R)))


# --------------------------------------------------------------------------- #
# Conséquence logique
# --------------------------------------------------------------------------- #


def test_modus_ponens_et_tollens() -> None:
    assert consequence_logique([Impl(P, Q), P], Q)
    assert consequence_logique([Impl(P, Q), Neg(Q)], Neg(P))


def test_les_deux_sophismes_classiques() -> None:
    """Affirmation du conséquent et négation de l'antécédent : invalides."""
    assert not consequence_logique([Impl(P, Q), Q], P)
    assert not consequence_logique([Impl(P, Q), Neg(P)], Neg(Q))


def test_le_contre_exemple_est_reellement_un_contre_exemple() -> None:
    """La fonction ne doit pas seulement dire « faux », elle doit le prouver."""
    premisses, conclusion = [Impl(P, Q), Q], P
    modele = contre_exemple(premisses, conclusion)
    assert modele is not None
    assert all(p.evaluer(modele) for p in premisses)
    assert not conclusion.evaluer(modele)


def test_aucun_contre_exemple_si_le_raisonnement_est_valide() -> None:
    assert contre_exemple([Impl(P, Q), P], Q) is None


def test_premisses_contradictoires_impliquent_tout() -> None:
    """*Ex falso quodlibet* : d'une contradiction on déduit n'importe quoi.

    Conséquence directe de la définition sémantique : s'il n'existe aucun modèle
    des prémisses, il n'existe a fortiori aucun modèle où les prémisses sont
    vraies et la conclusion fausse.
    """
    assert consequence_logique([P, Neg(P)], Q)
    assert consequence_logique([P, Neg(P)], Neg(Q))


def test_syllogisme_hypothetique() -> None:
    assert consequence_logique([Impl(P, Q), Impl(Q, R)], Impl(P, R))


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
    print("=== Tests — version 1 : logique propositionnelle ===\n")
    executer_tous_les_tests()
