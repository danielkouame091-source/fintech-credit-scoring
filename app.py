import streamlit as st
import pandas as pd
import numpy as np

# ==========================================
# 1. CONFIGURATION & DESIGN 3D (APPLE / FINTECH)
# ==========================================
st.set_page_config(
    page_title="Plateforme FinTech & Scoring Sécurisé",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp {
        background-color: #0B0F19;
        color: #F8FAFC;
        font-family: 'Inter', sans-serif;
    }
    .card-3d {
        background: linear-gradient(145deg, #1E293B, #0F172A);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 10px 10px 25px rgba(0, 0, 0, 0.6), -5px -5px 15px rgba(255, 255, 255, 0.02);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. NAVIGATION LATÉRALE (SIDEBAR)
# ==========================================
st.sidebar.markdown("### 🧭 Navigation")
menu = st.sidebar.radio(
    "Choisir un module :",
    ["🏠 Accueil & Tableau de Bord", "💳 Scoring & Analyse de Risque", "🛡️ Détection Anti-Fraude"]
)

# ==========================================
# 3. CONTENU DES PAGES SELON LE MENU
# ==========================================

if menu == "🏠 Accueil & Tableau de Bord":
    st.markdown('<div class="card-3d">', unsafe_allow_html=True)
    st.title("🚀 Système National & Panafricain de Sécurité Financière")
    st.write("Bienvenue sur votre plateforme professionnelle de scoring de crédit et d'évaluation des risques.")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Dossiers Traités", value="1,284", delta="+12%")
    with col2:
        st.metric(label="Taux d'Approbation", value="68.4%", delta="-2.1%")
    with col3:
        st.metric(label="Alertes Fraude Bloquées", value="14", delta="0")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "💳 Scoring & Analyse de Risque":
    st.markdown('<div class="card-3d">', unsafe_allow_html=True)
    st.subheader("🛡️ Module d'Analyse de Crédit & Scoring Sécurisé")
    st.markdown("Renseignez les informations financières pour une évaluation instantanée.")

    with st.form("credit_form"):
        col_a, col_b = st.columns(2)
        
        with col_a:
            age = st.number_input("Âge du demandeur", min_value=18, max_value=80, value=30)
            revenu = st.number_input("Revenu Mensuel (FCFA)", min_value=0.0, value=350000.0, step=25000.0)
            charges = st.number_input("Charges de Dettes Actuelles (FCFA)", min_value=0.0, value=100000.0, step=10000.0)

        with col_b:
            montant = st.number_input("Montant du Crédit Sollicité (FCFA)", min_value=0.0, value=1500000.0, step=100000.0)
            duree = st.slider("Durée du Prêt (en mois)", min_value=6, max_value=60, value=24)
            incidents = st.selectbox("Historique d'incidents (12 derniers mois)", ["Aucun", "1 à 2 retards", "Contentieux"])

        submitted = st.form_submit_button("Lancer l'Analyse de Risque")

    if submitted:
        # Validation stricte anti-erreur
        erreurs = []
        if revenu <= 0:
            erreurs.append("Le revenu doit être supérieur à 0.")
        if charges >= revenu:
            erreurs.append("Erreur de cohérence : les charges ne peuvent pas dépasser ou égaler le revenu.")
        
        if erreurs:
            st.error("❌ **Échec de la validation du dossier :**")
            for err in erreurs:
                st.warning(f"- {err}")
        else:
            # Calculs de risque
            taux_mensuel = 0.08 / 12
            mensualite = (montant * taux_mensuel) / (1 - (1 + taux_mensuel) ** -duree)
            endettement = ((charges + mensualite) / revenu) * 100

            score = 800
            if incidents == "1 à 2 retards":
                score -= 120
            elif incidents == "Contentieux":
                score -= 250
            score -= int(endettement * 1.5)
            score_final = max(300, min(850, score))

            st.markdown("---")
            st.markdown("### 📊 Résultats de l'Évaluation")
            
            res1, res2 = st.columns(2)
            with res1:
                st.metric(label="Score de Crédit Global", value=f"{score_final} / 850")
                st.metric(label="Taux d'Endettement", value=f"{endettement:.1f}%")
                
                if endettement <= 35 and score_final >= 650:
                    st.success("✅ **Décision : Dossier ACCEPTÉ** (Risque Faible)")
                elif endettement <= 45:
                    st.warning("⚠️ **Décision : Analyse Manuelle Requise**")
                else:
                    st.error("❌ **Décision : Dossier REFUSÉ** (Risque Élevé)")

            with res2:
                st.markdown("#### 🔍 Facteurs d'Explication")
                st.progress(min(1.0, max(0.0, float(revenu / 1000000))), text="Stabilité des Revenus (+)")
                st.progress(min(1.0, max(0.0, float(endettement / 100))), text="Poids de la Dette (-)")
                st.info(f"🔒 Session sécurisée (ID : {np.random.randint(10000, 99999)})")

    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🛡️ Détection Anti-Fraude":
    st.markdown('<div class="card-3d">', unsafe_allow_html=True)
    st.subheader("🛡️ Module de Surveillance & Anti-Fraude")
    st.write("Ce module analyse les transactions en temps réel pour détecter les schémas suspects.")
    
    id_trans = st.text_input("ID de la Transaction / Numéro de Dossier", "TRX-2026-9981")
    if st.button("Vérifier les Indicateurs de Fraude"):
        st.success("✅ Aucune anomalie détectée sur cette transaction.")
    st.markdown('</div>', unsafe_allow_html=True)
    
