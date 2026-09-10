import streamlit as st
import joblib
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Fintech Scoring & Anti-Fraude UEMOA",
    page_icon="🏦",
    layout="wide"
)

@st.cache_resource
def load_models():
    m_credit = joblib.load('modele_scoring_uemoa.pkl')
    m_fraude = joblib.load('modele_fraude_uemoa.pkl')
    return m_credit, m_fraude

model_credit, model_fraude = load_models()

st.title("🏦 Plateforme de Décision Prudentielle & Lutte Anti-Fraude (BCEAO)")
st.markdown("Système de Scoring Crédit Alternative Data & Monitoring des Risques Monétiques")
st.markdown("---")

tab1, tab2 = st.tabs(["📊 Évaluation Crédit & Décision", "🛡️ Contrôle Anti-Fraude & AML"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 Informations Emprunteur")
        secteur = st.selectbox("Secteur d'activité :", ['Planteur_Cacao', 'Commercant_Informel', 'Salarie_Prive', 'Fonctionnaire', 'Artisan'])
        revenu = st.number_input("Revenu mensuel estimé (FCFA) :", min_value=30000, value=300000, step=25000)
        cooperative = st.radio("Affiliation Coopérative / Tontine :", options=[1, 0], format_func=lambda x: "Oui" if x==1 else "Non")
        taux_endettement = st.slider("Taux d'endettement actuel (%) :", 0, 100, 25) / 100.0

    with col2:
        st.subheader("📱 Comportement Financier")
        flux_mm = st.number_input("Flux Mobile Money mensuel (FCFA) :", min_value=0, value=250000, step=25000)
        epargne_mm = st.number_input("Solde épargne Mobile Money (FCFA) :", min_value=0, value=50000, step=10000)
        retards = st.slider("Incidents de paiement (6 derniers mois) :", 0, 10, 0)

with tab2:
    st.subheader("⚠️ Moteur de Détection de Fraude (Mobile Money)")
    col_f1, col_f2 = st.columns(2)
    
    with col_f1:
        depots_24h = st.number_input("Nombre de petits dépôts reçus en <24h (Structuring) :", min_value=0, value=1)
        sim_swap = st.radio("Changement de carte SIM récent (< 72h) :", options=[1, 0], format_func=lambda x: "Oui" if x==1 else "Non")
    
    with col_f2:
        ratio_retrait = st.slider("Ratio de retrait immédiat des fonds reçus (%) :", 0, 100, 20) / 100.0

st.markdown("---")

if st.button("🚀 Analyser le Dossier Complet", use_container_width=True):
    # Dataframes pour prédictions
    df_c = pd.DataFrame([{
        'secteur_activite': secteur,
        'revenu_mensuel_estime_fcfa': revenu,
        'volume_flux_mobile_money_fcfa': flux_mm,
        'solde_epargne_mobile_fcfa': epargne_mm,
        'retards_paiement_6mois': retards,
        'taux_endettement': taux_endettement,
        'membre_cooperative_tontine': cooperative
    }])
    
    df_f = pd.DataFrame([{
        'volume_flux_mobile_money_fcfa': flux_mm,
        'solde_epargne_mobile_fcfa': epargne_mm,
        'nb_depots_suspects_24h': depots_24h,
        'ratio_retrait_immediat': ratio_retrait,
        'changement_sim_recent': sim_swap
    }])
    
    # CALCULS
    proba_defaut = model_credit.predict_proba(df_c)[0][1]
    proba_fraude = model_fraude.predict_proba(df_f)[0][1]
    score_fintech = int((1 - proba_defaut) * 850)
    
    # AFFICHAGE RÉSULTATS
    st.subheader("📋 Synthèse de la Décision d'Octroi")
    c1, c2, c3 = st.columns(3)
    
    c1.metric("Score FinTech", f"{score_fintech} / 850")
    c2.metric("Probabilité de Défaut (PD)", f"{proba_defaut * 100:.1f} %")
    c3.metric("Indice de Risque de Fraude", f"{proba_fraude * 100:.1f} %")
    
    # LOGIQUE PRUDENTIELLE COMBINÉE
    if proba_fraude > 0.60:
        st.error("🚨 **BLOCAGE SÉCURITÉ : ALERTE FRAUDE AMF/BCEAO.** Activité suspecte détectée sur le compte Mobile Money (SIM Swap / Structuring). Dossier transmis à la conformité.")
    elif proba_defaut < 0.25:
        st.success(f"✅ **CRÉDIT ACCORDÉ.** Risque très faible. Montant maximum recommandé : {int(revenu * 4)} FCFA à un taux préférentiel de 8.5%.")
    elif proba_defaut < 0.50:
        st.warning(f"⚠️ **PASSAGE EN COMITÉ DE CRÉDIT.** Risque modéré. Aval de la coopérative ou cautionnement solidaire requis.")
    else:
        st.error("❌ **CRÉDIT REFUSÉ.** Capacité de remboursement insuffisante ou historique de retard trop élevé.")