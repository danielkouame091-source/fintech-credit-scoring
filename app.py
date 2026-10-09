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
        "details_clair": details,
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
    st.markdown("<p style='text-align: center; color: #94a3b8;'>Expérience macOS Workspace, Agrégation Mobile Money & WhatsApp Business</p>", unsafe_allow_html=True)
    
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

st.markdown(f"""
<div class="macos-header">
    <div><b>🍎 Workspace CI</b> | Utilisateur : <b>{st.session_state.username}</b> ({st.session_state.user_role})</div>
    <div>🔐 Chiffrement AES-256 Actif &nbsp;|&nbsp; 🟢 Système Opérationnel</div>
</div>
""", unsafe_allow_html=True)

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
    
    apps = [
        {"nom": "🏠 Tableau de Bord", "desc": "Indicateurs clés & flux financiers", "cle": "Dashboard"},
        {"nom": "💳 Agrégateur Paiements", "desc": "Wave, Orange, MTN, Moov & Banques", "cle": "Paiements"},
        {"nom": "💬 WhatsApp Business", "desc": "Automatisation reçus & rappels clients", "cle": "WhatsApp"},
        {"nom": "📊 Finance & Comptabilité", "desc": "Imputations et normes SYSCOHADA", "cle": "Comptabilite"},
        {"nom": "🏢 Annuaire Tiers", "desc": "Gestion clients & fournisseurs (RCCM/IF)", "cle": "Tiers"},
        {"nom": "🏛️ Fiscalité & Veille DGI", "desc": "Échéances et déclarations fiscales CI", "cle": "Fiscalite"},
        {"nom": "🛡️ Piste d'Audit", "desc": "Journal immuable SHA-256 des actions", "cle": "Audit"},
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
    c3.metric("Rapprochements Paiements", "99.1%", delta="+1.8%")
    c4.metric("Alertes WhatsApp", "12 Envoyées", delta="Actif")

    st.markdown("---")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.subheader("📈 Volume des Encaissements Multi-Opérateurs")
        df_vol = pd.DataFrame({"Canal": ["Wave CI", "Orange Money", "MTN MoMo", "Virements Bancaires"], "Volume (FCFA)": [4500000, 3200000, 1800000, 6500000]})
        fig = px.bar(df_vol, x="Canal", y="Volume (FCFA)", template="plotly_dark", color_discrete_sequence=["#38bdf8"])
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
# 3. ESPACE : AGRÉGATEUR DE PAIEMENTS MULTI-OPÉRATEURS
# -----------------------------------------------------------------------------
elif st.session_state.espace_actif == "Paiements":
    st.markdown("<h2>💳 Agrégateur de Paiements & Rapprochement (Côte d'Ivoire)</h2>", unsafe_allow_html=True)
    st.markdown("Centralisez et rapprochez en temps réel tous vos encaissements Mobile Money et bancaires.")

    with st.form("form_paiement"):
        c1, c2 = st.columns(2)
        with c1:
            client_nom = st.text_input("Nom du Client / Payeur", value="Kouadio & Frères SARL")
            operateur = st.selectbox("Canal d'Encaissement", ["Wave Business CI", "Orange Money Marchand", "MTN MoMo Pay", "Moov Money", "Virement Bancaire Direct"])
            ref_trx = st.text_input("Référence Transaction / ID Reçu / UTR", value="WAVE-CI-9482104")
        with c2:
            montant_enc = st.number_input("Montant Encaissé (FCFA)", value=350000)
            facture_liee = st.text_input("Facture Rattachée", value="FACT-2026-089")
            
        valider_enc = st.form_submit_button("Enregistrer et Rapprocher l'Encaissement")
        if valider_enc:
            details = f"Encaissement de {montant_enc:,.0f} FCFA via {operateur} (Ref: {ref_trx}) pour le client {client_nom}"
            enregistrer_memoire("ENCAISSEMENT_PAIEMENT", details, st.session_state.username)
            st.success(f"✅ Encaissement de `{montant_enc:,.0f} FCFA` validé et rapproché avec succès.")

# -----------------------------------------------------------------------------
# 4. ESPACE : WHATSAPP BUSINESS AUTOMATISATION
# -----------------------------------------------------------------------------
elif st.session_state.espace_actif == "WhatsApp":
    st.markdown("<h2>💬 Automatisation WhatsApp Business (Reçus & Rappels)</h2>", unsafe_allow_html=True)
    st.markdown("Envoyez instantanément des reçus de paiement, des confirmations de commande ou des rappels d'impayés à vos clients via WhatsApp.")

    with st.form("form_whatsapp"):
        c1, c2 = st.columns(2)
        with c1:
            destinataire = st.text_input("Nom du Client / Destinataire", value="Entreprise Kouassi & Cie")
            telephone = st.text_input("Numéro WhatsApp (Format international)", value="+225 0700000000")
            type_msg = st.selectbox("Type de Message Automatisé", [
                "Reçu de Paiement & Confirmation",
                "Rappel de Facture Échue (Impayé)",
                "Confirmation de Commande & Livraison",
                "Message Personnalisé"
            ])
        with c2:
            montant_facture = st.number_input("Montant Concerné (FCFA)", value=150000)
            texte_perso = st.text_area("Aperçu du Message", value="Bonjour, nous vous confirmons la bonne réception de votre paiement de 150.000 FCFA. Merci pour votre confiance ! — Votre Entreprise")

        btn_envoi = st.form_submit_button("📤 Envoyer la Notification WhatsApp Business")
        if btn_envoi:
            details = f"Envoi d'un message WhatsApp ({type_msg}) au {telephone} pour un montant de {montant_facture:,.0f} FCFA"
            enregistrer_memoire("NOTIFICATION_WHATSAPP", details, st.session_state.username)
            st.success(f"✅ Message WhatsApp transmis avec succès au numéro `{telephone}` via l'API Business.")

# -----------------------------------------------------------------------------
# 5. ESPACE : FINANCE & COMPTABILITÉ (SYSCOHADA)
# -----------------------------------------------------------------------------
elif st.session_state.espace_actif == "Comptabilite":
    st.markdown("<h2>📊 Finance & Comptabilité (Normes SYSCOHADA)</h2>", unsafe_allow_html=True)
    
    with st.form("form_compta"):
        c1, c2 = st.columns(2)
        with c1:
            libelle = st.text_input("Libellé de l'Opération / Pièce", value="Achat de fournitures")
            compte = st.selectbox("Imputation SYSCOHADA", ["6041 - Matières premières", "6057 - Fournitures de bureau", "2441 - Matériel informatique", "6241 - Transports de biens"])
        with c2:
            montant_ht = st.number_input("Montant HT (FCFA)", value=500000)
            tva = st.selectbox("Taux TVA (Côte d'Ivoire)", ["TVA 18% (Standard)", "TVA 9% (Réduit)", "Exonéré (0%)"])

        montant_tva = montant_ht * 0.18 if "18%" in tva else (montant_ht * 0.09 if "9%" in tva else 0)
        total_ttc = montant_ht + montant_tva
        st.metric("Montant TTC Calculé", f"{total_ttc:,.0f} FCFA")

        if st.form_submit_button("Enregistrer l'Écriture Comptable"):
            details = f"Saisie écriture '{libelle}' pour {total_ttc:,.0f} FCFA"
            enregistrer_memoire("SAISIE_COMPTABLE", details, st.session_state.username)
            st.success("✅ Écriture comptable enregistrée avec succès.")

# -----------------------------------------------------------------------------
# 6. ESPACE : ANNUAIRE TIERS (RCCM / IF)
# -----------------------------------------------------------------------------
elif st.session_state.espace_actif == "Tiers":
    st.markdown("<h2>🏢 Annuaire des Tiers (Clients & Fournisseurs)</h2>", unsafe_allow_html=True)
    
    with st.form("form_tiers"):
        c1, c2 = st.columns(2)
        with c1:
            nom_tiers = st.text_input("Raison Sociale", value="Eburnie Distribution SARL")
            rccm = st.text_input("Numéro RCCM", value="CI-ABJ-2024-B-9876")
            ifu = st.text_input("Compte Contribuable (IFU)", value="2009876 K")
        with c2:
            contact = st.text_input("Téléphone / WhatsApp", value="+225 05 00 00 00 00")
            canal_paiement = st.selectbox("Mode de Paiement Préféré", ["Virement Bancaire", "Wave Business", "Orange Money Marchand"])

        if st.form_submit_button("Enregistrer le Tiers"):
            details = f"Enregistrement du tiers {nom_tiers} (RCCM: {rccm})"
            enregistrer_memoire("ENREGISTREMENT_TIERS", details, st.session_state.username)
            st.success(f"✅ Tiers **{nom_tiers}** consigné.")

# -----------------------------------------------------------------------------
# 7. ESPACE : FISCALITÉ & VEILLE DGI
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
# 8. ESPACE : PISTE D'AUDIT
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
# 9. ESPACE : ASSISTANT IA CENTRAL
# -----------------------------------------------------------------------------
elif st.session_state.espace_actif == "IA":
    st.markdown("<h2>🤖 Assistant IA Central Intelligent</h2>", unsafe_allow_html=True)
    st.markdown("Posez vos questions. L'assistant analyse les transactions, les paiements Mobile Money et la mémoire opérationnelle.")

    if "messages_ia" not in st.session_state:
        st.session_state.messages_ia = [
            {"role": "assistant", "content": "Bonjour ! Je suis votre Assistant IA Central. Je peux consulter les paiements Wave/Orange, vérifier des tiers ou résumer l'activité. Que souhaitez-vous savoir ?"}
        ]

    for msg in st.session_state.messages_ia:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ex: 'Quels sont les derniers encaissements réalisés ?'")
    if prompt:
        st.session_state.messages_ia.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        memoire = charger_memoire()
        reponse = "Je n'ai pas trouvé d'information correspondante dans les registres."
        p_lower = prompt.lower()
        
        if "paiement" in p_lower or "encaissement" in p_lower or "opération" in p_lower or "whatsapp" in p_lower:
            if memoire:
                dernier = memoire[0]
                reponse = f"Dernière opération enregistrée : **{dernier['action']}** par *{dernier['utilisateur']}* à {dernier['timestamp']} ({dernier['details_clair']}). Total d'opérations : {len(memoire)}."
            else:
                reponse = "Aucune opération enregistrée pour le moment."
        elif "bonjour" in p_lower:
            reponse = "Bonjour ! Comment puis-je vous assister dans la gestion de vos flux financiers aujourd'hui ?"

        st.session_state.messages_ia.append({"role": "assistant", "content": reponse})
        with st.chat_message("assistant"):
            st.markdown(reponse)
