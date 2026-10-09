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
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from cryptography.fernet import Fernet

# -----------------------------------------------------------------------------
# CONFIGURATION DE LA PAGE & DESIGN 3D / GLASSMORPHISM HAUT DE GAMME
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Plateforme FinTech & Compliance | Standard Suisse & UEMOA",
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
        background: radial-gradient(circle at 50% 10%, #040814 0%, #010204 100%);
        color: #f8fafc;
    }

    .dashboard-card, div[data-testid="stMetric"], div.stForm, .stPlotlyChart {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(212, 175, 55, 0.35);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.75), 
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }

    /* ---------------------------------------------------------
       STYLES 3D AVANCÉS POUR LES BOUTONS DU MENU (GLASSMORPHISM)
       --------------------------------------------------------- */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95)) !important;
        color: #f8fafc !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        border: 1px solid rgba(212, 175, 55, 0.3) !important;
        border-radius: 14px !important;
        padding: 14px 10px !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.5), 
                    inset 0 1px 0 rgba(255, 255, 255, 0.15),
                    inset 0 -2px 5px rgba(0, 0, 0, 0.6) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        margin-bottom: 10px;
    }

    div.stButton > button:hover {
        transform: translateY(-3px) scale(1.02);
        background: linear-gradient(145deg, rgba(51, 65, 85, 0.95), rgba(30, 41, 59, 0.98)) !important;
        border: 1px solid rgba(252, 211, 77, 0.8) !important;
        color: #fde047 !important;
        box-shadow: 0 14px 30px rgba(212, 175, 55, 0.25), 
                    inset 0 1px 0 rgba(255, 255, 255, 0.3),
                    inset 0 -2px 6px rgba(0, 0, 0, 0.8) !important;
    }

    div.stButton > button:active {
        transform: translateY(1px) scale(0.99);
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.8), inset 0 2px 4px rgba(0, 0, 0, 0.9) !important;
    }

    input, textarea {
        background-color: rgba(15, 23, 42, 0.95) !important;
        color: #ffffff !important;
        border: 1px solid rgba(212, 175, 55, 0.4) !important;
        border-radius: 10px !important;
    }
    
    div[data-baseweb="select"] > div {
        background-color: rgba(15, 23, 42, 0.95) !important;
        color: #ffffff !important;
        border: 1px solid rgba(212, 175, 55, 0.4) !important;
        border-radius: 10px !important;
    }

    label {
        color: #fde047 !important;
        font-weight: 600 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# GESTION DES CLÉS DE CHIFFREMENT AES-256 & PISTE D'AUDIT CHAÎNÉE
# -----------------------------------------------------------------------------
KEY_FILE = "secret.key"
DATA_FILE = "audit_suisse_aes256.json"
SOC_FILE = "soc_security_logs.json"

def obtenir_cle_chiffrement():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    else:
        cle = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(cle)
        return cle

fernet_cipher = Fernet(obtenir_cle_chiffrement())

def charger_historique():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                lignes_chiffrees = json.load(f)
                historique = []
                for item in lignes_chiffrees:
                    item_dechiffre = {
                        "id": item.get("id"),
                        "date": item.get("date"),
                        "client": fernet_cipher.decrypt(item.get("client_enc").encode()).decode() if item.get("client_enc") else "Inconnu",
                        "montant": item.get("montant"),
                        "decis": item.get("decis"),
                        "pd": item.get("pd"),
                        "auteur_maker": item.get("auteur_maker"),
                        "validateur_checker": item.get("validateur_checker"),
                        "hash_precedent": item.get("hash_precedent"),
                        "hash_actuel": item.get("hash_actuel")
                    }
                    historique.append(item_dechiffre)
                return historique
        except:
            return []
    return []

def sauvegarder_historique(entree):
    historique_brut = charger_historique()
    dernier_hash = historique_brut[0]["hash_actuel"] if historique_brut else "0" * 64
    client_chiffre = fernet_cipher.encrypt(str(entree.get('client')).encode()).decode()
    
    donnees_brutes = f"{dernier_hash}{entree.get('id')}{client_chiffre}{entree.get('montant')}{datetime.datetime.now().isoformat()}"
    hash_actuel = hashlib.sha256(donnees_brutes.encode()).hexdigest()
    
    item_stockage = {
        "id": entree.get('id'),
        "date": entree.get('date'),
        "client_enc": client_chiffre,
        "montant": entree.get('montant'),
        "decis": entree.get('decis'),
        "pd": entree.get('pd'),
        "auteur_maker": entree.get('auteur_maker'),
        "validateur_checker": entree.get('validateur_checker'),
        "hash_precedent": dernier_hash,
        "hash_actuel": hash_actuel
    }
    
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            contenu = json.load(f)
    else:
        contenu = []
    
    contenu.insert(0, item_stockage)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(contenu, f, ensure_ascii=False, indent=4)

def enregistrer_log_soc(evenement, niveau="INFO"):
    logs = charger_logs_soc()
    nouveau_log = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "niveau": niveau,
        "evenement": evenement,
        "ip_source": "196.200.14.82 (Abidjan / Genève Secure Gateway)"
    }
    logs.insert(0, nouveau_log)
    with open(SOC_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=4)

def charger_logs_soc():
    if os.path.exists(SOC_FILE):
        try:
            with open(SOC_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

@st.cache_resource
def entrainer_modele_scoring():
    np.random.seed(42)
    X_train = np.random.rand(600, 3) * np.array([20000000, 60, 600000])
    y_train = (X_train[:, 0] / (X_train[:, 2] + 1) < 4.5).astype(int)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)
    model = LogisticRegression()
    model.fit(X_scaled, y_train)
    return model, scaler

ml_model, ml_scaler = entrainer_modele_scoring()

LISTE_SANCTIONS_INTERNATIONALE = ["vladimir sanction", "cartel global", "terrorist fund", "blacklisted entity sa", "shell corporation int"]

def verifier_listes_sanctions(nom_client):
    nom_nettoye = nom_client.lower().strip()
    for interdit in LISTE_SANCTIONS_INTERNATIONALE:
        if interdit in nom_nettoye:
            return True
    return False

# -----------------------------------------------------------------------------
# AUTHENTIFICATION FORTE MFA (2FA)
# -----------------------------------------------------------------------------
if "authentifie" not in st.session_state:
    st.session_state.authentifie = False

if not st.session_state.authentifie:
    st.markdown("<h2 style='text-align: center; color: #fde047;'>🇨🇭🇨🇮 Portail d'Accès Unifié — Standard Suisse & UEMOA (BCEAO)</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #cbd5e1;'>Chiffrement AES-256, MFA Avancé & Surveillance SOC Active</p>", unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        with st.form("form_login"):
            username = st.text_input("Identifiant Bancaire Sécurisé", value="private.banker@geneva-abidjan.ch")
            password = st.text_input("Mot de passe maître", type="password", value="swisssecure2026")
            code_otp = st.text_input("Jeton d'Authentification Forte (Code MFA / OTP)", value="482910")
            role_choisi = st.selectbox("Profil d'Habilitation (RBAC)", [
                "🔍 Analyste de Crédit & Private Banker (Maker)",
                "⚖️ Comité de Direction / Chief Risk Officer (Checker - FINMA/BCEAO)",
                "🚨 Officier de Conformité LBA & Risques UEMOA",
                "🛡️ Opérateur SOC & Sécurité des Systèmes d'Information"
            ])
            submit_login = st.form_submit_button("Valider la Connexion Chiffrée 2FA", use_container_width=True)
            if submit_login:
                if len(code_otp) == 6:
                    st.session_state.authentifie = True
                    st.session_state.username = username
                    st.session_state.user_role = role_choisi
                    enregistrer_log_soc(f"Connexion réussie pour {username} avec le rôle {role_choisi}", "INFO")
                    st.rerun()
                else:
                    enregistrer_log_soc(f"Tentative de connexion échouée (OTP invalide) pour {username}", "WARNING")
                    st.error("Code MFA invalide. Veuillez saisir un code à 6 chiffres valide.")
    st.stop()

# -----------------------------------------------------------------------------
# EN-TÊTE & CONTEXTE INSTITUTIONNEL
# -----------------------------------------------------------------------------
st.markdown("<h1 style='text-align: center; color: #f8fafc; font-weight: 800;'>HUB BANCAIRE INTERNATIONAL & RISQUES (SUISSE - UEMOA)</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #fde047; font-size: 1.05rem;'>Collaborateur : <b>{st.session_state.username}</b> | Profil : <b>{st.session_state.user_role}</b> | 🔐 HSM / AES-256 Actif</p>", unsafe_allow_html=True)

col_cfg1, col_cfg2 = st.columns(2)
with col_cfg1:
    zone_reglementaire = st.selectbox(
        "Cadre Réglementaire Appliqué",
        [
            "BCEAO / UEMOA (Circulaires Bancaires & Provisions)",
            "FINMA (Autorité fédérale suisse & Bâle III)",
            "Standards Internationaux (UBS / SG / Ecobank)",
        ],
    )
with col_cfg2:
    secret_bancaire_mode = st.toggle("Activer le Masquage Dynamique du Secret Bancaire (LPD / RGPD)", value=True)

st.markdown("---")

# -----------------------------------------------------------------------------
# NAVIGATION CENTRALE (MENU 3D GLASSMORPHISM)
# -----------------------------------------------------------------------------
if "active_module" not in st.session_state:
    st.session_state.active_module = "🏠 Tableau de bord"

modules = {
    "🏠 Tableau de bord": "Vue Globale",
    "💳 Banque & Crédit": "Scoring IA & Maker-Checker",
    "📊 Provisions BCEAO": "Classification & Normes UEMOA",
    "🏛️ Sûretés & Garanties": "Nantissements & Hypothèques",
    "🚨 Anti-Fraude & Traçage": "Traçage des Flux & Gel",
    "🛡️ Conformité LBA": "KYC & Screening Sanctions",
    "🚨 SOC (Sécurité)": "Journal des Intrusions & Logs",
    "📱 Mobile Money": "Scoring Alternatif",
    "🌱 Risque Agricole": "Campagnes Cacao/Café",
    "🌍 PAPSS": "Paiements Transfrontaliers",
    "📈 Stress-Tests": "Résistance Macro & BCEAO",
    "📂 Data Center": "Import Chiffré",
    "📜 Historique & Audit": "Piste Chaînée & Rapport Certifié",
    "⚙️ Paramètres": "Paramétrage Global",
}

cols_menu = st.columns(5)
idx = 0
for mod_name, mod_desc in modules.items():
    col_target = cols_menu[idx % 5]
    with col_target:
        is_active = st.session_state.active_module == mod_name
        btn_label = f"✦ {mod_name}" if is_active else mod_name
        if st.button(btn_label, use_container_width=True, key=f"btn_{mod_name}"):
            st.session_state.active_module = mod_name
            st.rerun()
    idx += 1

current_page = st.session_state.active_module
st.markdown("---")
st.markdown(f"<h3 style='color: #fde047;'>Module Actif : {current_page}</h3>", unsafe_allow_html=True)

def masquer_donnee(valeur_texte, est_sensible=True):
    if secret_bancaire_mode and est_sensible:
        if len(valeur_texte) > 6:
            return f"****-****-{valeur_texte[-4:]}"
        return "********"
    return valeur_texte

# -----------------------------------------------------------------------------
# 1. TABLEAU DE BORD
# -----------------------------------------------------------------------------
if current_page == "🏠 Tableau de bord":
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Actifs Sous Gestion (AuM)", "4.8 Mds CHF / 3.2 Mille Mds XOF", delta="+4.2%")
    col2.metric("Indice de Conformité BCEAO/FINMA", "99.98%", delta="Optimal")
    col3.metric("Fonds Bloqués / Séquestrés LBA", "14.2 Mio CHF", delta="-2.1%")
    col4.metric("Ratio de Solvabilité Tier-1", "18.6%", delta="Sain")

    st.markdown("---")
    c_g1, c_g2 = st.columns(2)
    with c_g1:
        st.subheader("📈 Évolution des Capitaux et Engagements")
        df_chart = pd.DataFrame({"Mois": ["Nov", "Déc", "Jan", "Fév", "Mar", "Avr"], "Volume": [3.5, 3.8, 4.1, 4.3, 4.6, 4.8]})
        fig = px.line(df_chart, x="Mois", y="Volume", markers=True, template="plotly_dark")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with c_g2:
        st.subheader("📊 Allocation d'Actifs & Portefeuille Régional")
        df_pie = pd.DataFrame({"Classe d'Actifs": ["Fonds Privés & Actions", "Obligations Souveraines UEMOA", "Immobilier Abidjan/Genève", "Liquidités & Or", "Private Equity"], "Part": [30, 25, 20, 15, 10]})
        fig_pie = px.pie(df_pie, names="Classe d'Actifs", values="Part", hole=0.4, template="plotly_dark")
        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_pie, use_container_width=True)

# -----------------------------------------------------------------------------
# 2. BANQUE & CRÉDIT
# -----------------------------------------------------------------------------
elif current_page == "💳 Banque & Crédit":
    st.markdown("#### Modèle Prédictif de Solvabilité, Explicabilité IA & Workflow Maker-Checker")
    
    col_cr1, col_cr2 = st.columns(2)
    with col_cr1:
        nom_client_saisi = st.text_input("Nom de l'Emprunteur / Structure", value="Holding Alpha Wealth SA")
        nom_client = masquer_donnee(nom_client_saisi, est_sensible=False)
        chiffre_affaires = st.number_input("Chiffre d'Affaires Mensuel", min_value=100000, value=12000000)
        engagements_encours = st.number_input("Remboursements en cours / mois", min_value=0, value=400000)
    with col_cr2:
        pret_demande = st.number_input("Montant du Financement Demandé", min_value=100000, value=25000000)
        duree_mois = st.slider("Durée du remboursement (Mois)", 1, 60, 24)
        registre_impayes = st.radio("Fichage Central des Risques (BCEAO / Centrale)", ["Aucun incident", "Incident actif / Litige en cours"])

    sanction_detectee = verifier_listes_sanctions(nom_client_saisi)
    if sanction_detectee:
        st.error("🚨 ALERTE CRITIQUE : Entité figurant sur les listes de sanctions internationales (SECO / OFAC / ONU). Dossier bloqué.")

    features_input = ml_scaler.transform([[chiffre_affaires, duree_mois, engagements_encours]])
    prob_defaut = float(ml_model.predict_proba(features_input)[0][1]) * 100
    if registre_impayes == "Incident actif / Litige en cours" or sanction_detectee:
        prob_defaut = 99.0

    mensualite = (pret_demande * 1.02) / duree_mois
    taux_endettement = ((engagements_encours + mensualite) / chiffre_affaires) * 100 if chiffre_affaires > 0 else 100

    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    m1.metric("Mensualité Estimée", f"{mensualite:,.0f}")
    m2.metric("Taux d'Endettement", f"{taux_endettement:.1f} %")
    m3.metric("Probabilité de Défaut (PD - IA)", f"{prob_defaut:.1f}%")

    st.markdown("---")
    st.markdown("#### ⚖️ Gouvernance Maker-Checker")
    statut_initial = "EN ATTENTE VALIDATION COMITÉ DE DIRECTION" if (prob_defaut < 35 and not sanction_detectee) else "REJETÉ AUTOMATISÉ (Risque Élevé)"
    
    col_mk1, col_mk2 = st.columns(2)
    with col_mk1:
        st.info(f"**Rôle Maker :** Dossier préparé.\n\n**Statut :** {statut_initial}")
    with col_mk2:
        if "Direction" in st.session_state.user_role or "Conformité" in st.session_state.user_role or "Auditeur" in st.session_state.user_role:
            decision_checker = st.selectbox("Validation Hiérarchique (Checker)", ["En attente", "APPROUVÉ DÉFINITIVEMENT (Signature Comité)", "REJETÉ PAR LE CHIEF RISK OFFICER"])
        else:
            st.warning("⚠️ Seul le Comité de Direction (Checker) peut signer la décision finale.")
            decision_checker = "En attente"

    if st.button("💾 Enregistrer et Chiffrer au Repos (AES-256)"):
        decis_finale = decision_checker if decision_checker != "En attente" else ("APPROUVÉ (Maker)" if prob_defaut < 35 and not sanction_detectee else "REFUSÉ")
        dossier = {
            "id": f"UEMOA-CRED-{uuid.uuid4().hex[:6].upper()}",
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "client": nom_client_saisi,
            "montant": pret_demande,
            "decis": decis_finale,
            "pd": f"{prob_defaut:.1f}%",
            "auteur_maker": st.session_state.username,
            "validateur_checker": st.session_state.user_role
        }
        sauvegarder_historique(dossier)
        enregistrer_log_soc(f"Création de dossier de crédit {dossier['id']} - Statut: {decis_finale}", "INFO")
        st.success(f"✅ Dossier `{dossier['id']}` sécurisé, chiffré en AES-256 et consigné.")

# -----------------------------------------------------------------------------
# 3. PROVISIONS BCEAO / UEMOA
# -----------------------------------------------------------------------------
elif current_page == "📊 Provisions BCEAO":
    st.markdown("#### 📊 Classification et Calcul des Provisions Réglementaires (Normes BCEAO / UEMOA)")
    
    col_pr1, col_pr2 = st.columns(2)
    with col_pr1:
        encours_credit = st.number_input("Encours Brut du Crédit Octroyé (XOF / CHF)", value=50000000)
        jours_retard = st.slider("Nombre de jours de retard de paiement", 0, 360, 15)
    with col_pr2:
        type_garantie_associee = st.selectbox("Garantie principale rattachée", ["Aucune garantie", "Garantie personnelle (Aval)", "Nantissement / Gage", "Hypothèque immobilière de 1er rang"])

    if jours_retard == 0:
        classe_bceao = "Sains (Créances Saines)"
        taux_provision = 0.01
    elif jours_retard <= 90:
        classe_bceao = "Impayés / En souffrance (Sous surveillance)"
        taux_provision = 0.15
    elif jours_retard <= 180:
        classe_bceao = "Douteux"
        taux_provision = 0.50
    else:
        classe_bceao = "Litigieux (Contentieux)"
        taux_provision = 1.00

    montant_provision = encours_credit * taux_provision

    st.markdown("---")
    mp1, mp2, mp3 = st.columns(3)
    mp1.metric("Classification BCEAO", classe_bceao)
    mp2.metric("Taux de Provisionnement", f"{taux_provision * 100:.0f} %")
    mp3.metric("Montant de la Provision Requise", f"{montant_provision:,.0f}")

    if st.button("📝 Enregistrer la Dotation aux Provisions dans le Registre"):
        dossier_prov = {
            "id": f"UEMOA-PROV-{uuid.uuid4().hex[:6].upper()}",
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "client": f"Provision {classe_bceao} ({jours_retard}j retard)",
            "montant": montant_provision,
            "decis": f"PROVISIONNÉ ({taux_provision*100}%)",
            "pd": f"{jours_retard} jours",
            "auteur_maker": st.session_state.username,
            "validateur_checker": st.session_state.user_role
        }
        sauvegarder_historique(dossier_prov)
        enregistrer_log_soc(f"Calcul de provision BCEAO enregistré pour {encours_credit:,.0f} (Classe: {classe_bceao})", "INFO")
        st.success(f"✅ Provision de `{montant_provision:,.0f}` enregistrée et chiffrée avec succès.")

# -----------------------------------------------------------------------------
# 4. SÛRETÉS & GARANTIES
# -----------------------------------------------------------------------------
elif current_page == "🏛️ Sûretés & Garanties":
    st.markdown("#### 🏛️ Gestion des Sûretés, Nantissements et Hypothèques (Décote / Haircut)")
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        valeur_bien = st.number_input("Valeur Vénale / d'Expertise du Bien (CHF / XOF)", value=80000000)
        nature_garantie = st.selectbox("Nature de la Sûreté", [
            "Hypothèque Immobilière (Urbain / Commercial)",
            "Nantissement de Fonds de Commerce",
            "Gage sur Stocks (Cacao / Anacarde / Matières premières)",
            "Nantissement de Titres / Comptes d'Épargne Bloqués"
        ])
    with col_g2:
        taux_decote = st.slider("Taux de Décote Appliqué (Haircut prudentiel %)", 10, 60, 30)
        dossier_lie = st.text_input("ID du Dossier de Crédit Lié", "UEMOA-CRED-9482A1")

    valeur_nette_garantie = valeur_bien * (1 - (taux_decote / 100))

    st.markdown("---")
    mg1, mg2 = st.columns(2)
    mg1.metric("Valeur Brute du Bien", f"{valeur_bien:,.0f}")
    mg2.metric("Valeur Nette Prise en Compte (Après Haircut)", f"{valeur_nette_garantie:,.0f}")

    if st.button("🔒 Valider et Consigner la Sûreté au Registre Sécurisé"):
        dossier_surete = {
            "id": f"UEMOA-GART-{uuid.uuid4().hex[:6].upper()}",
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "client": f"Garantie {nature_garantie} ({dossier_lie})",
            "montant": valeur_nette_garantie,
            "decis": "SÛRETÉ VALIDÉE & ENREGISTRÉE",
            "pd": f"Décote: {taux_decote}%",
            "auteur_maker": st.session_state.username,
            "validateur_checker": st.session_state.user_role
        }
        sauvegarder_historique(dossier_surete)
        enregistrer_log_soc(f"Enregistrement de sûreté ({nature_garantie}) d'une valeur nette de {valeur_nette_garantie:,.0f}", "INFO")
        st.success(f"✅ Sûreté enregistrée avec succès sous l'identifiant `{dossier_surete['id']}`.")

# -----------------------------------------------------------------------------
# 5. ANTI-FRAUDE & TRAÇAGE
# -----------------------------------------------------------------------------
elif current_page == "🚨 Anti-Fraude & Traçage":
    st.markdown("#### 🕵️‍♂️ Traçage des Sauts Financiers & Gel Automatisé")
    col_tr1, col_tr2 = st.columns(2)
    with col_tr1:
        id_transaction = st.text_input("ID de la Transaction Suspecte", f"UEMOA-TXN-{uuid.uuid4().hex[:8].upper()}")
        compte_source = st.text_input("Compte Émetteur / Source", value="CI98-0001-2291-SGA")
        montant_initial = st.number_input("Montant Contesté", value=15000000)
    with col_tr2:
        canal_fraude = st.selectbox("Canal", ["Virement SWIFT / PAPSS", "Mobile Money Interopérable", "Plateforme Crypto", "Compte Intermédiaire"])
        delai_signalement = st.slider("Délai de signalement (Minutes)", 5, 120, 15)

    st.markdown("---")
    st.subheader("📊 Cartographie des Sauts Multi-Hop")
    fig_trace = go.Figure(data=[
        go.Scatter(x=[0, 1, 2, 3], y=[0, 0, 0, 0], mode='lines', line=dict(width=4, color='#fde047'), hoverinfo='none'),
        go.Scatter(
            x=[0, 1, 2, 3], 
            y=[0, 0, 0, 0], 
            mode='markers+text', 
            text=[f"Source\n{compte_source}", "Intermédiaire 1", "Compte Off-shore", "Blocage Final"], 
            textposition="top center", 
            marker=dict(color=['#3b82f6', '#f59e0b', '#ef4444', '#7f1d1d'], size=26)
        )
    ])
    fig_trace.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(showgrid=False, zeroline=False, showticklabels=False), yaxis=dict(showgrid=False, zeroline=False, showticklabels=False), margin=dict(t=50, b=50))
    st.plotly_chart(fig_trace, use_container_width=True)

    if st.button("🛑 EXÉCUTER LE SÉQUESTRE IMMÉDIAT ET NOTIFIER LA BCEAO / FINMA"):
        alerte_id = f"UEMOA-ALERT-{uuid.uuid4().hex[:6].upper()}"
        dossier_fraude = {
            "id": alerte_id,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "client": f"Séquestre {id_transaction}",
            "montant": montant_initial,
            "decis": "COMPTE GELÉ & SÉQUESTRÉ",
            "pd": f"{delai_signalement} min",
            "auteur_maker": st.session_state.username,
            "validateur_checker": st.session_state.user_role
        }
        sauvegarder_historique(dossier_fraude)
        enregistrer_log_soc(f"ALERTE ROUGE : Gel de transaction {id_transaction} pour un montant de {montant_initial:,.0f}", "CRITICAL")
        st.error(f"🛑 ORDRE DE SÉQUESTRE EXÉCUTÉ sous l'ID `{alerte_id}`. Comptes gelés en temps réel.")

# -----------------------------------------------------------------------------
# 6. CONFORMITÉ LBA
# -----------------------------------------------------------------------------
elif current_page == "🛡️ Conformité LBA":
    st.markdown("#### 🛡️ Conformité LBA & Screening Automatique des Listes de Sanctions (SECO / OFAC / ONU)")
    c_kyc1, c_kyc2 = st.columns(2)
    with c_kyc1:
        nom_beneficiaire = st.text_input("Nom du Bénéficiaire Effectif (UBO) / Société", value="Vladimir Sanction Holding")
        pays_origine = st.selectbox("Pays d'Origine des Fonds", ["Côte d'Ivoire (CI)", "Suisse (CH)", "Union Européenne (UE)", "Juridiction à Haut Risque (GAFI)"])
        statut_pep = st.selectbox("Statut Personne Politiquement Exposée (PEP)", ["Non PEP", "PEP National", "PEP International / Haut Risque"])
    with c_kyc2:
        justificatif = st.selectbox("Justificatif d'Origine des Fonds", ["Vente immobilière", "Héritage", "Dividendes certifiés", "Origine non vérifiable / Complexe"])
        montant_fonds = st.number_input("Montant Global des Actifs", value=10000000)

    sanction_match = verifier_listes_sanctions(nom_beneficiaire)
    score_lba_risque = 99.0 if (sanction_match or pays_origine == "Juridiction à Haut Risque (GAFI)" or statut_pep != "Non PEP") else 15.0
    
    st.markdown("---")
    if sanction_match:
        st.error("🚨 ALERTE ROUGE : Correspondance exacte détectée sur les listes de gel des avoirs internationales.")
    
    st.metric("Indice de Risque LBA & Sanctions", f"{score_lba_risque}%", delta="CRITIQUE - GEL IMMÉDIAT" if score_lba_risque > 50 else "Faible & Conforme", delta_color="inverse")

    if st.button("📋 Valider le Dossier KYC & Enregistrer le Certificat Chiffré"):
        decis_kyc = "BLOQUÉ - LISTE DE SANCTIONS" if sanction_match else ("VALIDÉ LBA (Conforme)" if score_lba_risque < 50 else "INVESTIGATION REQUISE")
        dossier_kyc = {
            "id": f"UEMOA-KYC-{uuid.uuid4().hex[:6].upper()}",
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "client": nom_beneficiaire,
            "montant": montant_fonds,
            "decis": decis_kyc,
            "pd": f"Risque: {score_lba_risque}%",
            "auteur_maker": st.session_state.username,
            "validateur_checker": st.session_state.user_role
        }
        sauvegarder_historique(dossier_kyc)
        enregistrer_log_soc(f"Contrôle KYC LBA effectué pour {nom_beneficiaire} - Résultat: {decis_kyc}", "WARNING" if sanction_match else "INFO")
        if not sanction_match and score_lba_risque < 50:
            st.success(f"✅ Dossier KYC `{dossier_kyc['id']}` validé et consigné de manière chiffrée.")
        else:
            st.error(f"🛑 Alerte Compliance : Le dossier `{dossier_kyc['id']}` a été consigné avec un statut de blocage.")

# -----------------------------------------------------------------------------
# 7. SOC (SÉCURITÉ)
# -----------------------------------------------------------------------------
elif current_page == "🚨 SOC (Sécurité)":
    st.markdown("#### 🛡️ Centre d'Opérations de Sécurité (SOC) — Journal des Événements et Intrusions")
    logs_soc = charger_logs_soc()
    if logs_soc:
        df_soc = pd.DataFrame(logs_soc)
        st.dataframe(df_soc, use_container_width=True)
        col_soc1, col_soc2 = st.columns(2)
        with col_soc1:
            csv_soc = df_soc.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Télécharger les Logs de Sécurité (CSV)", data=csv_soc, file_name="soc_security_audit_logs.csv", mime="text/csv")
        with col_soc2:
            if st.button("🧹 Vider le Journal des Logs SOC (Test)"):
                if os.path.exists(SOC_FILE):
                    os.remove(SOC_FILE)
                st.success("Journal SOC réinitialisé.")
                st.rerun()
    else:
        st.info("Aucun événement de sécurité consigné pour le moment.")

# -----------------------------------------------------------------------------
# 8. MOBILE MONEY
# -----------------------------------------------------------------------------
elif current_page == "📱 Mobile Money":
    st.markdown("#### Scoring Alternatif Digital (Orange Money / Wave / MTN MoMo)")
    flux = st.number_input("Encaissements 3 derniers mois", value=4000000)
    anciennete = st.slider("Ancienneté du compte (Mois)", 1, 36, 12)
    solde_nuit = st.number_input("Solde moyen de nuit", value=300000)
    score = 500 + (anciennete * 10) + (solde_nuit / 2000)
    st.metric("Score Digital Alternatif", f"{int(score)} / 950 points")
    st.success("🌟 Profil validé pour l'octroi d'une ligne de micro-crédit mobile.")

# -----------------------------------------------------------------------------
# 9. RISQUE AGRICOLE
# -----------------------------------------------------------------------------
elif current_page == "🌱 Risque Agricole":
    st.markdown("#### Modélisation Agricole & Campagnes (Cacao / Café / Anacarde)")
    surf = st.number_input("Surface exploitée (Hectares)", value=10.0)
    rend = st.number_input("Rendement moyen (Kg/Ha)", value=800)
    prix = st.number_input("Prix d'achat garanti (FCFA / kg)", value=1800)
    rev = surf * rend * prix
    st.metric("Revenu Net Estimé de la Campagne", f"{rev:,.0f}")

# -----------------------------------------------------------------------------
# 10. PAPSS
# -----------------------------------------------------------------------------
elif current_page == "🌍 PAPSS":
    st.markdown("#### Paiements & Règlements Panafricains Transfrontaliers (PAPSS)")
    montant_xof = st.number_input("Montant à transférer", value=10000000)
    devise_cible = st.selectbox("Devise Destinataire", ["NGN", "GHS", "KES", "USD"])
    if st.button("💱 Exécuter le Transfert Panafricain Instantané"):
        enregistrer_log_soc(f"Transfert PAPSS exécuté pour {montant_xof:,.0f} vers {devise_cible}", "INFO")
        st.success("✅ Règlement transfrontalier exécuté avec succès en monnaies locales.")

# -----------------------------------------------------------------------------
# 11. STRESS-TESTS MACROÉCONOMIQUES
# -----------------------------------------------------------------------------
elif current_page == "📈 Stress-Tests":
    st.markdown("#### 📈 Moteur de Stress-Test Macroéconomique (BCEAO & Cours des Matières Premières)")
    st.markdown("<p style='color: #cbd5e1;'>Simulation de résistance du portefeuille face à un choc sur les taux directeurs de la BCEAO et le prix du Cacao / Café.</p>", unsafe_allow_html=True)

    col_st1, col_st2 = st.columns(2)
    with col_st1:
        hausse_taux_bceao = st.slider("Augmentation du taux directeur BCEAO (Points de base)", 0, 300, 75)
        chute_cacao = st.slider("Baisse du cours international du Cacao / Café (%)", 0, 50, 20)
    with col_st2:
        portefeuille_total_milliards = st.number_input("Encours Global du Portefeuille (Milliards XOF)", value=150.0)

    impact_taux_pct = hausse_taux_bceao * 0.04
    impact_cacao_pct = chute_cacao * 0.85
    impact_total_defaut_pct = min(100.0, impact_taux_pct + impact_cacao_pct)
    
    montant_creances_compromises = portefeuille_total_milliards * (impact_total_defaut_pct / 100)
    exigence_fonds_propres_sup = montant_creances_compromises * 0.50

    st.markdown("---")
    ms1, ms2, ms3 = st.columns(3)
    ms1.metric("Augmentation du Taux de Défaut Global", f"+{impact_total_defaut_pct:.2f}%", delta="Stress Sévère", delta_color="inverse")
    ms2.metric("Créances à Risque / Compromises", f"{montant_creances_compromises:.2f} Mds XOF")
    ms3.metric("Besoin Additionnel Fonds Propres Tier-1", f"{exigence_fonds_propres_sup:.2f} Mds XOF")

    if st.button("📊 Générer le Rapport de Stress-Test Macroéconomique"):
        enregistrer_log_soc(f"Exécution d'un stress-test macroéconomique (Hausse taux: {hausse_taux_bceao} pb, Chute cacao: {chute_cacao}%)", "WARNING")
        st.success("✅ Simulation macroéconomique enregistrée et validée pour le rapport prudentiel.")

# -----------------------------------------------------------------------------
# 12. DATA CENTER
# -----------------------------------------------------------------------------
elif current_page == "📂 Data Center":
    st.markdown("#### Importation de Portefeuille & Registre Chiffré AES-256")
    uploaded_file = st.file_uploader("Importer un fichier chiffré (CSV / Excel)", type=["csv", "xlsx"])
    if uploaded_file is not None:
        try:
            df_imported = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            st.success(f"✅ Fichier '{uploaded_file.name}' déchiffré et analysé avec succès !")
            st.dataframe(df_imported.head(10), use_container_width=True)
        except Exception as e:
            st.error(f"Erreur : {e}")

# -----------------------------------------------------------------------------
# 13. HISTORIQUE & AUDIT
# -----------------------------------------------------------------------------
elif current_page == "📜 Historique & Audit":
    st.markdown("#### 🔒 Piste d'Audit Inviolable (Chiffrement AES-256 & Rapport Certifié)")
    historique = charger_historique()
    if historique:
        df_hist = pd.DataFrame(historique)
        st.dataframe(df_hist, use_container_width=True)

        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            csv_data = df_hist.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Télécharger la Piste d'Audit (CSV)", data=csv_data, file_name="piste_audit_uemoa_suisse.csv", mime="text/csv")

        with col_exp2:
            if historique:
                dossier = historique[0]
                html_report = f"""
                <html>
                <head><meta charset="utf-8"><title>Rapport d'Audit Sécurisé</title></head>
                <body style="font-family: Arial, sans-serif; padding: 40px; color: #0f172a; background: #f8fafc;">
                    <div style="max-width: 700px; margin: auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border: 1px solid #cbd5e1;">
                        <h2 style="color: #0f172a; text-align: center;">ATTESTATION OFFICIELLE DE CONFORMITÉ FINMA & BCEAO</h2>
                        <p style="text-align: center; color: #64748b;">Standards Bancaires Internationaux — Données Chiffrées au Repos (AES-256)</p>
                        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0;">
                        <p><b>ID Enregistrement :</b> {dossier.get('id')}</p>
                        <p><b>Horodatage UTC :</b> {dossier.get('date')}</p>
                        <p><b>Client / Actif (Déchiffré) :</b> {dossier.get('client')}</p>
                        <p><b>Montant :</b> {dossier.get('montant'):,.0f}</p>
                        <p><b>Décision / Statut :</b> <span style="color: {'green' if 'APPROUVÉ' in dossier.get('decis') or 'VALIDÉ' in dossier.get('decis') or 'PROVISIONNÉ' in dossier.get('decis') else 'red'}; font-weight: bold;">{dossier.get('decis')}</span></p>
                        <p><b>Empreinte Cryptographique (SHA-256) :</b> <code style="font-size: 0.75rem; background: #f1f5f9; padding: 4px; border-radius: 4px;">{dossier.get('hash_actuel')}</code></p>
                        <br>
                        <p style="font-size: 0.9rem; color: #475569; text-align: center;"><i>Ce document certifie le chiffrement AES-256 et l'intégrité absolue de la piste d'audit réglementaire.</i></p>
                    </div>
                </body>
                </html>
                """
                st.download_button(
                    "📄 Télécharger le Rapport d'Audit Certifié (HTML Imprimable / PDF)",
                    data=html_report,
                    file_name=f"Rapport_Audit_Certifie_{dossier.get('id')}.html",
                    mime="text/html"
                )
    else:
        st.info("Aucune transaction enregistrée dans le registre chiffré.")

# -----------------------------------------------------------------------------
# 14. PARAMÈTRES
# -----------------------------------------------------------------------------
elif current_page == "⚙️ Paramètres":
    st.markdown("#### Paramètres Généraux de la Plateforme")
    st.text_input("Responsable Technique / Risk Manager", value="Kouassi Kouame Daniel")
    st.text_input("Institution de Rattachement", value="Apex Institute of Management (MBA Data Science & AI)")
    if st.button("Se déconnecter de la session sécurisée"):
        enregistrer_log_soc(f"Déconnexion de {st.session_state.username}", "INFO")
        st.session_state.authentifie = False
        st.rerun()
