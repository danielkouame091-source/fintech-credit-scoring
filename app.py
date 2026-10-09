import datetime
import uuid
import pandas as pd
import streamlit as st

# -----------------------------------------------------------------------------
# CONFIGURATION DE LA PAGE & STYLE CSS (Dashboard SaaS Pro + Effet 3D)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Credit Risk Dashboard - Plateforme FinTech Panafricaine",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Fond général propre type SaaS Dashboard (similaire à l'image) */
    .stApp {
        background-color: #f4f6f9;
        color: #1e293b;
    }

    /* --- SIDEBAR STYLE SAAS (Sombre à gauche avec icônes) --- *
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #e2e8f0;
    }
    section[data-testid="stSidebar"] * {
        color: #94a3b8 !important;
    }
    section[data-testid="stSidebar"] .stSelectbox label, 
    section[data-testid="stSidebar"] .stRadio label,
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #f8fafc !important;
    }

    /* --- CARTES DU DASHBOARD : EFFET 3D & RELIEF (Glassmorphism clair) --- */
    .dashboard-card, div[data-testid="stMetric"], div.stForm, .stPlotlyChart {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 
                    0 8px 10px -6px rgba(0, 0, 0, 0.05); /* Effet 3D relief doux */
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        margin-bottom: 20px;
    }

    /* Effet de lévitation 3D au survol des cartes */
    .dashboard-card:hover, div[data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 35px -5px rgba(0, 0, 0, 0.1), 
                    0 10px 15px -5px rgba(0, 0, 0, 0.05);
        border-color: #cbd5e1;
    }

    /* Boutons stylisés Pro 3D */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    }

    /* Onglets épurés */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #e2e8f0;
        padding: 6px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
        color: #475569;
    }
    .stTabs [aria-selected="true"] {
        background: #ffffff !important;
        color: #1e293b !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# BARRE LATÉRALE : NAVIGATION FAÇON SAAS
# -----------------------------------------------------------------------------
st.sidebar.image("https://img.icons8.com/color/96/shield-with-signature.png", width=55)
st.sidebar.title("Credit Risk Hub")

style_menu = st.sidebar.selectbox(
    "🎛️ Style de Navigation",
    ["Dashboard SaaS 3D", "Menu Classique (Standard)"]
)

zone_reglementaire = st.sidebar.selectbox(
    "Zone Réglementaire / Banque Centrale",
    [
        "UEMOA (BCEAO - Côte d'Ivoire, Sénégal...)",
        "CEMAC (BEAC - Cameroun, Gabon...)",
        "Afrique de l'Est / M-Pesa (Kenya)",
        "Réseau Transfrontalier Panafricain (PAPSS)"
    ]
)

institution_type = st.sidebar.selectbox(
    "Établissement Opérateur",
    [
        "Banque Commerciale (Ecobank, SGBCI, UBA...)",
        "Opérateur Mobile Money (Wave, Orange, MTN)",
        "FinTech / Neobanque (Djamo, Kuda)"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("🔒 Conformité Active")
st.sidebar.write("✔️ Standard ISO 20022")
st.sidebar.write("✔️ LCB-FT (CENTIF / GAFI)")
st.sidebar.write("✔️ Normes Bâle III / IFRS 9")

# En-tête principal du Dashboard
col_head1, col_head2 = st.columns([4, 1])
with col_head1:
    st.title("Credit Risk Dashboard")
    st.caption(f"Zone active : **{zone_reglementaire}** | Opérateur : **{institution_type}**")
with col_head2:
    st.markdown("""
        <div style="background: #ffffff; padding: 10px; border-radius: 12px; border: 1px solid #e2e8f0; text-align: center;">
            <p style="margin: 0; font-size: 12px; color: #64748b;">Relationship Manager</p>
            <p style="margin: 0; font-size: 14px; font-weight: bold; color: #0f172a;">Kouassi Daniel</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# ONGLETS PRINCIPAUX DU TABLEAU DE BORD
# -----------------------------------------------------------------------------
tab_fraud, tab_credit, tab_mobile, tab_agri, tab_papss, tab_stress, tab_compliance = st.tabs([
    "🚨 1. Gel en Cascade",
    "💳 2. Scoring Prudentiel",
    "📱 3. Mobile Money",
    "🌱 4. Agro-Saisonnier",
    "🌍 5. PAPSS",
    "📈 6. Stress-Test",
    "📜 7. Conformité"
])

# -----------------------------------------------------------------------------
# TAB 1 : BLOCAGE EN CASCADE & FRAUD RINGS
# -----------------------------------------------------------------------------
with tab_fraud:
    st.subheader("Moteur d'Interception des Fraudes & Traçage des Comptes Mules")
    
    # Carte 3D conteneur
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            utrn = st.text_input("Référence Transactionnelle Unique (UTRN)", f"UTRN-{uuid.uuid4().hex[:10].upper()}")
            compte_victime = st.text_input("Compte Émetteur / Déclarant", placeholder="+225 07 00 00 00 00")
            montant_contesté = st.number_input("Montant Contesté (FCFA)", min_value=1000, value=2500000, step=50000)

        with c2:
            plateforme_source = st.selectbox("Plateforme d'Origine", ["Wave", "Orange Money", "MTN MoMo", "M-Pesa", "Virement Bancaire"])
            typologie_fraude = st.selectbox("Typologie de l'Incident", [
                "Erreur de Saisie de Numéro",
                "Ingénierie Sociale / Phishing",
                "Compte Mule / Blanchiment Suspecté"
            ])
            niveau_urgence = st.select_slider("Urgence Réglementaire", options=["CRITIQUE (Gel < 30s)", "ÉLEVÉ", "MODÉRÉ"])

    st.subheader("🕸️ Graphe de Transferts Multi-Réseaux")
    if st.button("🚨 DÉCLENCHER L'ORDRE DE GEL SYSTÉMIQUE"):
        st.error(f"🛑 ORDRE DE BLOCAGE TRANSMIS — RÉF : {utrn}")
        st.success("✅ Comptes récepteurs bloqués avec succès sur l'ensemble des réseaux connectés.")

# -----------------------------------------------------------------------------
# TAB 2 : SCORING D'OCTROI DE PRÊT PRUDENTIEL
# -----------------------------------------------------------------------------
with tab_credit:
    st.subheader("Analyse Solvabilité & Octroi Prudentiel (BCEAO / Bâle III)")
    
    col_cr1, col_cr2 = st.columns(2)
    with col_cr1:
        secteur = st.selectbox("Secteur d'Activité", ["Agro-industrie", "Commerce Général", "BTP & Infrastructure", "Services"])
        chiffre_affaires = st.number_input("Chiffre d'Affaires / Revenu mensuel (FCFA)", min_value=100000, value=5000000)
        engagements_encours = st.number_input("Remboursements en cours / mois (FCFA)", min_value=0, value=500000)

    with col_cr2:
        pret_demande = st.number_input("Montant du Prêt Demandé (FCFA)", min_value=100000, value=10000000)
        duree_mois = st.slider("Durée (Mois)", 1, 60, 12)
        registre_impayes = st.radio("Fichage Banque Centrale (CIP / BIC)", ["Aucun incident", "Incident actif"])

    mensualite = (pret_demande * 1.02) / duree_mois
    taux_endettement = ((engagements_encours + mensualite) / chiffre_affaires) * 100 if chiffre_affaires > 0 else 100

    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    m1.metric("Mensualité Estimée", f"{mensualite:,.0f} FCFA")
    m2.metric("Taux d'Endettement", f"{taux_endettement:.1f} %", delta="Plafond 33%" if taux_endettement <= 33 else "Hors norme", delta_color="normal" if taux_endettement <= 33 else "inverse")
    m3.metric("Score Risque", "742 / 900", delta="Low Risk")

    if registre_impayes == "Incident actif" or taux_endettement > 33:
        st.error("❌ **OCTROI REFUSÉ :** Indicateurs prudentiels non respectés.")
    else:
        st.success(f"✅ **PRÊT VALIDÉ :** Déblocage autorisé de {pret_demande:,.0f} FCFA.")

# -----------------------------------------------------------------------------
# LES AUTRES ONGLETS (Mobile, Agro, PAPSS, Stress-Test, Conformité)
# -----------------------------------------------------------------------------
with tab_mobile:
    st.subheader("Alternative Credit Scoring (Mobile Money & Neobanques)")
    st.info("Évaluation des marchands basée sur les flux Wave, Orange Money et M-Pesa.")
    st.metric("Score Digital Alternatif", "780 points (Catégorie A)")

with tab_agri:
    st.subheader("Modélisation Agro-Saisonnier (Cacao, Café, Anacarde)")
    st.info("Alignement des échéanciers sur les campagnes de récolte.")

with tab_papss:
    st.subheader("Paiements Transfrontaliers PAPSS / Afreximbank")
    st.info("Compensation multidevises en monnaie locale (XOF ↔ NGN ↔ KES).")

with tab_stress:
    st.subheader("Stress-Test Prudentiel (Bâle III / IFRS 9)")
    st.info("Simulation de résistance face à une baisse de chiffre d'affaires.")

with tab_compliance:
    st.subheader("Conformité CENTIF / ANIF & ISO 20022")
    if st.button("📄 Générer le Rapport XML ISO 20022"):
        st.success("✅ Rapport d'alerte prêt pour transmission au régulateur.")
