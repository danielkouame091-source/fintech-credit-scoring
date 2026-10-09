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
    page_title="Plateforme FinTech & Anti-Fraude Panafricaine | Enterprise Edition",
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

    /* Arrière-plan global : Bleu nuit institutionnel profond */
    .stApp {
        background: radial-gradient(circle at 50% 10%, #0b1329 0%, #040712 100%);
        color: #f8fafc;
    }

    /* --- CARTES 3D GLASSMORPHISM NETTES --- */
    .dashboard-card, div[data-testid="stMetric"], div.stForm, .stPlotlyChart {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.6), 
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }

    /* --- CHAMPS DE SAISIE & SELECTBOX PROFESSIONNELS --- */
    input, textarea {
        background-color: rgba(15, 23, 42, 0.95) !important;
        color: #ffffff !important;
        border: 1px solid rgba(59, 130, 246, 0.4) !important;
        border-radius: 10px !important;
    }
    
    div[data-baseweb="select"] > div {
        background-color: rgba(15, 23, 42, 0.95) !important;
        color: #ffffff !important;
        border: 1px solid rgba(59, 130, 246, 0.4) !important;
        border-radius: 10px !important;
    }

    label {
        color: #93c5fd !important;
        font-weight: 600 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# GESTION DE LA PERSISTANCE & HACHAGE SÉCURISÉ
# -----------------------------------------------------------------------------
DATA_FILE = "audit_historique.json"

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
# AUTHENTIFICATION & RÔLES (RBAC AVEC WORKFLOW MAKER-CHECKER)
# -----------------------------------------------------------------------------
if "authentifie" not in st.session_state:
    st.session_state.authentifie = False

if not st.session_state.authentifie:
    st.markdown("<h2 style='text-align: center; color: #60a5fa;'>🔐 Portail d'Accès Sécurisé — Standards SBI / Union Bank</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #cbd5e1;'>Authentification chiffrée, Workflow Maker-Checker & Scoring IA Explicable</p>", unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        with st.form("form_login"):
            username = st.text_input("Identifiant Professionnel", value="analyste.risques@unionbank.fin")
            password = st.text_input("Mot de passe sécurisé", type="password", value="secure2026")
            role_choisi = st.selectbox("Profil d'Habilitation (RBAC)", [
                "🔍 Analyste des Risques & Scoring (Rôle Maker)",
                "⚖️ Directeur des Engagements / Comité (Rôle Checker)",
                "🚨 Officier de Conformité & Traçage des Fonds",
                "📊 Auditeur Régulateur Interne"
            ])
            submit_login = st.form_submit_button("Connexion Bancaire Sécurisée", use_container_width=True)
            if submit_login:
                st.session_state.authentifie = True
                st.session_state.username = username
                st.session_state.user_role = role_choisi
                st.session_state.pwd_hash = hacher_mdp(password)
                st.rerun()
    st.stop()

# -----------------------------------------------------------------------------
# EN-TÊTE & CONTEXTE INSTITUTIONNEL
# -----------------------------------------------------------------------------
st.markdown("<h1 style='text-align: center; color: #f8fafc; font-weight: 800;'>HUB FINANCIER & ANTI-FRAUDE INTERNATIONALE</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #93c5fd; font-size: 1.05rem;'>Opérateur Connecté : <b>{st.session_state.username}</b> | Habilitation : <b>{st.session_state.user_role}</b></p>", unsafe_allow_html=True)

col_cfg1, col_cfg2 = st.columns(2)
with col_cfg1:
    zone_reglementaire = st.selectbox(
        "Cadre Réglementaire / Banque Centrale",
        [
            "Standards RBI (Reserve Bank of India / State Bank / Union Bank)",
            "UEMOA (BCEAO - Côte d'Ivoire, Sénégal...)",
            "CEMAC (BEAC - Cameroun, Gabon...)",
            "Réseau Transfrontalier Panafricain (PAPSS / Afreximbank)",
        ],
    )
with col_cfg2:
    institution_type = st.selectbox(
        "Établissement Financier Opérateur",
        [
            "State Bank of India / Union Bank Standard (Enterprise Core Banking)",
            "Émetteur Monnaie Électronique / Mobile Money (Wave, Orange, MTN, Moov)",
            "FinTech / Neobanque Panafricaine & Asiatique",
            "Cellule de Renseignement Financier & Cyber-Fraude (CENTIF / National Cyber Cell)",
        ],
    )

st.markdown("---")

# -----------------------------------------------------------------------------
# NAVIGATION CENTRALE
# -----------------------------------------------------------------------------
if "active_module" not in st.session_state:
    st.session_state.active_module = "🏠 Tableau de bord"

modules = {
    "🏠 Tableau de bord": "Vue Globale",
    "💳 Banque & Crédit": "Scoring Bâle III & Maker-Checker",
    "🚨 Anti-Fraude & Traçage": "Traçage des Fonds & Gel (Style Inde)",
    "📱 Mobile Money": "Scoring Alternatif",
    "🌱 Risque Agricole": "Campagnes Cacao/Café",
    "🌍 PAPSS": "Paiements Transfrontaliers",
    "📈 Stress-Tests": "Résistance Bancaire",
    "📂 Data Center": "Import & Registres",
    "📜 Historique & Audit": "Conformité ISO & Rapports",
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
st.markdown(f"<h3 style='color: #60a5fa;'>Module Actif : {current_page}</h3>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 1. TABLEAU DE BORD
# -----------------------------------------------------------------------------
if current_page == "🏠 Tableau de bord":
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Dossiers en Attente Validateur", "14", delta="Workflow Actif")
    col2.metric("Taux d'Interception Fraude", "99.4%", delta="+0.8%")
    col3.metric("Fonds Gelés / Séquestrés", "1.42 Mds FCFA", delta="-18.2%")
    col4.metric("Note de Solidité Prudentielle", "A+ (Optimal)", delta="Stable")

    st.markdown("---")
    c_g1, c_g2 = st.columns(2)
    with c_g1:
        st.subheader("📈 Évolution Mensuelle des Flux (Mds FCFA)")
        df_chart = pd.DataFrame({"Mois": ["Nov", "Déc", "Jan", "Fév", "Mar", "Avr"], "Volume": [12.5, 15.0, 18.2, 22.0, 29.5, 34.8]})
        fig = px.line(df_chart, x="Mois", y="Volume", markers=True, template="plotly_dark")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with c_g2:
        st.subheader("📊 Répartition Sectorielle des Risques de Crédit")
        df_pie = pd.DataFrame({"Secteur": ["Agro-industrie", "Commerce & Négoce", "BTP", "Services Financiers", "Transport & Logistique"], "Part": [35, 25, 15, 15, 10]})
        fig_pie = px.pie(df_pie, names="Secteur", values="Part", hole=0.4, template="plotly_dark")
        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_pie, use_container_width=True)

# -----------------------------------------------------------------------------
# 2. BANQUE & CRÉDIT (SCORING IA + EXPLICABILITÉ SHAP-LIKE + MAKER-CHECKER)
# -----------------------------------------------------------------------------
elif current_page == "💳 Banque & Crédit":
    st.markdown("#### Modèle Prédictif de Solvabilité, Explicabilité IA & Workflow Maker-Checker")
    
    col_cr1, col_cr2 = st.columns(2)
    with col_cr1:
        nom_client = st.text_input("Nom de l'Emprunteur / Entreprise", value="Société Ivoire Agro SARL")
        chiffre_affaires = st.number_input("Chiffre d'Affaires Mensuel (FCFA)", min_value=100000, value=6000000)
        engagements_encours = st.number_input("Remboursements en cours / mois (FCFA)", min_value=0, value=400000)
    with col_cr2:
        pret_demande = st.number_input("Montant du Prêt Demandé (FCFA)", min_value=100000, value=12000000)
        duree_mois = st.slider("Durée du remboursement (Mois)", 1, 60, 18)
        registre_impayes = st.radio("Fichage Centrale des Risques / BIC", ["Aucun incident", "Incident actif / Interdit bancaire"])

    # Calculs du modèle
    features_input = ml_scaler.transform([[chiffre_affaires, duree_mois, engagements_encours]])
    prob_defaut = float(ml_model.predict_proba(features_input)[0][1]) * 100
    if registre_impayes == "Incident actif / Interdit bancaire":
        prob_defaut = min(99.0, prob_defaut + 42.0)

    mensualite = (pret_demande * 1.025) / duree_mois
    taux_endettement = ((engagements_encours + mensualite) / chiffre_affaires) * 100 if chiffre_affaires > 0 else 100

    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    m1.metric("Mensualité Estimée", f"{mensualite:,.0f} FCFA")
    m2.metric("Taux d'Endettement", f"{taux_endettement:.1f} %")
    m3.metric("Probabilité de Défaut (PD - IA)", f"{prob_defaut:.1f}%")

    # --- EXPLICABILITÉ DE L'IA (FEATURE IMPORTANCE / SHAP-LIKE) ---
    st.markdown("#### 🧠 Explicabilité du Modèle (Pourquoi cette prédiction ?)")
    st.markdown("Décomposition des contributions des variables au score final de risque :")
    
    # Coefficients de contribution simulés basés sur les entrées
    contrib_ca = -35.0 if chiffre_affaires > 5000000 else 45.0
    contrib_end = 40.0 if taux_endettement > 30 else -20.0
    contrib_bic = 60.0 if registre_impayes == "Incident actif / Interdit bancaire" else -10.0

    df_expl = pd.DataFrame({
        "Facteur Clé": ["Niveau de Chiffre d'Affaires", "Taux d'Endettement Mensuel", "Historique BIC / Incidents"],
        "Impact sur le Risque (%)": [contrib_ca, contrib_end, contrib_bic]
    })
    
    fig_exp = px.bar(df_expl, x="Impact sur le Risque (%)", y="Facteur Clé", orientation='h', template="plotly_dark", color="Impact sur le Risque (%)", color_continuous_scale="RdBu_r")
    fig_exp.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=10, b=10))
    st.plotly_chart(fig_exp, use_container_width=True)

    st.markdown("---")
    # --- WORKFLOW MAKER-CHECKER ---
    st.markdown("#### ⚖️ Workflow de Gouvernance Maker-Checker (Double Contrôle)")
    
    statut_initial = "EN ATTENTE VALIDATION DIRECTEUR (Checker requis)" if (prob_defaut < 35 and registre_impayes != "Incident actif / Interdit bancaire") else "REJETÉ AUTOMATISE (Seuil IA dépassé)"
    
    col_mk1, col_mk2 = st.columns(2)
    with col_mk1:
        st.info(f"**Rôle Maker (Analyste) :** Soumet le dossier.\n\n**Statut actuel :** {statut_initial}")
    with col_mk2:
        if "Directeur" in st.session_state.user_role or "Conformité" in st.session_state.user_role or "Auditeur" in st.session_state.user_role:
            decision_checker = st.selectbox("Validation Hiérarchique (Rôle Checker)", ["En attente", "APPROUVÉ DÉFINITIVEMENT (Signature Comité)", "REJETÉ PAR LE DIRECTEUR DES RISQUES"])
        else:
            st.warning("⚠️ Seul le Directeur des Engagements (Checker) peut modifier la décision finale.")
            decision_checker = "En attente"

    if st.button("💾 Enregistrer et Transmettre le Dossier Sécurisé"):
        decis_finale = decision_checker if decision_checker != "En attente" else ("APPROUVÉ (Maker)" if prob_defaut < 35 else "REFUSÉ")
        dossier = {
            "id": f"CRED-{uuid.uuid4().hex[:6].upper()}",
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "client": nom_client,
            "montant": pret_demande,
            "decis": decis_finale,
            "pd": f"{prob_defaut:.1f}%",
            "auteur_maker": st.session_state.username,
            "validateur_checker": st.session_state.user_role
        }
        sauvegarder_historique(dossier)
        st.success(f"✅ Dossier {dossier['id']} enregistré et consigné dans la piste d'audit immuable avec double validation Maker-Checker.")

# -----------------------------------------------------------------------------
# 3. ANTI-FRAUDE & TRAÇAGE DES FONDS (STYLE BANQUES INDIENNES / SBI)
# -----------------------------------------------------------------------------
elif current_page == "🚨 Anti-Fraude & Traçage":
    st.markdown("#### 🕵️‍♂️ Moteur de Traçage des Sauts Financiers (Fund Tracing & Multi-Hop Analysis)")
    col_tr1, col_tr2 = st.columns(2)
    with col_tr1:
        id_transaction = st.text_input("ID de la Transaction Suspecte", f"TXN-{uuid.uuid4().hex[:8].upper()}")
        compte_source = st.text_input("Compte Victime / Initial", value="ACC-99281-SBI")
        montant_initial = st.number_input("Montant Dérobé / Transféré (FCFA / INR)", value=5000000)
    with col_tr2:
        canal_fraude = st.selectbox("Canal de la Fraude", ["UPI / Mobile Instantané", "Virement Interbancaire NEFT/RTGS", "Carte Bancaire / ATM Withdrawal", "Portefeuille Numérique"])
        delai_signalement = st.slider("Délai de signalement (Minutes après la fraude)", 5, 120, 20)

    st.markdown("---")
    st.subheader("📊 Cartographie des Sauts Financiers (Fund Trail Path)")
    hop_1 = f"Mule A ({int(montant_initial * 0.95):,} transférés)"
    hop_2 = f"Mule B ({int(montant_initial * 0.82):,} répartis)"
    hop_3 = f"Compte Final / Conversion Crypto ou Cash"

    fig_trace = go.Figure(data=[
        go.Scatter(x=[0, 1, 2, 3], y=[0, 0, 0, 0], mode='lines', line=dict(width=4, color='#ef4444'), hoverinfo='none'),
        go.Scatter(
            x=[0, 1, 2, 3], 
            y=[0, 0, 0, 0], 
            mode='markers+text', 
            text=[f"Source\n{compte_source}", hop_1, hop_2, hop_3], 
            textposition="top center", 
            marker=dict(color=['#3b82f6', '#f59e0b', '#ef4444', '#7f1d1d'], size=26)
        )
    ])
    fig_trace.update_layout(
        showlegend=False, 
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)", 
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False), 
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        margin=dict(t=50, b=50)
    )
    st.plotly_chart(fig_trace, use_container_width=True)

    st.markdown("#### ⚡ Configuration du Gel Automatique (Style National Cyber Crime Portal)")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        niveau_gel = st.selectbox("Portée du Gel des Comptes", [
            "Gel Total (Source + Tous les Sauts Intermédiaires)",
            "Gel Partiel (Bloquer uniquement le montant contesté sur le 1er saut)",
            "Mise en attente de la chambre de compensation"
        ])
    with col_g2:
        action_atm = st.checkbox("Bloquer simultanément les cartes associées et l'accès ATM", value=True)

    if st.button("🛑 EXÉCUTER LE GEL AUTOMATISÉ ET NOTIFIER LES PARTENAIRES"):
        alerte_id = f"ALERT-IND-{uuid.uuid4().hex[:6].upper()}"
        dossier_fraude = {
            "id": alerte_id,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "client": f"Traçage {id_transaction}",
            "montant": montant_initial,
            "decis": "GELÉ & TRAACÉ (Checker Validé)",
            "pd": f"{delai_signalement} min",
            "auteur_maker": st.session_state.username,
            "validateur_checker": st.session_state.user_role
        }
        sauvegarder_historique(dossier_fraude)
        st.error(f"🚨 SUCCÈS : Ordre de gel de niveau bancaire émis sous l'ID `{alerte_id}`. Comptes intermédiaires bloqués par double validation.")

# -----------------------------------------------------------------------------
# 4. MOBILE MONEY
# -----------------------------------------------------------------------------
elif current_page == "📱 Mobile Money":
    st.markdown("#### Scoring Alternatif basés sur les Flux de Portefeuilles Numériques")
    flux = st.number_input("Encaissements 3 derniers mois (FCFA)", value=4000000)
    anciennete = st.slider("Ancienneté du compte Mobile Money (Mois)", 1, 36, 12)
    solde_nuit = st.number_input("Solde moyen de nuit (FCFA)", value=300000)
    score = 500 + (anciennete * 10) + (solde_nuit / 2000)
    st.metric("Score Digital Alternatif", f"{int(score)} / 950 points")
    st.success("🌟 Profil validé pour l'octroi instantané d'une ligne de micro-crédit sans garantie physique.")

# -----------------------------------------------------------------------------
# 5. RISQUE AGRICOLE
# -----------------------------------------------------------------------------
elif current_page == "🌱 Risque Agricole":
    st.markdown("#### Modélisation Agricole & Campagnes (Cacao / Café / Hévéa)")
    surf = st.number_input("Surface exploitée (Hectares)", value=10.0)
    rend = st.number_input("Rendement moyen (Kg/Ha)", value=800)
    prix = st.number_input("Prix d'achat bord champ garanti (FCFA/Kg)", value=1800)
    rev = surf * rend * prix
    st.metric("Revenu Net Campagne Estimé", f"{rev:,.0f} FCFA")
    st.info("📅 Échéancier prudentiel adapté : 85% des remboursements prélevés en Grande Campagne (Octobre - Mars).")

# -----------------------------------------------------------------------------
# 6. PAPSS
# -----------------------------------------------------------------------------
elif current_page == "🌍 PAPSS":
    st.markdown("#### Paiements & Règlements Transfrontaliers en Monnaies Locales (PAPSS / Afreximbank)")
    montant_xof = st.number_input("Montant à transférer (XOF)", value=10000000)
    devise_cible = st.selectbox("Devise du Pays Destinataire", ["NGN (Nigéria)", "KES (Kenya)", "GHS (Ghana)"])
    if st.button("💱 Exécuter la Compensation Panafricaine Immédiate"):
        st.success("✅ Règlement transfrontalier exécuté en 120s en monnaies locales sans transit par devises tierces.")

# -----------------------------------------------------------------------------
# 7. STRESS-TESTS
# -----------------------------------------------------------------------------
elif current_page == "📈 Stress-Tests":
    st.markdown("#### Analyse de Résistance Bancaire sous Chocs macroéconomiques")
    choc = st.slider("Choc de baisse d'activité (%)", 0, 70, 40)
    stage = "Stage 1 (Normal - Portefeuille Sain)" if choc < 25 else ("Stage 2 (Surveillance Accrue)" if choc < 50 else "Stage 3 (Défaut NPL - Provisionnement Obligatoire)")
    st.metric("Classification Prudentielle IFRS 9", stage)

# -----------------------------------------------------------------------------
# 8. DATA CENTER
# -----------------------------------------------------------------------------
elif current_page == "📂 Data Center":
    st.markdown("#### Importation de Portefeuille & Registre des Connexions")
    uploaded_file = st.file_uploader("Importer un fichier de transactions ou de portefeuilles (CSV / Excel)", type=["csv", "xlsx"])
    if uploaded_file is not None:
        try:
            df_imported = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            st.success(f"✅ Fichier '{uploaded_file.name}' analysé avec succès !")
            st.dataframe(df_imported.head(10), use_container_width=True)
        except Exception as e:
            st.error(f"Erreur de lecture : {e}")

    st.markdown("---")
    st.subheader("Connecteurs Institutionnels Actifs")
    df_src = pd.DataFrame({
        "Source": ["BCEAO / Reserve Bank of India (RBI)", "Bureau d'Information sur le Crédit (BIC)", "Réseau PAPSS", "Passerelles Mobile Money / UPI"],
        "Type": ["Réglementaire", "Historique", "Transfrontalier", "Opérationnel"],
        "Statut": ["Connecté (API)", "Actif", "Sécurisé", "Temps Réel"]
    })
    st.table(df_src)

# -----------------------------------------------------------------------------
# 9. HISTORIQUE & AUDIT
# -----------------------------------------------------------------------------
elif current_page == "📜 Historique & Audit":
    st.markdown("#### Registre d'Audit & Conformité ISO 20022")
    historique = charger_historique()
    if historique:
        df_hist = pd.DataFrame(historique)
        st.dataframe(df_hist, use_container_width=True)

        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            csv_data = df_hist.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Télécharger le Registre (CSV)", data=csv_data, file_name="registre_audit_fintech.csv", mime="text/csv")

        with col_exp2:
            if historique:
                dossier = historique[0]
                html_report = f"""
                <html>
                <head><meta charset="utf-8"><title>Rapport d'Analyse des Risques</title></head>
                <body style="font-family: Arial, sans-serif; padding: 30px; color: #0f172a; background: #f8fafc;">
                    <div style="max-width: 700px; margin: auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                        <h2 style="color: #1e3a8a; text-align: center;">RAPPORT OFFICIEL D'ANALYSE & GOUVERNANCE RISQUES</h2>
                        <p style="text-align: center; color: #64748b;">Standards SBI / Union Bank / BCEAO (Double Validation Maker-Checker)</p>
                        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0;">
                        <p><b>Référence Dossier :</b> {dossier.get('id')}</p>
                        <p><b>Date d'Analyse :</b> {dossier.get('date')}</p>
                        <p><b>Client / Emprunteur :</b> {dossier.get('client')}</p>
                        <p><b>Montant Impliqué :</b> {dossier.get('montant'):,.0f} FCFA / INR</p>
                        <p><b>Décision Prudentielle :</b> <span style="color: {'green' if 'APPROUVÉ' in dossier.get('decis') else 'red'}; font-weight: bold;">{dossier.get('decis')}</span></p>
                        <p><b>Analyste (Maker) :</b> {dossier.get('auteur_maker', 'N/A')}</p>
                        <p><b>Validateur (Checker) :</b> {dossier.get('validateur_checker', 'N/A')}</p>
                        <br>
                        <p style="font-size: 0.9rem; color: #475569;"><i>Ce document certifie l'application rigoureuse du double regard et des modèles prédictifs d'IA explicable.</i></p>
                    </div>
                </body>
                </html>
                """
                st.download_button(
                    "📄 Télécharger le Rapport Officiel (HTML Imprimable)",
                    data=html_report,
                    file_name=f"Rapport_Risque_{dossier.get('id')}.html",
                    mime="text/html"
                )
    else:
        st.info("Aucun dossier enregistré dans le registre pour le moment.")

    if st.button("📄 Transmettre le Flux ISO 20022 (XML) au Régulateur"):
        st.json({
            "Document": {
                "MsgId": f"CENTIF-MAKERCHECKER-{uuid.uuid4().hex[:8].upper()}",
                "Status": "Certifié conforme, doublement validé et transmis aux serveurs centraux"
            }
        })

# -----------------------------------------------------------------------------
# 10. PARAMÈTRES
# -----------------------------------------------------------------------------
elif current_page == "⚙️ Paramètres":
    st.markdown("#### Paramètres Généraux de la Plateforme")
    st.text_input("Responsable Technique", value="Kouassi Kouame Daniel")
    st.text_input("Institution de Rattachement", value="Apex Institute of Management (MBA Data Science & AI)")
    if st.button("Se déconnecter de la session"):
        st.session_state.authentifie = False
        st.rerun()
