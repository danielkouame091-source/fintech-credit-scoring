import datetime
import json
import os
import uuid
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# -----------------------------------------------------------------------------
# CONFIGURATION DE LA PAGE & STYLE CSS (iOS 18 + Glassmorphism 3D)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title=(
        "Plateforme FinTech & Anti-Fraude Pan-Africaine (BCEAO / BEAC / PAPSS)"
    ),
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
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

    /* --- CHAMPS DE SAISIE & SELECTBOX (MODE SOMBRE UNIFORME) --- */
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
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# GESTION DE LA PERSISTANCE (HISTORIQUE LOCAL JSON)
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


# -----------------------------------------------------------------------------
# BARRE LATÉRALE : NAVIGATION VERTICALE
# -----------------------------------------------------------------------------
st.sidebar.image(
    "https://img.icons8.com/color/96/shield-with-signature.png", width=55
)
st.sidebar.title("Hub Panafricain")

zone_reglementaire = st.sidebar.selectbox(
    "Zone Réglementaire / Banque Centrale",
    [
        "UEMOA (BCEAO - Côte d'Ivoire, Sénégal, Bénin...)",
        "CEMAC (BEAC - Cameroun, Gabon, Congo...)",
        "Afrique de l'Est / M-Pesa (CBK - Kenya, Ouganda...)",
        "Afrique du Nord & Austral (SARB, CBE - Afrique du Sud, Égypte)",
        "Réseau Transfrontalier Panafricain (PAPSS / Afreximbank)",
    ],
)

institution_type = st.sidebar.selectbox(
    "Établissement Opérateur",
    [
        "Banque Commerciale (SGBCI, Ecobank, Coris, UBA)",
        "Opérateur Mobile Money (Wave, Orange, MTN, M-Pesa)",
        "FinTech / Neobanque (Djamo, Kuda)",
        "Institution de Microfinance (Baobab, Advans)",
        "Régulateur / CENTIF",
    ],
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
    "⚙️ Paramètres": "Configuration",
}

for mod_name in modules.keys():
    if st.sidebar.button(mod_name, key=f"nav_{mod_name}"):
        st.session_state.active_module = mod_name

# -----------------------------------------------------------------------------
# AFFICHAGE DE LA PAGE ACTIVE
# -----------------------------------------------------------------------------
current_page = st.session_state.active_module
st.title(f"{current_page}")
st.caption(
    f"Plateforme unifiée — Zone : **{zone_reglementaire}** | Organisme :"
    f" **{institution_type}**"
)
st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 1. TABLEAU DE BORD
# -----------------------------------------------------------------------------
if current_page == "🏠 Tableau de bord":
    st.header("Vue d'ensemble de la Sécurité Financière & du Scoring")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Dossiers Analysés", "1,482", delta="+12%")
    col2.metric("Fraude Interceptée", "99.4%", delta="+0.8%")
    col3.metric("Volume PAPSS", "42.8 Mds FCFA", delta="+15.4%")
    col4.metric("Indice de Risque", "Faible (A+)", delta="Stable")

    st.markdown("---")
    c_g1, c_g2 = st.columns(2)
    with c_g1:
        st.subheader("📈 Évolution Mensuelle des Octrois (FCFA)")
        df_chart = pd.DataFrame(
            {
                "Mois": ["Nov", "Déc", "Jan", "Fév", "Mar", "Avr"],
                "Volume (Mds)": [12.5, 15.0, 18.2, 22.0, 29.5, 34.8],
            }
        )
        fig = px.line(
            df_chart,
            x="Mois",
            y="Volume (Mds)",
            markers=True,
            template="plotly_dark",
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True)

    with c_g2:
        st.subheader("📊 Répartition des Risques par Secteur")
        df_pie = pd.DataFrame(
            {
                "Secteur": ["Agro", "Commerce", "BTP", "Services", "Transport"],
                "Part": [35, 25, 15, 15, 10],
            }
        )
        fig_pie = px.pie(
            df_pie,
            names="Secteur",
            values="Part",
            hole=0.4,
            template="plotly_dark",
        )
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# -----------------------------------------------------------------------------
# 2. BANQUE & SCORING CRÉDIT (AVEC MODÈLE ML & JAUGE PLOTLY)
# -----------------------------------------------------------------------------
elif current_page == "💳 Banque & Scoring Crédit":
    st.header(
        "Analyse Solvabilité & Octroi Prudentiel (Bâle III / Modèle ML)"
    )

    col_cr1, col_cr2 = st.columns(2)
    with col_cr1:
        nom_client = st.text_input(
            "Nom de l'Emprunteur / Entreprise", value="Société Ivoire Agro SARL"
        )
        secteur = st.selectbox(
            "Secteur d'Activité",
            [
                "Agro-industrie",
                "Commerce Général",
                "BTP & Infrastructure",
                "Services",
            ],
        )
        chiffre_affaires = st.number_input(
            "Chiffre d'Affaires Mensuel (FCFA)",
            min_value=100000,
            value=6000000,
            step=100000,
        )
        engagements_encours = st.number_input(
            "Remboursements en cours / mois (FCFA)", min_value=0, value=400000
        )

    with col_cr2:
        pret_demande = st.number_input(
            "Montant du Prêt Demandé (FCFA)",
            min_value=100000,
            value=12000000,
            step=250000,
        )
        duree_mois = st.slider("Durée du remboursement (Mois)", 1, 60, 18)
        registre_impayes = st.radio(
            "Fichage Banque Centrale (CIP / BIC)",
            ["Aucun incident", "Incident actif / Interdit bancaire"],
        )

    mensualite = (pret_demande * 1.025) / duree_mois
    taux_endettement = (
        ((engagements_encours + mensualite) / chiffre_affaires) * 100
        if chiffre_affaires > 0
        else 100
    )

    # Simulation de probabilité de défaut (Modèle ML Logit / Scoring)
    prob_defaut = min(
        95.0,
        max(
            1.2,
            (taux_endettement * 0.8)
            + (15.0 if registre_impayes == "Incident actif / Interdit bancaire" else 0)
            - (2.0 * (chiffre_affaires / 10000000)),
        ),
    )

    st.markdown("---")
    st.subheader("📋 Résultat de l'Évaluation du Modèle Prédictif")

    m1, m2, m3 = st.columns(3)
    m1.metric("Mensualité Estimée", f"{mensualite:,.0f} FCFA / mois")
    m2.metric(
        "Taux d'Endettement",
        f"{taux_endettement:.1f} %",
        delta="Plafond 33%" if taux_endettement <= 33 else "Hors norme",
        delta_color="normal" if taux_endettement <= 33 else "inverse",
    )
    m3.metric(
        "Probabilité de Défaut (PD)",
        f"{prob_defaut:.1f}%",
        delta="Risque Élevé" if prob_defaut > 30 else "Risque Maîtrisé",
        delta_color="inverse" if prob_defaut > 30 else "normal",
    )

    # Jauge Plotly interactive
    fig_gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=prob_defaut,
            title={"text": "Indice de Probabilité de Défaut (%)"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#3b82f6"},
                "steps": [
                    {"range": [0, 20], "color": "rgba(16, 185, 129, 0.3)"},
                    {"range": [20, 45], "color": "rgba(245, 158, 11, 0.3)"},
                    {"range": [45, 100], "color": "rgba(239, 68, 68, 0.3)"},
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": 35,
                },
            },
        )
    )
    fig_gauge.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", font={"color": "white"}
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

    if st.button("💾 Valider et Enregistrer le Dossier de Crédit"):
        decision = (
            "REFUSÉ"
            if (
                registre_impayes == "Incident actif / Interdit bancaire"
                or taux_endettement > 33
                or prob_defaut > 35
            )
            else "APPROUVÉ"
        )
        dossier = {
            "id": f"CRED-{uuid.uuid4().hex[:6].upper()}",
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "client": nom_client,
            "montant": pret_demande,
            "decis": decision,
            "pd": f"{prob_defaut:.1f}%",
        }
        sauvegarder_historique(dossier)
        if decision == "APPROUVÉ":
            st.success(
                f"✅ Dossier {dossier['id']} enregistré et **APPROUVÉ** avec"
                f" succès !"
            )
        else:
            st.error(
                f"❌ Dossier {dossier['id']} enregistré mais **REFUSÉ** suite aux"
                " critères prudentiels."
            )

# -----------------------------------------------------------------------------
# 3. DÉTECTION DE FRAUDE & COMPTES MULES (AVEC RÉSEAU PLOTLY)
# -----------------------------------------------------------------------------
elif current_page == "🚨 Détection de Fraude":
    st.header(
        "Moteur d'Interception des Fraudes & Traçage des Comptes Mules"
    )

    c1, c2 = st.columns(2)
    with c1:
        utrn = st.text_input(
            "Référence UTRN", f"UTRN-{uuid.uuid4().hex[:10].upper()}"
        )
        compte_victime = st.text_input(
            "Compte Émetteur", placeholder="+225 07000000"
        )
        montant_fraud = st.number_input("Montant Contesté (FCFA)", value=3000000)
    with c2:
        plateforme = st.selectbox(
            "Opérateur", ["Wave", "Orange Money", "MTN MoMo", "M-Pesa"]
        )
        typologie = st.selectbox(
            "Type d'Incident",
            ["Phishing / Escroquerie", "Compte Mule", "SIM Swap"],
        )

    st.subheader("🕸️ Visualisation Graphique du Réseau de Transfert")
    # Simulation d'un graphe de réseau avec Plotly
    edge_x = [0, 1, 2, 3]
    edge_y = [0, 1, 0, -1]
    node_x = [0, 1, 2, 3]
    node_y = [0, 1, 0, -1]

    fig_net = go.Figure(
        data=[
            go.Scatter(
                x=[0, 1, 1, 2],
                y=[0, 1, -1, 0],
                mode="lines",
                line=dict(width=2, color="#ef4444"),
                hoverinfo="none",
            ),
            go.Scatter(
                x=[0, 1, 1, 2],
                y=[0, 1, -1, 0],
                mode="markers+text",
                text=[
                    "Victime",
                    "Mule 1 (Bloqué)",
                    "Mule 2 (Bloqué)",
                    "Encaisseur Final",
                ],
                textposition="top center",
                marker=dict(
                    showscale=False,
                    color=["#3b82f6", "#ef4444", "#ef4444", "#f59e0b"],
                    size=20,
                ),
            ),
        ]
    )
    fig_net.update_layout(
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    )
    st.plotly_chart(fig_net, use_container_width=True)

    if st.button("🚨 DÉCLENCHER LE GEL IMMÉDIAT DE LA CHAÎNE"):
        st.error(
            f"🛑 Ordre de gel systémique émis pour l'UTRN : {utrn}. Comptes"
            " complices séquestrés."
        )

# -----------------------------------------------------------------------------
# 4. MOBILE MONEY & NÉOBANQUES
# -----------------------------------------------------------------------------
elif current_page == "📱 Mobile Money & Néobanques":
    st.header(
        "Alternative Credit Scoring pour le Secteur Informel & Neobanques"
    )
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        flux = st.number_input(
            "Encaissements 3 derniers mois (FCFA)", value=4000000
        )
        anciennete = st.slider("Ancienneté du compte (Mois)", 1, 36, 12)
    with c_m2:
        solde_nuit = st.number_input(
            "Solde moyen de nuit (FCFA)", value=300000
        )
        retrait_cash = st.slider(
            "Taux de retrait cash immédiat (%)", 0, 100, 30
        )

    score = 500 + (anciennete * 10) + (solde_nuit / 2000) - (retrait_cash * 2)
    st.metric("Score FinTech Alternatif", f"{int(score)} / 950 points")
    if score >= 700:
        st.success(
            "🌟 **Éligible :** Prêt instantané accordé sans garantie physique."
        )
    else:
        st.warning("⚠️ **Vérification requise :** Historique insuffisant.")

# -----------------------------------------------------------------------------
# 5. RISQUE AGRICOLE
# -----------------------------------------------------------------------------
elif current_page == "🌱 Risque Agricole":
    st.header("Modélisation Agricole Panafricaine & Campagnes Cacao / Café")
    surf = st.number_input("Surface exploitée (Hectares)", value=10.0)
    rend = st.number_input("Rendement moyen (Kg/Ha)", value=800)
    prix = st.number_input("Prix d'achat bord champ (FCFA/Kg)", value=1800)
    rev = surf * rend * prix
    st.metric("Revenu Brut Estimé de la Campagne", f"{rev:,.0f} FCFA")
    st.info(
        "📅 Échéancier aligné : 85% prélevés en Grande Campagne (Oct-Mars),"
        " 15% en Petite Campagne."
    )

# -----------------------------------------------------------------------------
# 6. PAIEMENTS TRANSFRONTALIERS
# -----------------------------------------------------------------------------
elif current_page == "🌍 Paiements Transfrontaliers":
    st.header(
        "Plateforme Interbancaire de Paiement Transfrontalier (PAPSS)"
    )
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        montant_xof = st.number_input("Montant en XOF (FCFA)", value=10000000)
    with col_p2:
        devise_cible = st.selectbox("Devise Cible", ["NGN (Nigéria)", "KES (Kenya)", "GHS (Ghana)"])
    if st.button("💱 Exécuter la Compensation Instantanée"):
        st.success(
            "✅ Transaction réglée en moins de 120 secondes via le réseau"
            " PAPSS / Afreximbank sans conversion USD."
        )

# -----------------------------------------------------------------------------
# 7. STRESS-TESTS PRUDENTIELS
# -----------------------------------------------------------------------------
elif current_page == "📈 Stress-Tests Prudentiels":
    st.header("Module Prudentiel d'Analyse des Chocs (Bâle III / IFRS 9)")
    choc = st.slider("Choc de baisse du Chiffre d'Affaires (%)", 0, 70, 40)
    stage = (
        "Stage 1 (Normal)"
        if choc < 25
        else ("Stage 2 (Dégradation)" if choc < 50 else "Stage 3 (Défaut / NPL)")
    )
    st.metric("Classification IFRS 9", stage)

# -----------------------------------------------------------------------------
# 8. SOURCES DE DONNÉES
# -----------------------------------------------------------------------------
elif current_page == "📂 Sources de Données":
    st.header("Data Center & Registre des Sources")
    df_src = pd.DataFrame(
        {
            "Source": ["BCEAO / BEAC", "BIC (Bureau Crédit)", "PAPSS"],
            "Type": ["Réglementaire", "Historique", "Transfrontalier"],
            "Statut": ["Connecté", "Actif", "Sécurisé"],
        }
    )
    st.table(df_src)

# -----------------------------------------------------------------------------
# 9. RAPPORTS & HISTORIQUE (AVEC PERSISTANCE & EXPORT)
# -----------------------------------------------------------------------------
elif current_page == "📜 Rapports & Historique":
    st.header("Registre d'Audit & Historique des Dossiers")
    historique = charger_historique()
    if historique:
        df_hist = pd.DataFrame(historique)
        st.dataframe(df_hist, use_container_width=True)
    else:
        st.info(
            "Aucun dossier enregistré pour le moment. Effectuez une simulation"
            " dans l'onglet 'Banque & Scoring Crédit'."
        )

    if st.button("📄 Générer le Rapport XML ISO 20022 (camt.056)"):
        st.json(
            {
                "Document": {
                    "MsgId": f"CENTIF-{uuid.uuid4().hex[:8].upper()}",
                    "Status": "Transmis avec succès au régulateur",
                }
            }
        )

# -----------------------------------------------------------------------------
# 10. PARAMÈTRES
# -----------------------------------------------------------------------------
elif current_page == "⚙️ Paramètres":
    st.header("Paramètres de la Plateforme")
    st.text_input("Administrateur", value="Kouassi Kouame Daniel")
    st.text_input("Institut", value="Apex Institute of Management / MBA Data Science")
    st.success("Configuration mise à jour.")
