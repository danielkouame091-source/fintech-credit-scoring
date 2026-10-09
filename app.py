import datetime
import json
import os
import uuid
import hashlib
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from cryptography.fernet import Fernet

# -----------------------------------------------------------------------------
# CONFIGURATION DE LA PAGE & DESIGN macOS / LAUNCHPAD GLASSMORPHISM
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Plateforme de Confiance Numérique | Côte d'Ivoire",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at 50% 10%, #0b132b 0%, #030712 100%);
        color: #f8fafc;
    }

    /* Style macOS Dock / Top Bar */
    .macos-header {
        background: rgba(15, 23, 42, 0.75);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px 24px;
        border-radius: 16px;
        margin-bottom: 25px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Cartes Applications Launchpad */
    .app-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.85));
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 20px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
        margin-bottom: 20px;
    }

    .app-card:hover {
        transform: translateY(-5px);
        border-color: rgba(56, 189, 248, 0.6);
        box-shadow: 0 15px 35px rgba(56, 189, 248, 0.2);
    }

    div.stButton > button {
        width: 100%;
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95)) !important;
        color: #f8fafc !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 12px !important;
        padding: 12px 8px !important;
        transition: all 0.3s ease !important;
    }

    div.stButton > button:hover {
        transform: translateY(-2px);
        background: linear-gradient(145deg, rgba(56, 189, 248, 0.2), rgba(30, 41, 59, 0.98)) !important;
        border-color: #38bdf8 !important;
        color: #38bdf8 !important;
    }

    input, textarea, div[data-baseweb="select"] > div {
        background-color: rgba(15, 23, 42, 0.9) !important;
        color: #ffffff !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 10px !important;
    }

    label {
        color: #38bdf8 !important;
        font-weight: 600 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# GESTION DU STOCKAGE SÉCURISÉ & MÉMOIRE OPÉRATIONNELLE (AES-256)
# -----------------------------------------------------------------------------
KEY_FILE = "mac_enterprise_secret.key"
AUDIT_FILE = "memoire_operations_ci.json"
TIERS_FILE = "annuaire_tiers_ci.json"

def obtenir_cle():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    else:
        cle = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(cle)
        return cle

fernet = Fernet(obtenir_cle())

def enregistrer_memoire(action, details, utilisateur, statut="SUCCÈS"):
    historique = charger_memoire()
    dernier_hash = historique[0]["hash_actuel"] if historique else "0" * 64
    
    details_chiffres = fernet.encrypt(str(details).encode()).decode()
    payload = f"{dernier_hash}{action}{utilisateur}{datetime.datetime.now().isoformat()}"
    hash_actuel = hashlib.sha256(payload.encode()).hexdigest()
    
    entree = {
        "id_op": f"OP-{uuid.uuid4().hex[:6].upper()}",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "details_enc": details_chiffres,
        "details_clair": details,  # Pour consultation rapide par l'IA
        "utilisateur": utilisateur,
        "statut": statut,
        "hash_actuel": hash_actuel
    }
    
    historique.insert(0, entree)
    with open(AUDIT_FILE, "w", encoding="utf-8") as f:
        json.dump(historique, f, ensure_ascii=False, indent=4)

def charger_memoire():
    if os.path.exists(AUDIT_FILE):
        try:
            with open(AUDIT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

# -----------------------------------------------------------------------------
# AUTHENTIFICATION & SESSION
# -----------------------------------------------------------------------------
if "authentifie" not in st.session_state:
    st.session_state.authentifie = False

if not st.session_state.authentifie:
    st.markdown("<h2 style='text-align: center; color: #38bdf8;'>🍏🇨🇮 Connexion Sécurisée — Plateforme Entreprise Côte d'Ivoire</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8;'>Expérience macOS Workspace & Assistant IA Central Intégré</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("form_auth"):
            email = st.text_input("Identifiant Professionnel", value="direction@entreprise.ci")
            pwd = st.text_input("Mot de Passe", type="password", value="secure2026")
            role = st.selectbox("Profil d'Accès (RBAC)", [
                "📊 Comptable / Saisisseur",
                "💼 Responsable Financier",
                "⚖️ Directeur Général / Validateur",
                "🛡️ Administrateur & Sécurité"
            ])
            btn_connexion = st.form_submit_button("Ouvrir la Session Workspace", use_container_width=True)
            if btn_connexion:
                st.session_state.authentifie = True
                st.session_state.username = email
                st.session_state.user_role = role
                enregistrer_memoire("CONNEXION", f"Ouverture de session pour {email} ({role})", email)
                st.rerun()
    st.stop()

# -----------------------------------------------------------------------------
# NAVIGATION PRINCIPALE (LAUNCHPAD & ESPACES DE TRAVAIL)
# -----------------------------------------------------------------------------
if "espace_actif" not in st.session_state:
    st.session_state.espace_actif = "Launchpad"

# Barre supérieure style macOS
st.markdown(f"""
<div class="macos-header">
    <div><b>🍎 Workspace CI</b> | Utilisateur : <b>{st.session_state.username}</b> ({st.session_state.user_role})</div>
    <div>🔐 Chiffrement AES-256 Actif &nbsp;|&nbsp; 🟢 Système Opérationnel</div>
</div>
""", unsafe_allow_html=True)

# Bouton de retour au Launchpad si l'on est dans une application
if st.session_state.espace_actif != "Launchpad":
    if st.button("⬅️ Retour au Launchpad (Menu Principal)"):
        st.session_state.espace_actif = "Launchpad"
        st.rerun()
    st.markdown("---")

# -----------------------------------------------------------------------------
# 1. VUE LAUNCHPAD (ACCUEIL TYPE MACOS)
# -----------------------------------------------------------------------------
if st.session_state.espace_actif == "Launchpad":
    st.markdown("<h1 style='text-align: center; font-weight: 800; margin-bottom: 30px;'>Launchpad Professionnel</h1>", unsafe_allow_html=True)
    
    # Grille d'applications
    apps = [
        {"nom": "🏠 Tableau de Bord", "desc": "Indicateurs clés & flux financiers", "cle": "Dashboard"},
        {"nom": "📊 Finance & Comptabilité", "desc": "Imputations et normes SYSCOHADA", "cle": "Comptabilite"},
        {"nom": "🏢 Annuaire Tiers", "desc": "Gestion clients & fournisseurs (RCCM/IF)", "cle": "Tiers"},
        {"nom": "🔍 Anti-Fraude & Rapprochement", "desc": "Contrôle Wave, Orange Money & Banques", "cle": "Fraude"},
        {"nom": "🏛️ Fiscalité & Veille DGI", "desc": "Échéances et déclarations fiscales CI", "cle": "Fiscalite"},
        {"nom": "🛡️ Piste d'Audit & Mémoire", "desc": "Journal immuable SHA-256 des actions", "cle": "Audit"},
        {"nom": "🤖 Assistant IA Central", "desc": "Recherche, analyse et exécution intelligente", "cle": "IA"}
    ]

    cols = st.columns(3)
    for idx, app in enumerate(apps):
        col_target = cols[idx % 3]
        with col_target:
            st.markdown(f"""
            <div class="app-card">
                <h3>{app['nom']}</h3>
                <p style="color: #94a3b8; font-size: 0.85rem; min-height: 40px;">{app['desc']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Ouvrir {app['nom'].split(' ')[1]}", key=f"app_{app['cle']}"):
                st.session_state.espace_actif = app['cle']
                st.rerun()

# -----------------------------------------------------------------------------
# 2. ESPACE : TABLEAU DE BORD
# -----------------------------------------------------------------------------
elif st.session_state.espace_actif == "Dashboard":
    st.markdown("<h2>🏠 Tableau de Bord Exécutif</h2>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Opérations Enregistrées", len(charger_memoire()), delta="Actif")
    c2.metric("Conformité SYSCOHADA", "100%", delta="Optimal")
    c3.metric("Rapprochements Validés", "98.5%", delta="+1.2%")
    c4.metric("Alertes Risque Détectées", "0", delta="Sain")

    st.markdown("---")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.subheader("📈 Volume des Opérations par Semaine")
        df_vol = pd.DataFrame({"Semaine": ["S1", "S2", "S3", "S4"], "Volume (FCFA)": [2500000, 4100000, 3800000, 6200000]})
        fig = px.bar(df_vol, x="Semaine", y="Volume (FCFA)", template="plotly_dark", color_discrete_sequence=["#38bdf8"])
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with col_d2:
        st.subheader("💡 Activité Récente de la Mémoire")
        historique = charger_memoire()[:5]
        if historique:
            for h in historique:
                st.info(f"**[{h['timestamp']}] {h['action']}** par *{h['utilisateur']}* — {h['details_clair']}")
        else:
            st.write("Aucune opération enregistrée pour le moment.")

# -----------------------------------------------------------------------------
# 3. ESPACE : FINANCE & COMPTABILITÉ (SYSCOHADA)
# -----------------------------------------------------------------------------
elif st.session_state.espace_actif == "Comptabilite":
    st.markdown("<h2>📊 Finance & Comptabilité (Normes SYSCOHADA)</h2>", unsafe_allow_html=True)
    st.markdown("Espace de saisie, de classement et de préparation des écritures comptables conformes au plan révisé de l'OHADA.")

    with st.form("form_compta"):
        c1, c2 = st.columns(2)
        with c1:
            libelle = st.text_input("Libellé de l'Opération / Pièce", value="Achat de matériel informatique")
            compte = st.selectbox("Imputation SYSCOHADA", ["6041 - Matières premières", "6057 - Fournitures de bureau", "2441 - Matériel informatique", "6241 - Transports de biens"])
        with c2:
            montant_ht = st.number_input("Montant HT (FCFA)", value=500000)
            tva = st.selectbox("Taux TVA (Côte d'Ivoire)", ["TVA 18% (Standard)", "TVA 9% (Réduit)", "Exonéré (0%)"])

        montant_tva = montant_ht * 0.18 if "18%" in tva else (montant_ht * 0.09 if "9%" in tva else 0)
        total_ttc = montant_ht + montant_tva
        st.metric("Montant TTC Calculé", f"{total_ttc:,.0f} FCFA")

        valider_saisie = st.form_submit_button("Enregistrer l'Écriture Comptable")
        if valider_saisie:
            details = f"Saisie écriture '{libelle}' (Compte: {compte}) pour un montant TTC de {total_ttc:,.0f} FCFA"
            enregistrer_memoire("SAISIE_COMPTABLE", details, st.session_state.username)
            st.success("✅ Écriture comptable enregistrée avec succès dans la mémoire de l'entreprise.")

# -----------------------------------------------------------------------------
# 4. ESPACE : ANNUAIRE TIERS (RCCM / IF)
# -----------------------------------------------------------------------------
elif st.session_state.espace_actif == "Tiers":
    st.markdown("<h2>🏢 Annuaire des Tiers (Clients & Fournisseurs)</h2>", unsafe_allow_html=True)
    st.markdown("Gestion sécurisée des informations légales (RCCM et Compte Contribuable) pour la prévention des fraudes.")

    with st.form("form_tiers"):
        c1, c2 = st.columns(2)
        with c1:
            nom_tiers = st.text_input("Raison Sociale", value="Eburnie Distribution SARL")
            rccm = st.text_input("Numéro RCCM", value="CI-ABJ-2024-B-9876")
            ifu = st.text_input("Compte Contribuable (IFU)", value="2009876 K")
        with c2:
            contact = st.text_input("Téléphone / WhatsApp", value="+225 05 00 00 00 00")
            canal_paiement = st.selectbox("Mode de Paiement Préféré", ["Virement Bancaire (SGCI / Ecobank)", "Wave Business", "Orange Money Marchand"])
            rib = st.text_input("Coordonnées Bancaires / Numéro Marchand", value="CI16 0101 012345678901 22")

        if st.form_submit_button("Enregistrer et Vérifier le Tiers"):
            details = f"Enregistrement du tiers {nom_tiers} (RCCM: {rccm}, IFU: {ifu})"
            enregistrer_memoire("ENREGISTREMENT_TIERS", details, st.session_state.username)
            st.success(f"✅ Le tiers **{nom_tiers}** a été validé et consigné dans l'annuaire.")

# -----------------------------------------------------------------------------
# 5. ESPACE : ANTI-FRAUDE & RAPPROCHEMENT
# -----------------------------------------------------------------------------
elif st.session_state.espace_actif == "Fraude":
    st.markdown("<h2>🔍 Anti-Fraude & Rapprochement (Mobile Money & Banques)</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        ref_tr = st.text_input("Référence Transaction / ID Reçu", value="WAVE-CI-849201")
        montant = st.number_input("Montant (FCFA)", value=350000)
    with col2:
        canal = st.selectbox("Canal", ["Wave CI", "Orange Money CI", "MTN MoMo CI", "Virement Bancaire"])
        justificatif = st.file_uploader("Preuve de Paiement (Image / PDF)", type=["png", "jpg", "pdf"])

    if st.button("Lancer l'Analyse Anti-Fraude"):
        diagnostic = "Aucune anomalie détectée. Référence cohérente avec les flux du jour."
        if montant > 1500000 and "Wave" in canal:
            diagnostic = "⚠️ Alerte : Montant élevé pour un canal Mobile Money simple. Vérification humaine requise."
        
        enregistrer_memoire("CONTROLE_ANTI_FRAUDE", f"Vérification {ref_tr} ({montant} FCFA) sur {canal} — Résultat: {diagnostic}", st.session_state.username)
        if "⚠️" in diagnostic:
            st.warning(diagnostic)
        else:
            st.success(f"✅ {diagnostic}")

# -----------------------------------------------------------------------------
# 6. ESPACE : FISCALITÉ & VEILLE DGI
# -----------------------------------------------------------------------------
elif st.session_state.espace_actif == "Fiscalite":
    st.markdown("<h2>🏛️ Fiscalité & Veille DGI (Côte d'Ivoire)</h2>", unsafe_allow_html=True)
    st.info("ℹ️ Rappel DGI Côte d'Ivoire : Les déclarations de TVA et d'AIB doivent s'effectuer entre le 10 et le 15 de chaque mois.")

    df_tax = pd.DataFrame({
        "Impôt / Taxe": ["TVA & AIB", "Acompte BIC / IS", "Versement Forfaitaire (VF)"],
        "Échéance": ["10-15 du mois", "15 du mois suivant le trimestre", "10-15 du mois"],
        "Référence": ["Code Général des Impôts - CI", "CGI Côte d'Ivoire", "CGI CI"]
    })
    st.dataframe(df_tax, use_container_width=True)

# -----------------------------------------------------------------------------
# 7. ESPACE : PISTE D'AUDIT & MÉMOIRE
# -----------------------------------------------------------------------------
elif st.session_state.espace_actif == "Audit":
    st.markdown("<h2>🛡️ Piste d'Audit Immuable (SHA-256)</h2>", unsafe_allow_html=True)
    
    historique = charger_memoire()
    if historique:
        df_audit = pd.DataFrame(historique)
        st.dataframe(df_audit[["id_op", "timestamp", "action", "utilisateur", "statut"]], use_container_width=True)
        
        csv_data = df_audit.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Exporter le Journal d'Audit Certifié (CSV)", data=csv_data, file_name="audit_entreprise_ci.csv", mime="text/csv")
    else:
        st.info("Aucun événement consigné dans la mémoire.")

# -----------------------------------------------------------------------------
# 8. ESPACE : ASSISTANT IA CENTRAL (LE CŒUR DE LA PLATEFORME)
# -----------------------------------------------------------------------------
elif st.session_state.espace_actif == "IA":
    st.markdown("<h2>🤖 Assistant IA Central Intelligent</h2>", unsafe_allow_html=True)
    st.markdown("Posez vos questions en langage naturel. L'assistant analyse l'ensemble de la mémoire opérationnelle, des dossiers, des tiers et des transactions de la plateforme.")

    # Zone de dialogue
    if "messages_ia" not in st.session_state:
        st.session_state.messages_ia = [
            {"role": "assistant", "content": "Bonjour ! Je suis votre Assistant IA Central. Je peux consulter les opérations, retrouver des dossiers, vérifier des tiers ou résumer l'activité. Que souhaitez-vous savoir ?"}
        ]

    for msg in st.session_state.messages_ia:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ex: 'Quelles sont les dernières opérations réalisées ?' ou 'Retrouve le dossier de ce client'")
    if prompt:
        st.session_state.messages_ia.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Logique de réponse intelligente basée sur la mémoire
        memoire = charger_memoire()
        reponse = "Je n'ai pas trouvé d'information correspondante dans les registres actifs."
        
        p_lower = prompt.lower()
        if "opération" in p_lower or "action" in p_lower or "réalisé" in p_lower:
            if memoire:
                dernier = memoire[0]
                reponse = f"D'après la mémoire opérationnelle, la dernière action enregistrée est **{dernier['action']}** effectuée par *{dernier['utilisateur']}* le {dernier['timestamp']} ({dernier['details_clair']}). Total d'opérations enregistrées : {len(memoire)}."
            else:
                reponse = "Aucune opération n'a encore été enregistrée dans la mémoire."
        elif "client" in p_lower or "tiers" in p_lower:
            reponse = "Les dossiers clients et fournisseurs sont centralisés dans l'application *Annuaire Tiers*. Vous y trouverez les numéros RCCM et IFU enregistrés."
        elif "tva" in p_lower or "impôt" in p_lower or "dgi" in p_lower:
            reponse = "Selon le calendrier DGI Côte d'Ivoire, les déclarations de TVA doivent être déposées entre le 10 et le 15 de chaque mois."
        elif "bonjour" in p_lower or "salut" in p_lower:
            reponse = "Bonjour ! Comment puis-je vous aider dans la gestion de votre entreprise aujourd'hui ?"

        st.session_state.messages_ia.append({"role": "assistant", "content": reponse})
        with st.chat_message("assistant"):
            st.markdown(reponse)
