"""
licences.py — BaobabVault ERP
Licence liée à l'empreinte matérielle (machine-locked) + panneau
administrateur "fondateur" caché pour révoquer/bloquer à distance,
relances automatiques J-7/J-3/J-1, et tableau de bord KPI.

⚠️ Limite honnête n°1 : comme pour tout schéma SQLite embarqué dans le
même process que l'app cliente, un client avec accès shell au conteneur
pourrait théoriquement altérer sa propre ligne. Pour une vraie séparation
fournisseur/client en production, la table `licences` doit vivre sur un
serveur central à toi (API HTTPS séparée), pas dans le déploiement client.

⚠️ Limite honnête n°2 : Streamlit ne fait tourner aucune tâche de fond.
Les relances ci-dessous se déclenchent quand quelqu'un OUVRE l'app et
que le seuil (J-7/J-3/J-1) est franchi — pas exactement au calendrier
si personne n'ouvre l'app ce jour-là. Pour un vrai déclenchement
calendaire indépendant des visites, il faut un job planifié externe
(ex: GitHub Actions quotidien) interrogeant une base centrale.
"""

import hashlib
import platform
import sqlite3
import uuid
from datetime import datetime, timedelta

import streamlit as st

import alertes

DUREE_JOURS = {"mensuel": 30, "annuel": 365, "essai": 14}
SEUILS_RELANCE = [7, 3, 1]  # jours avant expiration


def empreinte_machine() -> str:
    """Empreinte stable de la machine hôte — sert à lier une licence payante à un poste précis."""
    brut = f"{platform.node()}|{uuid.getnode()}|{platform.system()}|{platform.machine()}"
    return hashlib.sha256(brut.encode("utf-8")).hexdigest()[:32]


def init_licences_tables(db_name: str):
    conn = sqlite3.connect(db_name)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS licences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client TEXT,
            licence_key TEXT UNIQUE,
            type_abonnement TEXT,
            montant REAL DEFAULT 0,
            contact_telephone TEXT DEFAULT '',
            empreinte_machine TEXT,
            date_debut TEXT,
            date_fin TEXT,
            statut TEXT DEFAULT 'Actif',
            dernier_rappel_envoye INTEGER DEFAULT NULL
        )
    """)
    cols = [c[1] for c in conn.execute("PRAGMA table_info(licences)").fetchall()]
    for col, ddl in [
        ("montant", "ALTER TABLE licences ADD COLUMN montant REAL DEFAULT 0"),
        ("contact_telephone", "ALTER TABLE licences ADD COLUMN contact_telephone TEXT DEFAULT ''"),
        ("dernier_rappel_envoye", "ALTER TABLE licences ADD COLUMN dernier_rappel_envoye INTEGER DEFAULT NULL"),
    ]:
        if col not in cols:
            conn.execute(ddl)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS licence_evenements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT, licence_key TEXT, evenement TEXT, details TEXT
        )
    """)
    conn.commit()
    conn.close()


def _log(db_name, licence_key, evenement, details):
    conn = sqlite3.connect(db_name)
    conn.execute(
        "INSERT INTO licence_evenements (timestamp, licence_key, evenement, details) VALUES (?,?,?,?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), licence_key, evenement, details),
    )
    conn.commit(); conn.close()


def creer_licence(db_name: str, client: str, type_abonnement: str, montant: float = 0.0, telephone: str = "") -> str:
    init_licences_tables(db_name)
    cle = hashlib.sha256(f"{client}{datetime.now()}".encode()).hexdigest()[:20].upper()
    debut = datetime.now(); fin = debut + timedelta(days=DUREE_JOURS.get(type_abonnement, 30))
    conn = sqlite3.connect(db_name)
    conn.execute(
        """INSERT INTO licences (client, licence_key, type_abonnement, montant, contact_telephone, date_debut, date_fin, statut)
           VALUES (?,?,?,?,?,?,?,'Actif')""",
        (client, cle, type_abonnement, montant, telephone, debut.strftime("%Y-%m-%d"), fin.strftime("%Y-%m-%d")),
    )
    conn.commit(); conn.close()
    _log(db_name, cle, "Création", f"Licence créée pour {client} ({type_abonnement}, {montant:,.0f} FCFA)")
    return cle


def _verifier_et_envoyer_relance(db_name: str, licence_key: str, client: str, telephone: str, jours_restants: int):
    """Envoie un SMS de relance au client (et au fondateur) au franchissement d'un seuil J-7/J-3/J-1, une seule fois par seuil."""
    conn = sqlite3.connect(db_name)
    dernier = conn.execute("SELECT dernier_rappel_envoye FROM licences WHERE licence_key=?", (licence_key,)).fetchone()
    conn.close()
    dernier_seuil = dernier[0] if dernier else None

    for seuil in SEUILS_RELANCE:
        deja_envoye = dernier_seuil is not None and dernier_seuil <= seuil
        if jours_restants <= seuil and not deja_envoye:
            message = f"⏳ BaobabVault ERP — votre abonnement ({client}) expire dans {jours_restants} jour(s). Merci de régulariser pour éviter une coupure d'accès."
            if telephone:
                alertes.envoyer_sms([telephone], message)
            alertes.alerte_urgence_founder(f"[Relance J-{seuil}] {client} ({licence_key}) — {jours_restants} j restants.")
            conn = sqlite3.connect(db_name)
            conn.execute("UPDATE licences SET dernier_rappel_envoye=? WHERE licence_key=?", (seuil, licence_key))
            conn.commit(); conn.close()
            _log(db_name, licence_key, f"Relance J-{seuil}", f"SMS envoyé à {telephone or '(aucun numéro client)'}")
            break


def verifier_licence_machine(db_name: str, licence_key: str) -> dict:
    """
    Vérifie la licence, verrouille/vérifie l'empreinte machine, et déclenche
    les relances automatiques J-7/J-3/J-1 si le seuil est franchi.
    """
    init_licences_tables(db_name)
    if not licence_key:
        return {"valide": False, "message": "Aucune clé de licence configurée."}

    empreinte_actuelle = empreinte_machine()
    conn = sqlite3.connect(db_name)
    row = conn.execute(
        "SELECT client, date_fin, statut, empreinte_machine, contact_telephone FROM licences WHERE licence_key=?",
        (licence_key,),
    ).fetchone()

    if not row:
        conn.close()
        _log(db_name, licence_key, "⚠️ Clé introuvable", f"Tentative depuis machine {empreinte_actuelle}")
        return {"valide": False, "message": "Clé de licence introuvable."}

    client, date_fin_str, statut, empreinte_liee, telephone = row

    if statut == "Révoqué":
        conn.close()
        return {"valide": False, "message": f"Licence révoquée pour {client}. Contactez le fournisseur."}
    if statut == "Bloqué":
        conn.close()
        return {"valide": False, "message": f"Licence bloquée (impayé/fraude signalée) pour {client}."}

    if empreinte_liee is None:
        conn.execute("UPDATE licences SET empreinte_machine=? WHERE licence_key=?", (empreinte_actuelle, licence_key))
        conn.commit()
        _log(db_name, licence_key, "Activation machine", f"Liée à l'empreinte {empreinte_actuelle}")
    elif empreinte_liee != empreinte_actuelle:
        conn.close()
        _log(db_name, licence_key, "🚨 Machine non autorisée", f"Empreinte reçue {empreinte_actuelle} ≠ empreinte liée {empreinte_liee}")
        return {"valide": False, "message": "Cette licence est déjà activée sur une autre machine. Contactez le fournisseur pour un transfert."}

    date_fin = datetime.strptime(date_fin_str, "%Y-%m-%d")
    jours_restants = (date_fin - datetime.now()).days
    conn.close()

    if jours_restants < 0:
        conn = sqlite3.connect(db_name)
        conn.execute("UPDATE licences SET statut='Bloqué' WHERE licence_key=? AND statut='Actif'", (licence_key,))
        conn.commit(); conn.close()
        _log(db_name, licence_key, "Kill-switch auto (expiration)", f"Bloqué automatiquement — expiré depuis {abs(jours_restants)} j.")
        return {"valide": False, "message": f"Licence expirée depuis {abs(jours_restants)} jour(s). Accès bloqué automatiquement."}

    if jours_restants <= max(SEUILS_RELANCE):
        _verifier_et_envoyer_relance(db_name, licence_key, client, telephone, jours_restants)

    return {"valide": True, "message": f"Licence active — {client}", "jours_restants": jours_restants}


def bloc_verification_licence(db_name: str) -> bool:
    licence_key = st.secrets.get("LICENCE_KEY", "") if hasattr(st, "secrets") else ""
    resultat = verifier_licence_machine(db_name, licence_key)
    if not resultat["valide"]:
        st.markdown(
            f"""<div style="max-width:600px;margin:100px auto;padding:30px;background:#1E293B;
            border:1px solid #7F1D1D;border-radius:16px;text-align:center;color:#F8FAFC;">
            <h2 style="color:#F87171;">🔒 Accès Verrouillé</h2><p>{resultat['message']}</p></div>""",
            unsafe_allow_html=True,
        )
        st.stop()
    elif resultat.get("jours_restants", 999) <= 7:
        st.sidebar.warning(f"⏳ Licence expire dans {resultat['jours_restants']} jour(s).")
    return True


# ------------------------------------------------------------------
# PANNEAU FONDATEUR — caché, jamais dans le menu principal.
# Accès : ajouter ?fondateur=1 à l'URL, puis saisir le mot de passe
# stocké dans st.secrets["FOUNDER_PASSWORD"] (jamais en dur dans le code).
# ------------------------------------------------------------------
def panneau_fondateur_secret(db_name: str):
    params = st.query_params
    if params.get("fondateur") != "1":
        return

    st.markdown("## 🕵️ Panneau Fondateur — Supervision Totale")
    mdp_attendu = st.secrets.get("FOUNDER_PASSWORD", "") if hasattr(st, "secrets") else ""
    if not mdp_attendu:
        st.error("FOUNDER_PASSWORD n'est pas configuré dans les secrets — panneau désactivé.")
        return

    saisi = st.text_input("Mot de passe fondateur", type="password", key="fondateur_pwd")
    if saisi != mdp_attendu:
        if saisi:
            st.error("Mot de passe incorrect.")
        st.stop()

    init_licences_tables(db_name)
    import pandas as pd
    conn = sqlite3.connect(db_name)
    df = pd.read_sql_query("SELECT * FROM licences ORDER BY id DESC", conn)
    df_evt = pd.read_sql_query("SELECT * FROM licence_evenements ORDER BY id DESC LIMIT 300", conn)
    conn.close()

    st.markdown("#### 📊 Indicateurs Clés")
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Licences totales", len(df))
    k2.metric("Actives", len(df[df["statut"] == "Actif"]) if not df.empty else 0)
    k3.metric("Bloquées", len(df[df["statut"] == "Bloqué"]) if not df.empty else 0)
    k4.metric("Révoquées", len(df[df["statut"] == "Révoqué"]) if not df.empty else 0)
    k5.metric("Chiffre d'affaires cumulé", f"{df['montant'].sum():,.0f} FCFA" if not df.empty else "0 FCFA")

    anomalies = df_evt[df_evt["evenement"].str.contains("⚠️|🚨", na=False)] if not df_evt.empty else df_evt
    if not anomalies.empty:
        st.error(f"🚨 {len(anomalies)} anomalie(s) de sécurité détectée(s) (empreinte machine suspecte, clé invalide...).")

    st.caption(
        "ℹ️ Ce journal couvre le CYCLE DE VIE DES LICENCES (création, blocage, relance, "
        "anomalies d'empreinte machine). Les opérations métier de chaque client (transactions, "
        "dossiers douane...) restent dans la base propre à son déploiement, par cloisonnement "
        "volontaire — aucune donnée bancaire client ne transite par ce panneau."
    )

    st.markdown("---")
    st.markdown("#### ➕ Créer une nouvelle licence")
    with st.form("form_nouvelle_licence_fondateur"):
        c1, c2, c3, c4 = st.columns(4)
        with c1: nom_client = st.text_input("Nom du client")
        with c2: type_ab = st.selectbox("Abonnement", ["mensuel", "annuel", "essai"])
        with c3: montant = st.number_input("Montant (FCFA)", min_value=0.0, step=10000.0)
        with c4: tel_client = st.text_input("Téléphone client (+225...)")
        if st.form_submit_button("Générer la licence", use_container_width=True) and nom_client:
            cle = creer_licence(db_name, nom_client, type_ab, montant, tel_client)
            st.success(f"Licence créée pour **{nom_client}**")
            st.code(cle, language=None)

    st.markdown("---")
    st.markdown("#### 📋 Licences existantes")
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        cle_sel = st.selectbox("Licence à administrer", df["licence_key"].tolist())
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("⛔ Bloquer (impayé/fraude)", use_container_width=True):
                conn = sqlite3.connect(db_name)
                conn.execute("UPDATE licences SET statut='Bloqué' WHERE licence_key=?", (cle_sel,))
                conn.commit(); conn.close()
                _log(db_name, cle_sel, "Blocage fondateur", "Bloqué manuellement par le fondateur")
                st.success("Licence bloquée. Le client sera coupé à sa prochaine ouverture d'app.")
        with c2:
            if st.button("🔓 Débloquer / Réactiver", use_container_width=True):
                conn = sqlite3.connect(db_name)
                conn.execute("UPDATE licences SET statut='Actif', dernier_rappel_envoye=NULL WHERE licence_key=?", (cle_sel,))
                conn.commit(); conn.close()
                _log(db_name, cle_sel, "Réactivation fondateur", "Réactivé manuellement")
                st.success("Licence réactivée.")
        with c3:
            if st.button("🗑️ Révoquer définitivement", use_container_width=True):
                conn = sqlite3.connect(db_name)
                conn.execute("UPDATE licences SET statut='Révoqué' WHERE licence_key=?", (cle_sel,))
                conn.commit(); conn.close()
                _log(db_name, cle_sel, "Révocation fondateur", "Révoqué définitivement")
                st.error("Licence révoquée définitivement.")

        c4, c5 = st.columns(2)
        with c4:
            if st.button("🔁 Autoriser un transfert vers une nouvelle machine", use_container_width=True):
                conn = sqlite3.connect(db_name)
                conn.execute("UPDATE licences SET empreinte_machine=NULL WHERE licence_key=?", (cle_sel,))
                conn.commit(); conn.close()
                _log(db_name, cle_sel, "Déverrouillage machine", "Empreinte machine réinitialisée pour transfert")
                st.info("La licence se liera à la prochaine machine qui l'utilisera.")
        with c5:
            nouveau_type = st.selectbox("Renouveler avec", ["mensuel", "annuel", "essai"], key="renouv_type")
            if st.button("🔄 Renouveler (repart de zéro à partir d'aujourd'hui)", use_container_width=True):
                debut = datetime.now(); fin = debut + timedelta(days=DUREE_JOURS.get(nouveau_type, 30))
                conn = sqlite3.connect(db_name)
                conn.execute(
                    "UPDATE licences SET date_debut=?, date_fin=?, statut='Actif', dernier_rappel_envoye=NULL, type_abonnement=? WHERE licence_key=?",
                    (debut.strftime("%Y-%m-%d"), fin.strftime("%Y-%m-%d"), nouveau_type, cle_sel),
                )
                conn.commit(); conn.close()
                _log(db_name, cle_sel, "Renouvellement fondateur", f"Nouvelle échéance {fin.strftime('%Y-%m-%d')} ({nouveau_type})")
                st.success("Licence renouvelée.")

    st.markdown("---")
    st.markdown("#### 🕵️ Journal Complet des Événements de Licence")
    st.dataframe(df_evt, use_container_width=True)

    st.stop()
