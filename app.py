import streamlit as st
import pandas as pd
import datetime
import uuid

# -----------------------------------------------------------------------------
# CONFIGURATION DE LA PAGE & STYLE CSS (iOS 18 + CHAMPS SOMBRE CORRIGÉS)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Plateforme FinTech & Anti-Fraude Pan-Africaine (BCEAO / BEAC / PAPSS)",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Arrière-plan global : Dégradé bleu nuit profond */
    .stApp {
        background: linear-gradient(145deg, #070b19 0%, #0f172a 50%, #090d16 100%);
        color: #f8fafc;
    }

    /* --- CARTES GLASSMORPHISM & EFFET 3D --- */
    .dashboard-card, div[data-testid="stMetric"], div.stForm, .stPlotlyChart {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 16px 32px 0 rgba(0, 0, 0, 0.37), 
                    inset 0 1px 0 0 rgba(255, 255, 255, 0.12);
        transition: all 0.35s cubic-bezier(0.25, 0.8, 0.25, 1);
        margin-bottom: 20px;
    }

    /* --- BARRE LATÉRALE STYLE iOS VERTICALE --- */
    section[data-testid="stSidebar"] {
        background: rgba(11, 18, 32, 0.92);
        backdrop-filter: blur(25px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        text-align: left;
        background: rgba(255, 255, 255, 0.03);
        color: #cbd5e1;
        border-radius: 14px;
        padding: 0.65rem 1rem;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.06);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        transition: all 0.25s ease;
        margin-bottom: 6px;
    }

    section[data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(29, 78, 216, 0.3) 100%);
        color: #ffffff;
        border: 1px solid rgba(59, 130, 246, 0.4);
        transform: translateX(4px);
    }

    /* --- CORRECTION DES CHAMPS DE SAISIE & SELECTBOX (MODE SOMBRE UNIFORME) --- */
    input, textarea {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
    }
    
    div[data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
    }

    .stSelectbox label, .stNumberInput label, .stRadio label, .stSlider label, .stTextInput label {
        color: #e2e8f0 !important;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# BARRE LATÉRALE : NAVIGATION VERTICALE
# -----------------------------------------------------------------------------
st.sidebar.image("https://img.icons8.com/color/96/shield-with-signature.png", width=55)
st.sidebar.title("Hub Panafricain")

zone_reglementaire = st.sidebar.selectbox(
    "Zone Réglementaire / Banque Centrale",
    [
        "UEMOA (BCEAO - Côte d'Ivoire, Sénégal, Bénin...)",
        "CEMAC (BEAC - Cameroun, Gabon, Congo...)",
        "Afrique de l'Est / M-Pesa (CBK - Kenya, Ouganda...)",
        "Afrique du Nord & Austral (SARB, CBE - Afrique du Sud, Égypte)",
        "Réseau Transfrontalier Panafricain (PAPSS / Afreximbank)"
    ]
)

institution_type = st.sidebar.selectbox(
    "Établissement Opérateur",
    [
        "Banque Commerciale (SGBCI, Ecobank, Coris, UBA)",
        "Opérateur Mobile Money (Wave, Orange, MTN, M-Pesa)",
        "FinTech / Neobanque (Djamo, Kuda)",
        "Institution de Microfinance (Baobab, Advans)",
        "Régulateur / CENTIF"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧭 Navigation")

if "active_module" not in st.session_state:
    st.session_state.active_module = "🏠 Tableau de bord"

modules = {
    "🏠 Tableau de bord": "Vue d'ensemble",
    "💳 Banque & Scoring Crédit": "Octroi prudentiel (Bâle III)",
    "🚨 Détection de Fraude": "Gel en cascade",
    "📱 Mobile Money & Néobanques": "Scoring alternatif",
    "🌱 Risque Agricole": "Modélisation cacao/café",
    "🌍 Paiements Transfrontaliers": "PAPSS",
    "📈 Stress-Tests Prudentiels": "Analyse de résistance",
    "📂 Sources de Données": "Data Center",
    "📜 Rapports & Historique": "Conformité ISO 20022",
    "⚙️ Paramètres": "Configuration"
}

for mod_name in modules.keys():
    if st.sidebar.button(mod_name, key=f"nav_{mod_name}"):
        st.session_state.active_module = mod_name

# -----------------------------------------------------------------------------
# AFFICHAGE DE LA PAGE ACTIVE
# -----------------------------------------------------------------------------
current_page = st.session_state.active_module
st.title(f"{current_page}")
st.caption(f"Plateforme unifiée — Zone : **{zone_reglementaire}** | Organisme : **{institution_type}**")
st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

if current_page == "🏠 Tableau de bord":
    st.header("Vue d'ensemble de la Sécurité Financière & du Scoring")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Dossiers Analysés", "1,482", delta="+12%")
    col2.metric("Fraude Interceptée", "99.4%", delta="+0.8%")
    col3.metric("Volume PAPSS", "42.8 Mds FCFA", delta="+15.4%")
    col4.metric("Indice de Risque", "Faible (A+)", delta="Stable")

elif current_page == "💳 Banque & Scoring Crédit":
    st.header("Analyse Solvabilité & Octroi Prudentiel (BCEAO / BEAC / Bâle III)")
    col_cr1, col_cr2 = st.columns(2)
    with col_cr1:
        secteur = st.selectbox("Secteur d'Activité", ["Agro-industrie", "Commerce Général", "BTP", "Services"])
        chiffre_affaires = st.number_input("Chiffre d'Affaires / Revenu mensuel (FCFA)", min_value=100000, value=5000000)
        engagements_encours = st.number_input("Remboursements en cours / mois (FCFA)", min_value=0, value=500000)
    with col_cr2:
        pret_demande = st.number_input("Montant du Prêt Demandé (FCFA)", min_value=100000, value=10000000)
        duree_mois = st.slider("Durée du remboursement (Mois)", 1, 60, 12)
        registre_impayes = st.radio("Fichage Banque Centrale", ["Aucun incident", "Incident actif / Interdit bancaire"])

    mensualite = (pret_demande * 1.02) / duree_mois
    taux_endettement = ((engagements_encours + mensualite) / chiffre_affaires) * 100 if chiffre_affaires > 0 else 100

    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    m1.metric("Mensualité", f"{mensualite:,.0f} FCFA / mois")
    m2.metric("Taux d'Endettement", f"{taux_endettement:.1f} %", delta="Max 33%" if taux_endettement <= 33 else "Hors norme", delta_color="normal" if taux_endettement <= 33 else "inverse")
    m3.metric("Capacité Dispo", f"{max(0, (chiffre_affaires * 0.33) - engagements_encours):,.0f} FCFA")

    if registre_impayes == "Incident actif / Interdit bancaire" or taux_endettement > 33:
        st.error("❌ **OCTROI REFUSÉ :** Indicateurs prudentiels non respectés.")
    else:
        st.success(f"✅ **PRÊT VALIDÉ :** Déblocage autorisé de {pret_demande:,.0f} FCFA.")

elif current_page == "🚨 Détection de Fraude":
    st.header("Moteur d'Interception des Fraudes & Traçage des Comptes Mules")
    st.text_input("Référence UTRN", f"UTRN-{uuid.uuid4().hex[:10].upper()}")
    st.text_input("Compte Émetteur", placeholder="+225...")
    st.number_input("Montant Contesté", value=2500000)
    if st.button("🚨 DÉCLENCHER LE GEL"):
        st.error("🛑 Ordre de blocage systémique transmis.")

elif current_page == "📱 Mobile Money & Néobanques":
    st.header("Alternative Credit Scoring (Wave, Orange, MTN, M-Pesa)")
    st.metric("Score Digital", "780 / 950 points (Catégorie A)")

elif current_page == "🌱 Risque Agricole":
    st.header("Modélisation Agricole (Cacao / Café)")
    st.metric("Revenu Net Campagne", "12,000,000 FCFA")

elif current_page == "🌍 Paiements Transfrontaliers":
    st.header("Plateforme PAPSS")
    st.success("✅ Compensation multidevises instantanée validée.")

elif current_page == "📈 Stress-Tests Prudentiels":
    st.header("Analyse des Chocs (Bâle III / IFRS 9)")
    st.metric("Classification IFRS 9", "Stage 1 (Normal)")

elif current_page == "📂 Sources de Données":
    st.header("Data Center & Registre")
    st.write("BCEAO, BEAC, PAPSS, BIC connectés.")

elif current_page == "📜 Rapports & Historique":
    st.header("Conformité CENTIF & ISO 20022")
    if st.button("Générer le rapport XML"):
        st.success("✅ Rapport généré avec succès.")

elif current_page == "⚙️ Paramètres":
    st.header("Paramètres")
    st.text_input("Administrateur", value="Kouassi Kouame Daniel")
    
