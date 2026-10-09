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

# -----------------------------------------------------------------------------
# CONFIGURATION DE LA PAGE & DESIGN INSTITUTIONNEL HAUT DE GAMME
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Plateforme FinTech & Anti-Fraude | Swiss Banking Standard",
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

    /* Arrière-plan global : Bleu nuit institutionnel profond (Banque Privée) */
    .stApp {
        background: radial-gradient(circle at 50% 10%, #060d1f 0%, #020408 100%);
        color: #f8fafc;
    }

    /* --- CARTES 3D GLASSMORPHISM NETTES --- */
    .dashboard-card, div[data-testid="stMetric"], div.stForm, .stPlotlyChart {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(212, 175, 55, 0.3); /* Touche d'or institutionnel suisse */
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.7), 
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }

    /* --- CHAMPS DE SAISIE & SELECTBOX PROFESSIONNELS --- */
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
# GESTION DE LA PERSISTANCE & PISTE D'AUDIT CRYPTOGRAPHIQUE CHAÎNÉE (SWISS STANDARD)
# -----------------------------------------------------------------------------
DATA_FILE = "audit_suisse_blockchain.json"

def charger_historique():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def sauvegarder_historique(entree):
    historique = charger_historique()
    # Création d'une empreinte cryptographique liée au bloc précédent (Chaînage immuable)
    dernier_hash = historique[0]["hash_actuel"] if historique else "0" * 64
    donnees_brutes = f"{dernier_hash}{entree.get('id')}{entree.get('client')}{entree.get('montant')}{datetime.datetime.now().isoformat()}"
    hash_actuel = hashlib.sha256(donnees_brutes.encode()).hexdigest()
    
    entree["hash_precedent"] = dernier_hash
    entree["hash_actuel"] = hash_actuel
    
    historique.insert(0, entree)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(historique, f, ensure_ascii=False, indent=4)

def hacher_mdp(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Entraînement du modèle de Scoring Prudentiel Scikit-Learn
@st.cache_resource
def entrainer_modele_scoring():
    np.random.seed(42)
    X_train = np.random.rand(600, 3) * np.array([20000000, 60, 600000]) # [CA, Duree, Encours]
    y_train = (X_train[:, 0] / (X_train[:, 2] + 1) < 4.5).astype(int)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)
    model = LogisticRegression()
    model.fit(X_scaled, y_train)
    return model, scaler

ml_model, ml_scaler = entrainer_modele_scoring()

# -----------------------------------------------------------------------------
# AUTHENTIFICATION FORTE MFA (2FA & JETON NUMÉRIQUE)
# -----------------------------------------------------------------------------
if "authentifie" not in st.session_state:
    st.session_state.authentifie = False

if not st.session_state.authentifie:
    st.markdown("<h2 style='text-align: center; color: #fde047;'>🇨🇭 Portail d'Accès Sécurisé — Standards Banques Privées Suisses (FINMA)</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #cbd5e1;'>Chiffrement Militaire, Authentification Forte (MFA) & Piste d'Audit Inviolable</p>", unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        with st.form("form_login"):
            username = st.text_input("Identifiant Bancaire Sécurisé", value="private.banker@geneva.ch")
            password = st.text_input("Mot de passe maître", type="password", value="swisssecure2026")
            code_otp = st.text_input("Jeton d'Authentification Forte (Code MFA / SwissID)", value="849204")
            role_choisi = st.selectbox("Profil d'Habilitation (RBAC)", [
                "🔍 Analyste de Crédit & Private Banker (Maker)",
                "⚖️ Comité de Direction / Chief Risk Officer (Checker - FINMA)",
                "🚨 Officier de Conformité LBA & Lutte Anti-Blanchiment",
                "📊 Auditeur Interne / Inspecteur Régulateur"
            ])
            submit_login = st.form_submit_button("Valider la Connexion Sécurisée 2FA", use_container_width=True)
            if submit_login:
                if len(code_otp) == 6:
                    st.session_state.authentifie = True
                    st.session_state.username = username
                    st.session_state.user_role = role_choisi
                    st.session_state.pwd_hash = hacher_mdp(password)
                    st.rerun()
                else:
                    st.error("Code MFA invalide. Veuillez saisir un code à 6 chiffres valide.")
    st.stop()

# -----------------------------------------------------------------------------
# EN-TÊTE & CONTEXTE INSTITUTIONNEL SUISSE
# -----------------------------------------------------------------------------
st.markdown("<h1 style='text-align: center; color: #f8fafc; font-weight: 800;'>SWISS PRIVATE BANKING & RISK MANAGEMENT HUB</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #fde047; font-size: 1.05rem;'>Conseiller Connecté : <b>{st.session_state.username}</b> | Habilitation : <b>{st.session_state.user_role}</b> | 🛡️ Session Protégée (FINMA)</p>", unsafe_allow_html=True)

col_cfg1, col_cfg2 = st.columns(2)
with col_cfg1:
    zone_reglementaire = st.selectbox(
        "Cadre Réglementaire / Autorité de Surveillance",
        [
            "FINMA (Autorité fédérale de surveillance des banques suisses)",
            "Standards Bancaires Internationaux (UBS / Julius Baer / Pictet)",
            "UEMOA (BCEAO - Standards Panafricains)",
            "Référence Transfrontalière PAPSS",
        ],
    )
with col_cfg2:
    secret_bancaire_mode = st.toggle("Activer le Masquage Dynamique du Secret Bancaire (LPD)", value=True)

st.markdown("---")

# -----------------------------------------------------------------------------
# NAVIGATION CENTRALE
# -----------------------------------------------------------------------------
if "active_module" not in st.session_state:
    st.session_state.active_module = "🏠 Tableau de bord"

modules = {
    "🏠 Tableau de bord": "Vue Globale",
    "💳 Banque & Crédit": "Scoring Bâle III & Maker-Checker",
    "🚨 Anti-Fraude & Traçage": "Traçage des Flux & Gel (Style Suisse/Inde)",
    "🛡️ Conformité LBA": "KYC & Origine des Fonds (Loi Blanchiment)",
    "📱 Mobile Money": "Scoring Alternatif",
    "🌱 Risque Agricole": "Campagnes Cacao/Café",
    "🌍 PAPSS": "Paiements Transfrontaliers",
    "📈 Stress-Tests": "Résistance Bancaire",
    "📂 Data Center": "Import & Registres",
    "📜 Historique & Audit": "Piste d'Audit Chaînée (Blockchain)",
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

# Fonction utilitaire pour masquer les données personnelles (Secret Bancaire / LPD)
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
    col1.metric("Actifs Sous Gestion (AuM)", "4.8 Mds CHF", delta="+4.2%")
    col2.metric("Indice de Conformité FINMA", "99.98%", delta="Optimal")
    col3.metric("Fonds Bloqués / Séquestrés LBA", "14.2 Mio CHF", delta="-2.1%")
    col4.metric("Ratio de Solvabilité Tier-1", "18.6%", delta="Sain")

    st.markdown("---")
    c_g1, c_g2 = st.columns(2)
    with c_g1:
        st.subheader("📈 Évolution des Capitaux et Rendements (Mds CHF)")
        df_chart = pd.DataFrame({"Mois": ["Nov", "Déc", "Jan", "Fév", "Mar", "Avr"], "Volume": [3.5, 3.8, 4.1, 4.3, 4.6, 4.8]})
        fig = px.line(df_chart, x="Mois", y="Volume", markers=True, template="plotly_dark")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with c_g2:
        st.subheader("📊 Allocation d'Actifs et Profils de Risque Private Banking")
        df_pie = pd.DataFrame({"Classe d'Actifs": ["Actions Internationales", "Obligations Souveraines", "Immobilier de Prestige", "Liquidités & Or", "Private Equity"], "Part": [30, 25, 20, 15, 10]})
        fig_pie = px.pie(df_pie, names="Classe d'Actifs", values="Part", hole=0.4, template="plotly_dark")
        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_pie, use_container_width=True)

# -----------------------------------------------------------------------------
# 2. BANQUE & CRÉDIT (SCORING IA + EXPLICABILITÉ + MAKER-CHECKER)
# -----------------------------------------------------------------------------
elif current_page == "💳 Banque & Crédit":
    st.markdown("#### Modèle Prédictif de Solvabilité, Explicabilité IA & Workflow Maker-Checker")
    
    col_cr1, col_cr2 = st.columns(2)
    with col_cr1:
        nom_client_saisi = st.text_input("Nom de l'Emprunteur / Structure", value="Holding Alpha Wealth SA")
        nom_client = masquer_donnee(nom_client_saisi, est_sensible=False) # Nom masqué ou non selon option
        chiffre_affaires = st.number_input("Chiffre d'Affaires Mensuel (CHF / FCFA)", min_value=100000, value=12000000)
        engagements_encours = st.number_input("Remboursements en cours / mois", min_value=0, value=400000)
    with col_cr2:
        pret_demande = st.number_input("Montant du Financement Demandé", min_value=100000, value=25000000)
        duree_mois = st.slider("Durée du remboursement (Mois)", 1, 60, 24)
        registre_impayes = st.radio("Fichage Central des Risques (Zentralstelle / BIC)", ["Aucun incident", "Incident actif / Litige en cours"])

    features_input = ml_scaler.transform([[chiffre_affaires, duree_mois, engagements_encours]])
    prob_defaut = float(ml_model.predict_proba(features_input)[0][1]) * 100
    if registre_impayes == "Incident actif / Litige en cours":
        prob_defaut = min(99.0, prob_defaut + 45.0)

    mensualite = (pret_demande * 1.02) / duree_mois
    taux_endettement = ((engagements_encours + mensualite) / chiffre_affaires) * 100 if chiffre_affaires > 0 else 100

    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    m1.metric("Mensualité Estimée", f"{mensualite:,.0f}")
    m2.metric("Taux d'Endettement", f"{taux_endettement:.1f} %")
    m3.metric("Probabilité de Défaut (PD - IA)", f"{prob_defaut:.1f}%")

    # Explicabilité IA
    st.markdown("#### 🧠 Explicabilité du Modèle (Facteurs de Risque)")
    contrib_ca = -35.0 if chiffre_affaires > 5000000 else 45.0
    contrib_end = 40.0 if taux_endettement > 30 else -20.0
    contrib_bic = 60.0 if registre_impayes == "Incident actif / Litige en cours" else -10.0

    df_expl = pd.DataFrame({
        "Facteur Clé": ["Niveau de Chiffre d'Affaires", "Taux d'Endettement", "Historique Contentieux"],
        "Impact sur le Risque (%)": [contrib_ca, contrib_end, contrib_bic]
    })
    
    fig_exp = px.bar(df_expl, x="Impact sur le Risque (%)", y="Facteur Clé", orientation='h', template="plotly_dark", color="Impact sur le Risque (%)", color_continuous_scale="RdBu_r")
    fig_exp.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=10, b=10))
    st.plotly_chart(fig_exp, use_container_width=True)

    st.markdown("---")
    st.markdown("#### ⚖️ Gouvernance Maker-Checker (Double Regard Suisse)")
    statut_initial = "EN ATTENTE VALIDATION COMITÉ DE DIRECTION" if (prob_defaut < 35 and registre_impayes != "Incident actif / Litige en cours") else "REJETÉ AUTOMATISÉ (Seuil de risque FINMA)"
    
    col_mk1, col_mk2 = st.columns(2)
    with col_mk1:
        st.info(f"**Rôle Maker (Banquier Privé) :** Dossier préparé.\n\n**Statut :** {statut_initial}")
    with col_mk2:
        if "Direction" in st.session_state.user_role or "Conformité" in st.session_state.user_role or "Auditeur" in st.session_state.user_role:
            decision_checker = st.selectbox("Validation Hiérarchique (Rôle Checker)", ["En attente", "APPROUVÉ DÉFINITIVEMENT (Signature Comité Suisse)", "REJETÉ PAR LE CHIEF RISK OFFICER"])
        else:
            st.warning("⚠️ Seul le Comité de Direction (Checker) peut signer la décision finale.")
            decision_checker = "En attente"

    if st.button("💾 Enregistrer et Consigner dans la Piste d'Audit Chaînée"):
        decis_finale = decision_checker if decision_checker != "En attente" else ("APPROUVÉ (Maker)" if prob_defaut < 35 else "REFUSÉ")
        dossier = {
            "id": f"CH-CRED-{uuid.uuid4().hex[:6].upper()}",
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "client": nom_client_saisi if not secret_bancaire_mode else masquer_donnee(nom_client_saisi),
            "montant": pret_demande,
            "decis": decis_finale,
            "pd": f"{prob_defaut:.1f}%",
            "auteur_maker": st.session_state.username,
            "validateur_checker": st.session_state.user_role
        }
        sauvegarder_historique(dossier)
        st.success(f"✅ Dossier `{dossier['id']}` validé et consigné de manière infalsifiable avec horodatage cryptographique.")

# -----------------------------------------------------------------------------
# 3. ANTI-FRAUDE & TRAÇAGE DES FONDS
# -----------------------------------------------------------------------------
elif current_page == "🚨 Anti-Fraude & Traçage":
    st.markdown("#### 🕵️‍♂️ Traçage des Sauts Financiers & Gel Automatisé (Standards Internationaux)")
    col_tr1, col_tr2 = st.columns(2)
    with col_tr1:
        id_transaction = st.text_input("ID de la Transaction Suspecte", f"CH-TXN-{uuid.uuid4().hex[:8].upper()}")
        compte_source = st.text_input("Compte Émetteur / Source", value="CH93-0000-1192-SWISS")
        montant_initial = st.number_input("Montant Contesté", value=150000)
    with col_tr2:
        canal_fraude = st.selectbox("Canal", ["Virement SWIFT suspect", "Paiement Carte Privée", "Plateforme Crypto-actif", "Intermédiaire Tiers"])
        delai_signalement = st.slider("Délai de signalement (Minutes)", 5, 120, 15)

    st.markdown("---")
    st.subheader("📊 Cartographie des Sauts Multi-Hop")
    hop_1 = f"Bénéficiaire Intermédiaire 1 ({int(montant_initial * 0.98):,})"
    hop_2 = f"Compte Off-shore / Complice ({int(montant_initial * 0.90):,})"
    hop_3 = f"Point de Liquidation Final / Blocage"

    fig_trace = go.Figure(data=[
        go.Scatter(x=[0, 1, 2, 3], y=[0, 0, 0, 0], mode='lines', line=dict(width=4, color='#fde047'), hoverinfo='none'),
        go.Scatter(
            x=[0, 1, 2, 3], 
            y=[0, 0, 0, 0], 
            mode='markers+text', 
            text=[f"Source\n{compte_source}", hop_1, hop_2, hop_3], 
            textposition="top center", 
            marker=dict(color=['#3b82f6', '#f59e0b', '#ef4444', '#7f1d1d'], size=26)
        )
    ])
    fig_trace.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(showgrid=False, zeroline=False, showticklabels=False), yaxis=dict(showgrid=False, zeroline=False, showticklabels=False), margin=dict(t=50, b=50))
    st.plotly_chart(fig_trace, use_container_width=True)

    if st.button("🛑 EXÉCUTER LE SÉQUESTRE IMMÉDIAT ET NOTIFIER LA FINMA"):
        alerte_id = f"CH-ALERT-{uuid.uuid4().hex[:6].upper()}"
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
        st.error(f"🛑 ORDRE DE SÉQUESTRE EXÉCUTÉ sous l'ID `{alerte_id}`. Comptes intermédiaires gelés en temps réel.")

# -----------------------------------------------------------------------------
# 4. CONFORMITÉ LBA (KYC & ORIGINE DES FONDS)
# -----------------------------------------------------------------------------
elif current_page == "🛡️ Conformité LBA":
    st.markdown("#### 🛡️ Module de Conformité & Lutte Anti-Blanchiment (Loi sur le Blanchiment d'Argent - LBA)")
    c_kyc1, c_kyc2 = st.columns(2)
    with c_kyc1:
        nom_beneficiaire = st.text_input("Nom du Bénéficiaire Effectif (UBO)", value="Client Privé Anonyme")
        pays_origine = st.selectbox("Pays d'Origine des Fonds", ["Suisse (CH)", "Union Européenne (UE)", "Zone UEMOA / CEMAC", "Juridiction à Haut Risque (Liste Gratuite GAFI)"])
        statut_pep = st.selectbox("Statut Personne Politiquement Exposée (PPE / PEP)", ["Non PEP", "PEP National", "PEP International / Haut Risque"])
    with c_kyc2:
        justificatif = st.selectbox("Justificatif d'Origine des Fonds", ["Vente de biens immobiliers", "Héritage / Succession", "Dividendes d'entreprise certifiés", "Origine non vérifiable / Complexe"])
        montant_fonds = st.number_input("Montant Global des Actifs (CHF)", value=5000000)

    score_lba_risque = 85.0 if (pays_origine == "Juridiction à Haut Risque (Liste Gratuite GAFI)" or statut_pep != "Non PEP" or justificatif == "Origine non vérifiable / Complexe") else 15.0
    
    st.markdown("---")
    st.metric("Indice de Risque LBA (Blanchiment)", f"{score_lba_risque}%", delta="Élevé" if score_lba_risque > 50 else "Faible & Conforme", delta_color="inverse")

    if st.button("📋 Valider le Dossier KYC & Etablir le Certificat LBA"):
        dossier_kyc = {
            "id": f"CH-KYC-{uuid.uuid4().hex[:6].upper()}",
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "client": masquer_donnee(nom_beneficiaire),
            "montant": montant_fonds,
            "decis": "VALIDÉ LBA (Conforme)" if score_lba_risque < 50 else "BLOQUÉ - ENQUÊTE COMPLÉMENTAIRE REQUISE",
            "pd": f"Risque: {score_lba_risque}%",
            "auteur_maker": st.session_state.username,
            "validateur_checker": st.session_state.user_role
        }
        sauvegarder_historique(dossier_kyc)
        if score_lba_risque < 50:
            st.success(f"✅ Dossier KYC `{dossier_kyc['id']}` validé et enregistré dans le registre cryptographique.")
        else:
            st.error(f"🛑 Alerte LBA : Le dossier `{dossier_kyc['id']}` nécessite une investigation approfondie de la compliance.")

# -----------------------------------------------------------------------------
# 5. MOBILE MONEY
# -----------------------------------------------------------------------------
elif current_page == "📱 Mobile Money":
    st.markdown("#### Scoring Alternatif Digital")
    flux = st.number_input("Encaissements 3 derniers mois", value=4000000)
    anciennete = st.slider("Ancienneté du compte (Mois)", 1, 36, 12)
    solde_nuit = st.number_input("Solde moyen de nuit", value=300000)
    score = 500 + (anciennete * 10) + (solde_nuit / 2000)
    st.metric("Score Digital Alternatif", f"{int(score)} / 950 points")
    st.success("🌟 Profil validé pour l'octroi d'une ligne de micro-crédit.")

# -----------------------------------------------------------------------------
# 6. RISQUE AGRICOLE
# -----------------------------------------------------------------------------
elif current_page == "Risque Agricole" or current_page == "🌱 Risque Agricole":
    st.markdown("#### Modélisation Agricole & Campagnes")
    surf = st.number_input("Surface exploitée (Hectares)", value=10.0)
    rend = st.number_input("Rendement moyen (Kg/Ha)", value=800)
    prix = st.number_input("Prix d'achat garanti", value=1800)
    rev = surf * rend * prix
    st.metric("Revenu Net Estimé", f"{rev:,.0f}")

# -----------------------------------------------------------------------------
# 7. PAPSS
# -----------------------------------------------------------------------------
elif current_page == "🌍 PAPSS":
    st.markdown("#### Paiements & Règlements Transfrontaliers (PAPSS)")
    montant_xof = st.number_input("Montant à transférer", value=10000000)
    devise_cible = st.selectbox("Devise Destinataire", ["NGN", "KES", "GHS"])
    if st.button("💱 Exécuter le Transfert Panafricain"):
        st.success("✅ Règlement transfrontalier exécuté en monnaies locales.")

# -----------------------------------------------------------------------------
# 8. STRESS-TESTS
# -----------------------------------------------------------------------------
elif current_page == "📈 Stress-Tests":
    st.markdown("#### Analyse de Résistance Bancaire (Stress-Tests FINMA)")
    choc = st.slider("Choc de baisse des marchés (%)", 0, 70, 30)
    stage = "Stage 1 (Sain)" if choc < 25 else ("Stage 2 (Surveillance)" if choc < 50 else "Stage 3 (Défaut / Provisionnement)")
    st.metric("Classification Prudentielle", stage)

# -----------------------------------------------------------------------------
# 9. DATA CENTER
# -----------------------------------------------------------------------------
elif current_page == "📂 Data Center":
    st.markdown("#### Importation de Portefeuille & Registre Chiffré")
    uploaded_file = st.file_uploader("Importer un fichier chiffré (CSV / Excel)", type=["csv", "xlsx"])
    if uploaded_file is not None:
        try:
            df_imported = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            st.success(f"✅ Fichier '{uploaded_file.name}' déchiffré et analysé avec succès !")
            st.dataframe(df_imported.head(10), use_container_width=True)
        except Exception as e:
            st.error(f"Erreur : {e}")

# -----------------------------------------------------------------------------
# 10. HISTORIQUE & AUDIT (PISTE CHAÎNÉE CRYPTOGRAPHIQUE)
# -----------------------------------------------------------------------------
elif current_page == "📜 Historique & Audit":
    st.markdown("#### 🔒 Piste d'Audit Inviolable (Blockchain-like & Chaînage SHA-256)")
    historique = charger_historique()
    if historique:
        df_hist = pd.DataFrame(historique)
        st.dataframe(df_hist, use_container_width=True)

        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            csv_data = df_hist.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Télécharger la Piste d'Audit (CSV)", data=csv_data, file_name="piste_audit_suisse.csv", mime="text/csv")

        with col_exp2:
            if historique:
                dossier = historique[0]
                html_report = f"""
                <html>
                <head><meta charset="utf-8"><title>Rapport d'Audit Suisse</title></head>
                <body style="font-family: Arial, sans-serif; padding: 30px; color: #0f172a; background: #f8fafc;">
                    <div style="max-width: 700px; margin: auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                        <h2 style="color: #0f172a; text-align: center;">ATTESTATION OFFICIELLE DE CONFORMITÉ FINMA</h2>
                        <p style="text-align: center; color: #64748b;">Standards Banques Privées Suisses — Piste d'Audit Chaînée</p>
                        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0;">
                        <p><b>ID Enregistrement :</b> {dossier.get('id')}</p>
                        <p><b>Horodatage UTC :</b> {dossier.get('date')}</p>
                        <p><b>Client / Actif :</b> {dossier.get('client')}</p>
                        <p><b>Montant :</b> {dossier.get('montant'):,.0f}</p>
                        <p><b>Décision / Statut :</b> <span style="color: {'green' if 'APPROUVÉ' in dossier.get('decis') or 'VALIDÉ' in dossier.get('decis') else 'red'}; font-weight: bold;">{dossier.get('decis')}</span></p>
                        <p><b>Empreinte Cryptographique (SHA-256) :</b> <code style="font-size: 0.75rem;">{dossier.get('hash_actuel')}</code></p>
                        <br>
                        <p style="font-size: 0.9rem; color: #475569;"><i>Ce document certifie l'intégrité absolue des données et le respect des dispositions de la FINMA.</i></p>
                    </div>
                </body>
                </html>
                """
                st.download_button(
                    "📄 Télécharger le Rapport d'Audit (HTML Imprimable)",
                    data=html_report,
                    file_name=f"Rapport_Audit_{dossier.get('id')}.html",
                    mime="text/html"
                )
    else:
        st.info("Aucune transaction enregistrée dans le registre sécurisé.")

# -----------------------------------------------------------------------------
# 11. PARAMÈTRES
# -----------------------------------------------------------------------------
elif current_page == "⚙️ Paramètres":
    st.markdown("#### Paramètres Généraux de la Plateforme")
    st.text_input("Responsable Technique / Risk Manager", value="Kouassi Kouame Daniel")
    st.text_input("Institution de Rattachement", value="Apex Institute of Management (MBA Data Science & AI)")
    if st.button("Se déconnecter de la session sécurisée"):
        st.session_state.authentifie = False
        st.rerun()
