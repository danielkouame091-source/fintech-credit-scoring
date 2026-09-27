"""
fiscalite_ohada.py — BaobabVault ERP
Fiscalité & Conformité OHADA : TVA, Impôt sur les Sociétés (BIC/IS),
et états financiers simplifiés dérivés des écritures SYSCOHADA.

⚠️ Taux par défaut (TVA 18%, IS 25%) à vérifier chaque exercice auprès
de la DGI compétente — ce module ne remplace pas un conseil fiscal.
"""

import streamlit as st
import pandas as pd
import sqlite3

TAUX_TVA = 0.18
TAUX_IS = 0.25
MINIMUM_PERCEPTION_IS = 3_000_000


def calculer_tva(ca_ht: float, achats_ht: float) -> dict:
    collectee = ca_ht * TAUX_TVA
    deductible = achats_ht * TAUX_TVA
    net = collectee - deductible
    return {"collectee": collectee, "deductible": deductible, "a_decaisser": max(net, 0), "credit": max(-net, 0)}


def calculer_is(resultat_fiscal: float) -> dict:
    is_theorique = max(resultat_fiscal, 0) * TAUX_IS
    is_du = max(is_theorique, MINIMUM_PERCEPTION_IS) if resultat_fiscal > 0 else 0
    return {"resultat_fiscal": resultat_fiscal, "is_theorique": is_theorique, "minimum": MINIMUM_PERCEPTION_IS, "is_du": is_du}


def etat_financier_simplifie(db_name: str) -> dict:
    """
    Bilan et compte de résultat SIMPLIFIÉS, calculés directement depuis
    compta_ecritures (comptabilite_syscohada.py). Ce n'est pas une liasse
    fiscale OHADA complète (qui exige des retraitements et une revue par
    un expert-comptable) — c'est une lecture rapide de la balance,
    reclassée par grande masse (Actif / Passif / Charges / Produits).
    """
    conn = sqlite3.connect(db_name)
    try:
        df = pd.read_sql_query("SELECT * FROM compta_ecritures", conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    if df.empty:
        return {"actif": 0, "passif": 0, "charges": 0, "produits": 0, "resultat": 0}

    def classe(compte):
        return compte[0] if compte else "?"

    charges = 0.0; produits = 0.0; actif = 0.0; passif = 0.0
    for _, r in df.iterrows():
        c_debit_classe = classe(r["compte_debit"])
        c_credit_classe = classe(r["compte_credit"])
        montant = r["montant"]
        if c_debit_classe == "6":
            charges += montant
        elif c_debit_classe in ("2", "3", "4", "5"):
            actif += montant
        if c_credit_classe == "7":
            produits += montant
        elif c_credit_classe in ("1", "4"):
            passif += montant

    return {"actif": actif, "passif": passif, "charges": charges, "produits": produits, "resultat": produits - charges}


def render(db_name: str):
    st.subheader("🧾 Fiscalité & Conformité OHADA")
    st.caption("Taux par défaut : TVA 18%, IS 25%, minimum de perception 3 000 000 FCFA — à vérifier chaque exercice auprès de la DGI.")

    tab_tva, tab_is, tab_etats = st.tabs(["💶 TVA", "🏢 IS / BIC", "📑 États Financiers Simplifiés"])

    with tab_tva:
        c1, c2 = st.columns(2)
        with c1: ca_ht = st.number_input("Chiffre d'affaires HT du mois (FCFA)", min_value=0.0, step=100000.0)
        with c2: achats_ht = st.number_input("Achats déductibles HT du mois (FCFA)", min_value=0.0, step=100000.0)
        r = calculer_tva(ca_ht, achats_ht)
        k1, k2, k3 = st.columns(3)
        k1.metric("TVA Collectée", f"{r['collectee']:,.0f} FCFA")
        k2.metric("TVA Déductible", f"{r['deductible']:,.0f} FCFA")
        k3.metric("TVA à Décaisser", f"{r['a_decaisser']:,.0f} FCFA")
        if r["credit"] > 0:
            st.info(f"Crédit de TVA à reporter : {r['credit']:,.0f} FCFA")

    with tab_is:
        resultat = st.number_input("Résultat fiscal de l'exercice (FCFA)", step=500000.0)
        r = calculer_is(resultat)
        k1, k2 = st.columns(2)
        k1.metric("IS Théorique (25%)", f"{r['is_theorique']:,.0f} FCFA")
        k2.metric("IS Dû (après minimum)", f"{r['is_du']:,.0f} FCFA")
        if 0 < r["is_theorique"] < r["minimum"]:
            st.warning("Le minimum de perception s'applique.")

    with tab_etats:
        st.caption("⚠️ Lecture rapide par grande masse comptable — ne remplace pas une liasse fiscale OHADA validée par un expert-comptable.")
        etats = etat_financier_simplifie(db_name)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### Bilan (aperçu)")
            st.metric("Actif (classes 2-5, mouvements débit)", f"{etats['actif']:,.0f} FCFA")
            st.metric("Passif (classes 1/4, mouvements crédit)", f"{etats['passif']:,.0f} FCFA")
        with c2:
            st.markdown("##### Compte de Résultat (aperçu)")
            st.metric("Produits (classe 7)", f"{etats['produits']:,.0f} FCFA")
            st.metric("Charges (classe 6)", f"{etats['charges']:,.0f} FCFA")
            st.metric("Résultat net (aperçu)", f"{etats['resultat']:,.0f} FCFA")
