"""
tresorerie.py — BaobabVault ERP
Trésorerie & Rapprochement Bancaire multi-comptes : suivi des soldes
et des flux par compte bancaire distinct (utile dès qu'un client gère
plusieurs comptes — CI, Mali, devises différentes...).
"""

import sqlite3
from datetime import datetime

import pandas as pd
import streamlit as st


def init_tresorerie_tables(db_name: str):
    conn = sqlite3.connect(db_name)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS comptes_bancaires (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT UNIQUE, banque TEXT, devise TEXT DEFAULT 'FCFA', solde_initial REAL DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS flux_tresorerie (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            compte_id INTEGER, date TEXT, libelle TEXT, montant REAL, sens TEXT  -- 'entree' ou 'sortie'
        )
    """)
    conn.commit(); conn.close()


def ajouter_compte(db_name: str, nom: str, banque: str, devise: str, solde_initial: float):
    init_tresorerie_tables(db_name)
    conn = sqlite3.connect(db_name)
    conn.execute(
        "INSERT OR IGNORE INTO comptes_bancaires (nom, banque, devise, solde_initial) VALUES (?,?,?,?)",
        (nom, banque, devise, solde_initial),
    )
    conn.commit(); conn.close()


def enregistrer_flux(db_name: str, compte_id: int, libelle: str, montant: float, sens: str):
    conn = sqlite3.connect(db_name)
    conn.execute(
        "INSERT INTO flux_tresorerie (compte_id, date, libelle, montant, sens) VALUES (?,?,?,?,?)",
        (compte_id, datetime.now().strftime("%Y-%m-%d"), libelle, montant, sens),
    )
    conn.commit(); conn.close()


def solde_compte(db_name: str, compte_id: int) -> float:
    conn = sqlite3.connect(db_name)
    solde_init = conn.execute("SELECT solde_initial FROM comptes_bancaires WHERE id=?", (compte_id,)).fetchone()
    entrees = conn.execute("SELECT COALESCE(SUM(montant),0) FROM flux_tresorerie WHERE compte_id=? AND sens='entree'", (compte_id,)).fetchone()[0]
    sorties = conn.execute("SELECT COALESCE(SUM(montant),0) FROM flux_tresorerie WHERE compte_id=? AND sens='sortie'", (compte_id,)).fetchone()[0]
    conn.close()
    base = solde_init[0] if solde_init else 0
    return base + entrees - sorties


def render(db_name: str):
    st.subheader("🏦 Trésorerie & Rapprochement Bancaire Multi-Comptes")
    init_tresorerie_tables(db_name)

    tab_comptes, tab_flux, tab_rappro = st.tabs(["🏛️ Comptes", "💸 Flux", "🔍 Rapprochement"])

    with tab_comptes:
        with st.form("form_nouveau_compte"):
            c1, c2, c3, c4 = st.columns(4)
            with c1: nom = st.text_input("Nom du compte", value="Compte Principal")
            with c2: banque = st.text_input("Banque", value="SGBCI")
            with c3: devise = st.selectbox("Devise", ["FCFA", "USD", "EUR"])
            with c4: solde_init = st.number_input("Solde initial", value=0.0, step=100000.0)
            if st.form_submit_button("➕ Ajouter le compte"):
                ajouter_compte(db_name, nom, banque, devise, solde_init)
                st.success(f"Compte {nom} ajouté.")

        conn = sqlite3.connect(db_name)
        df_comptes = pd.read_sql_query("SELECT * FROM comptes_bancaires", conn)
        conn.close()
        if df_comptes.empty:
            st.info("Aucun compte bancaire enregistré.")
        else:
            df_comptes["solde_actuel"] = df_comptes["id"].apply(lambda i: solde_compte(db_name, i))
            st.dataframe(df_comptes, use_container_width=True)
            st.metric("Trésorerie totale (tous comptes confondus, hors conversion devise)", f"{df_comptes['solde_actuel'].sum():,.0f}")

    with tab_flux:
        conn = sqlite3.connect(db_name)
        df_comptes = pd.read_sql_query("SELECT id, nom FROM comptes_bancaires", conn)
        conn.close()
        if df_comptes.empty:
            st.info("Ajoute d'abord un compte bancaire.")
        else:
            with st.form("form_flux"):
                compte_id = st.selectbox("Compte", df_comptes["id"].tolist(), format_func=lambda i: df_comptes[df_comptes["id"] == i]["nom"].values[0])
                c1, c2, c3 = st.columns(3)
                with c1: libelle = st.text_input("Libellé", value="Opération")
                with c2: montant = st.number_input("Montant", min_value=0.0, step=10000.0)
                with c3: sens = st.selectbox("Sens", ["entree", "sortie"])
                if st.form_submit_button("Enregistrer le flux"):
                    enregistrer_flux(db_name, compte_id, libelle, montant, sens)
                    st.success("Flux enregistré.")

            conn = sqlite3.connect(db_name)
            df_flux = pd.read_sql_query("SELECT f.*, c.nom as compte FROM flux_tresorerie f JOIN comptes_bancaires c ON f.compte_id=c.id ORDER BY f.id DESC", conn)
            conn.close()
            st.dataframe(df_flux, use_container_width=True)

    with tab_rappro:
        conn = sqlite3.connect(db_name)
        df_comptes = pd.read_sql_query("SELECT id, nom FROM comptes_bancaires", conn)
        conn.close()
        if df_comptes.empty:
            st.info("Ajoute d'abord un compte bancaire.")
        else:
            compte_id = st.selectbox("Compte à rapprocher", df_comptes["id"].tolist(), format_func=lambda i: df_comptes[df_comptes["id"] == i]["nom"].values[0], key="rappro_compte")
            fichier = st.file_uploader("Relevé bancaire (CSV : date, libelle, montant)", type=["csv"])
            conn = sqlite3.connect(db_name)
            df_livre = pd.read_sql_query("SELECT * FROM flux_tresorerie WHERE compte_id=?", conn, params=(compte_id,))
            conn.close()
            if fichier is not None:
                try:
                    df_releve = pd.read_csv(fichier)
                    df_releve.columns = [c.strip().lower() for c in df_releve.columns]
                    m_livre = set(df_livre["montant"].round(2))
                    m_releve = set(df_releve["montant"].round(2)) if "montant" in df_releve.columns else set()
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Rapprochés", len(m_livre & m_releve))
                    c2.metric("Livre seul", len(m_livre - m_releve))
                    c3.metric("Relevé seul", len(m_releve - m_livre))
                except Exception as e:
                    st.error(f"Erreur CSV : {e}")
            else:
                st.dataframe(df_livre, use_container_width=True)
