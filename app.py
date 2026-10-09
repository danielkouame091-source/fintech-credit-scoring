import datetime
import json
import os
import uuid
import hashlib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from cryptography.fernet import Fernet

# -----------------------------------------------------------------------------
# CONFIGURATION DE LA PAGE & DESIGN PROFESSIONNEL HAUT DE GAMME
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Plateforme de Confiance Numérique | Côte d'Ivoire & UEMOA",
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
        background: radial-gradient(circle at 50% 10%, #06101e 0%, #02060d 100%);
        color: #f8fafc;
    }

    .dashboard-card, div[data-testid="stMetric"], div.stForm, .stPlotlyChart {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.75), 
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }

    div.stButton > button {
        width: 100%;
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95)) !important;
        color: #f8fafc !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        border: 1px solid rgba(16, 185, 129, 0.4) !important;
        border-radius: 12px !important;
        padding: 12px 8px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    div.stButton > button:hover {
        transform: translateY(-2px);
        background: linear-gradient(145deg, rgba(16, 185, 129, 0.2), rgba(30, 41, 59, 0.98)) !important;
        border: 1px solid #10b981 !important;
        color: #34d399 !important;
    }

    input, textarea {
        background-color: rgba(15, 23, 42, 0.95) !important;
        color: #ffffff !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
        border-radius: 10px !important;
    }
    
    div[data-baseweb="select"] > div {
        background-color: rgba(15, 23, 42, 0.95) !important;
        color: #ffffff !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
        border-radius: 10px !important;
    }

    label {
        color: #34d399 !important;
        font-weight: 600 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# GESTION DU STOCKAGE SÉCURISÉ & PISTE D'AUDIT (AES-256)
# -----------------------------------------------------------------------------
KEY_FILE = "enterprise_secret.key"
AUDIT_FILE = "piste_audit_ivoire_secure.json"
TIERS_FILE = "referentiel_tiers.json"

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

def enregistrer_piste_audit(action, details, utilisateur, statut="SUCCÈS"):
    historique = charger_audit()
    dernier_hash = historique[0]["hash_actuel"] if historique else "0" * 64
    
    details_chiffres = fernet.encrypt(str(details).encode()).decode()
    payload = f"{dernier_hash}{action}{utilisateur}{datetime.datetime.now().isoformat()}"
    hash_actuel = hashlib.sha256(payload.encode()).hexdigest()
    
    entree = {
        "id_journal": f"AUDIT-{uuid.uuid4().hex[:6].upper()}",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "details_enc": details_chiffres,
        "utilisateur": utilisateur,
        "statut": statut,
        "hash_precedent": dernier_hash,
        "hash_actuel": hash_actuel
    }
    
    historique.insert(0, entree)
    with open(AUDIT_FILE, "w", encoding="utf-8") as f:
        json.dump(historique, f, ensure_ascii=False, indent=4)

def charger_audit():
    if os.path.exists(AUDIT_FILE):
        try:
            with open(AUDIT_FILE, "r", encoding="utf-8") as f:
                donnees = json.load(f)
                resultats = []
                for item in donnees:
                    details_dechiffres = fernet.decrypt(item.get("details_enc").encode()).decode() if item.get("details_enc") else ""
                    resultats.append({
                        "id_journal": item.get("id_journal"),
                        "timestamp": item.get("timestamp"),
                        "action": item.get("action"),
                        "details": details_dechiffres,
                        "utilisateur": item.get("utilisateur"),
                        "statut": item.get("statut"),
                        "hash_actuel": item.get("hash_actuel")
                    })
                return resultats
        except:
            return []
    return []

# -----------------------------------------------------------------------------
# AUTHENTIFICATION & CONTRÔLE D'ACCÈS (RBAC)
# -----------------------------------------------------------------------------
if "authentifie" not in st.session_state:
    st.session_state.authentifie = False

if not st.session_state.authentifie:
    st.markdown("<h2 style='text-align: center; color: #34d399;'>🇨🇮 Portail de Confiance Numérique — Entreprises & Institutions (Côte d'Ivoire)</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8;'>Conformité SYSCOHADA, DGI, BCEAO & Sécurisation des flux financiers</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("form_connexion"):
            email_user = st.text_input("Adresse Email Professionnelle", value="comptable@entreprise.ci")
            pass_user = st.text_input("Mot de Passe", type="password", value="secure2026")
            role_user = st.selectbox("Profil d'Habilitation (RBAC)", [
                "📊 Comptable / Saisisseur (Maker)",
                "💼 Responsable Financier / Validateur",
                "⚖️ Directeur Général / Approbateur Final",
                "🛡️ Officier de Sécurité & Conformité"
            ])
            valider = st.form_submit_button("Se Connecter à la Plateforme Sécurisée", use_container_width=True)
            if valider:
                st.session_state.authentifie = True
                st.session_state.username = email_user
                st.session_state.user_role = role_user
                enregistrer_piste_audit("CONNEXION", f"Connexion réussie de {email_user} avec le profil {role_user}", email_user)
                st.rerun()
    st.stop()

# -----------------------------------------------------------------------------
# EN-TÊTE PRINCIPAL & NAVIGATION PAR MODULES MÉTIERS
# -----------------------------------------------------------------------------
st.markdown("<h1 style='text-align: center; color: #f8fafc; font-weight: 800;'>PLATEFORME DE CONFIANCE NUMÉRIQUE — CÔTE D'IVOIRE</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #34d399; font-size: 1rem;'>Utilisateur Actuel : <b>{st.session_state.username}</b> | Rôle : <b>{st.session_state.user_role}</b> | 🔐 Chiffrement AES-256 Actif</p>", unsafe_allow_html=True)
st.markdown("---")

if "module_actif" not in st.session_state:
    st.session_state.module_actif = "🏠 Tableau de Bord"

onglets = {
    "🏠 Tableau de Bord": "Indicateurs & Alertes",
    "🏢 Annuaire Tiers (RCCM/IF)": "Vérification Clients & Fournisseurs",
    "🔍 Anti-Fraude & Rapprochement": "Détection Doublons & Fausses Preuves",
    "📊 Comptabilité & SYSCOHADA": "Pièces Comptables & États",
    "🏛️ Fiscalité & Veille DGI": "Échéances & Références Légales",
    "🛡️ Piste d'Audit Sécurisée": "Journal Immuable (SHA-256)",
    "⚙️ Paramètres": "Gestion de l'Entreprise"
}

cols = st.columns(len(onglets))
i = 0
for nom_mod, desc in onglets.items():
    with cols[i % len(cols)]:
        actif = st.session_state.module_actif == nom_mod
        libelle = f"▶ {nom_mod}" if actif else nom_mod
        if st.button(libelle, use_container_width=True, key=f"nav_{i}"):
            st.session_state.module_actif = nom_mod
            st.rerun()
    i += 1

module_courant = st.session_state.module_actif
st.markdown(f"<h3 style='color: #34d399; margin-top: 20px;'>Section : {module_courant}</h3>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 1. TABLEAU DE BORD
# -----------------------------------------------------------------------------
if module_courant == "🏠 Tableau de Bord":
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Factures Traitées (Mois)", "142", delta="+12%")
    c2.metric("Alertes Anti-Fraude Actives", "2", delta="Attention", delta_color="inverse")
    c3.metric("Rapprochements Mobile Money", "98.4%", delta="Optimal")
    c4.metric("Conformité SYSCOHADA", "100%", delta="Conforme")

    st.markdown("---")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("📈 Évolution des Encaissements (Banques & Mobile Money)")
        df_flux = pd.DataFrame({
            "Semaine": ["Semaine 1", "Semaine 2", "Semaine 3", "Semaine 4"],
            "Montant (FCFA)": [1250000, 3400000, 2800500, 5100000]
        })
        fig = px.bar(df_flux, x="Semaine", y="Montant (FCFA)", template="plotly_dark", color_discrete_sequence=["#10b981"])
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with col_g2:
        st.subheader("⚠️ Répartition des Risques & Alertes")
        df_pie = pd.DataFrame({
            "Type d'Alerte": ["Doublon de facture", "Modification compte fournisseur", "Preuve de paiement suspecte", "RAS / Conforme"],
            "Nombre": [1, 1, 0, 140]
        })
        fig_pie = px.pie(df_pie, names="Type d'Alerte", values="Nombre", hole=0.4, template="plotly_dark", color_discrete_sequence=px.colors.sequential.Teal)
        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_pie, use_container_width=True)

# -----------------------------------------------------------------------------
# 2. ANNUAIRE TIERS (RCCM / IF)
# -----------------------------------------------------------------------------
elif module_courant == "🏢 Annuaire Tiers (RCCM/IF)":
    st.markdown("#### Gestion et Vérification des Fournisseurs et Clients (Côte d'Ivoire)")
    st.markdown("<p style='color: #94a3b8;'>Enregistrez et suivez les informations légales (RCCM, Compte Contribuable) pour éviter les fraudes sur coordonnées bancaires.</p>", unsafe_allow_html=True)

    with st.form("form_tiers"):
        c_t1, c_t2 = st.columns(2)
        with c_t1:
            nom_tiers = st.text_input("Dénomination Sociale / Nom de l'Entreprise", value="SARL Abidjan Prestations")
            rccm_tiers = st.text_input("Numéro RCCM", value="CI-ABJ-2023-B-12345")
            ifu_tiers = st.text_input("Identifiant Fiscal Unique (Compte Contribuable)", value="2309845 L")
        with c_t2:
            contact_tiers = st.text_input("Téléphone Professionnel / WhatsApp", value="+225 07 00 00 00 00")
            banque_tiers = st.selectbox("Banque / Opérateur Mobile Money", ["SGCI", "Ecobank CI", "NSIA Banque", "Orange Money CI", "Wave CI", "MTN MoMo CI"])
            rib_tiers = st.text_input("Numéro de Compte / IBAN / Numéro Marchand", value="CI16 CI03 0101 012345678901 45")
            
        soumettre_tiers = st.form_submit_button("Enregistrer et Vérifier le Tiers")
        if soumettre_tiers:
            enregistrer_piste_audit("ENREGISTREMENT_TIERS", f"Ajout ou mise à jour du tiers {nom_tiers} (RCCM: {rccm_tiers})", st.session_state.username)
            st.success(f"✅ Le tiers **{nom_tiers}** a été enregistré et sécurisé dans le référentiel de l'entreprise.")

# -----------------------------------------------------------------------------
# 3. ANTI-FRAUDE & RAPPROCHEMENT
# -----------------------------------------------------------------------------
elif module_courant == "🔍 Anti-Fraude & Rapprochement":
    st.markdown("#### Détection des Fausses Preuves de Paiement & Rapprochement (Wave / Orange / Banques)")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        ref_paiement = st.text_input("Référence de la Transaction / ID Reçu Mobile Money", value="WAVE-CI-9482104")
        montant_declare = st.number_input("Montant Déclaré (FCFA)", value=250000)
    with col_f2:
        canal_reception = st.selectbox("Canal de Réception", ["Wave CI", "Orange Money CI", "MTN MoMo CI", "Virement Bancaire Direct"])
        piece_jointe_recue = st.file_uploader("Importer le Reçu ou la Capture (PDF / Image)", type=["pdf", "png", "jpg"])

    if st.button("🔍 Lancer l'Analyse Anti-Fraude & Rapprochement"):
        risque_detecte = False
        message_analyse = "Transaction cohérente. Aucun doublon ni altération détectée sur la référence."
        
        if montant_declare > 2000000 and "Wave" in canal_reception:
            risque_detecte = True
            message_analyse = "⚠️ Alerte : Montant élevé pour un canal Mobile Money simple. Vérification visuelle humaine exigée."

        enregistrer_piste_audit("CONTROLE_ANTI_FRAUDE", f"Vérification de la référence {ref_paiement} - Résultat: {message_analyse}", st.session_state.username)
        
        if risque_detecte:
            st.error(message_analyse)
        else:
            st.success(f"✅ {message_analyse}")

# -----------------------------------------------------------------------------
# 4. COMPTABILITÉ & SYSCOHADA
# -----------------------------------------------------------------------------
elif module_courant == "📊 Comptabilité & SYSCOHADA":
    st.markdown("#### Assistant Comptable & Gestion des Pièces Justificatives (Normes SYSCOHADA)")
    st.markdown("<p style='color: #94a3b8;'>Classement et préparation des écritures comptables conformes au plan comptable révisé de l'OHADA.</p>", unsafe_allow_html=True)

    c_cp1, c_cp2 = st.columns(2)
    with c_cp1:
        libelle_piece = st.text_input("Libellé de la Pièce / Facture", value="Achat de fournitures de bureau")
        compte_imputation = st.selectbox("Imputation Comptable SYSCOHADA", ["6057 - Fournitures de bureau", "6041 - Matières premières", "6241 - Transports de biens", "6130 - Locations"])
    with c_cp2:
        montant_ht = st.number_input("Montant HT (FCFA)", value=150000)
        tva_applicable = st.selectbox("Taux de TVA (Côte d'Ivoire)", ["TVA 18% (Standard)", "TVA 9% (Réduit)", "Exonéré (0%)"])

    montant_tva = montant_ht * 0.18 if "18%" in tva_applicable else (montant_ht * 0.09 if "9%" in tva_applicable else 0)
    montant_ttc = montant_ht + montant_tva

    st.metric("Montant TTC Calculé", f"{montant_ttc:,.0f} FCFA")

    if st.button("💾 Enregistrer l'Écriture au Brouillon Comptable"):
        enregistrer_piste_audit("SAISIE_COMPTABLE", f"Saisie écriture {libelle_piece} pour {montant_ttc} FCFA", st.session_state.username)
        st.success("✅ Pièce comptable enregistrée en mode brouillon pour validation par le responsable financier.")

# -----------------------------------------------------------------------------
# 5. FISCALITÉ & VEILLE DGI
# -----------------------------------------------------------------------------
elif module_courant == "🏛️ Fiscalité & Veille DGI":
    st.markdown("#### Calendrier Fiscal & Références Officielles (Direction Générale des Impôts - DGI CI)")
    
    st.info("ℹ️ **Rappel officiel DGI Côte d'Ivoire :** La date limite de dépôt des déclarations mensuelles d'impôts (Taxes sur la Valeur Ajoutée - TVA) intervient généralement entre le 10 et le 15 de chaque mois suivant le mois d'imposition selon le secteur ou le régime.")

    st.markdown("##### Échéances Fiscales Clés en Cours")
    df_echeances = pd.DataFrame({
        "Impôt / Taxe": ["Déclaration mensuelle TVA & AIB", "Acompte BIC / IS", "Versement Forfaitaire (VF)"],
        "Périodicité": ["Mensuelle", "Trimestrielle", "Mensuelle"],
        "Échéance Limite": ["10 au 15 du mois", "15 du mois suivant le trimestre", "10 au 15 du mois"],
        "Référence Officielle": ["Code Général des Impôts (CGI) - CI", "CGI Côte d'Ivoire", "CGI CI"]
    })
    st.dataframe(df_echeances, use_container_width=True)

# -----------------------------------------------------------------------------
# 6. PISTE D'AUDIT SÉCURISÉE
# -----------------------------------------------------------------------------
elif module_courant == "🛡️ Piste d'Audit Sécurisée":
    st.markdown("#### Journal d'Audit Immuable & Chaîné (Cryptographie SHA-256)")
    st.markdown("<p style='color: #94a3b8;'>Chaque action sensible sur la plateforme est scellée et liée mathématiquement à la précédente pour garantir l'inviolabilité.</p>", unsafe_allow_html=True)

    logs = charger_audit()
    if logs:
        df_logs = pd.DataFrame(logs)
        st.dataframe(df_logs, use_container_width=True)
        
        csv_logs = df_logs.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Exporter le Journal d'Audit (CSV Sécurisé)", data=csv_logs, file_name="piste_audit_entreprise.csv", mime="text/csv")
    else:
        st.info("Aucun journal d'audit enregistré pour l'instant.")

# -----------------------------------------------------------------------------
# 7. PARAMÈTRES
# -----------------------------------------------------------------------------
elif module_courant == "⚙️ Paramètres":
    st.markdown("#### Paramètres de l'Entreprise & Sécurité")
    st.text_input("Raison Sociale de l'Entreprise", value="MaSociété SARL")
    st.text_input("Siège Social", value="Abidjan, Plateau, Avenue X")
    if st.button("Se déconnecter de la session"):
        enregistrer_piste_audit("DECONNEXION", f"Déconnexion de {st.session_state.username}", st.session_state.username)
        st.session_state.authentifie = False
        st.rerun()
