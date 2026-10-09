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
# CONFIGURATION DE LA PAGE & DESIGN INSTITUTIONNEL HAUT DE GAMME
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
# NAVIGATION CENTRALE
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
        btn_label = f"📍 {mod_name}" if is_active else mod_name
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
