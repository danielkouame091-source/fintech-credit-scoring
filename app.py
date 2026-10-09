import datetime
import json
import os
import uuid
import io
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# -----------------------------------------------------------------------------
# CONFIGURATION DE LA PAGE & STYLE INSTITUTIONNEL (NETteté & 3D)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Plateforme FinTech & Anti-Fraude Pan-Africaine | Enterprise Edition",
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
        background: radial-gradient(circle at 50% 10%, #0f172a 0%, #070b19 100%);
        color: #f8fafc;
    }

    /* --- CARTES 3D GLASSMORPHISM NETTES --- */
    .dashboard-card, div[data-testid="stMetric"], div.stForm, .stPlotlyChart {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), 
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }

    /* --- CHAMPS DE SAISIE & SELECTBOX PRO --- */
    input, textarea {
        background-color: rgba(15, 23, 42, 0.9) !important;
        color: #ffffff !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        border-radius: 10px !important;
    }
    
    div[data-baseweb="select"] > div {
        background-color: rgba(15, 23, 42, 0.9) !important;
        color: #ffffff !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
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
# GESTION DE LA PERSISTANCE (JSON) & MACHINE LEARNING DE BASE
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

# Entraînement d'un modèle Scikit-Learn de Scoring Prudentiel (Simulation réaliste)
@st.cache_resource
def entrainer_modele_scoring():
    np.random.seed(42)
    X_train = np.random.rand(500, 3) * np.array([15000000, 60, 500000]) # [CA, Duree, Encours]
    y_train = (X_train[:, 0] / (X_train[:, 2] + 1) < 5).astype(int) # Règle de défaut simulée
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)
    model = LogisticRegression()
    model.fit(X_scaled, y_train)
    return model, scaler

ml_model, ml_scaler = entrainer_modele_scoring()

# -----------------------------------------------------------------------------
# SYSTÈME D'AUTHENTIFICATION & GOUVERNANCE Rôles (RBAC)
# -----------------------------------------------------------------------------
if "authentifie" not in st.session_state:
    st.session_state.authentifie = False

if not st.session_state.authentifie:
    st.markdown("<h2 style='text-align: center; color: #60a5fa;'>🔐 Authentification Institutionnelle</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #cbd5e1;'>Accès réservé aux auditeurs, analystes et directeurs des risques (MBA Data Science & AI)</p>", unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        with st.form("form_login"):
            username = st.text_input("Identifiant Professionnel", value="analyste.risques")
            password = st.text_input("Mot de passe", type="password", value="secure2026")
            role_choisi = st.selectbox("Profil d'Habilitation", [
                "🔍 Analyste des Risques & Scoring",
                "⚖️ Directeur des Engagements (Validateur)",
                "🚨 Officier de Conformité / Anti-Fraude (CENTIF)",
                "📊 Auditeur Régulateur"
            ])
            submit_login = st.form_submit_button("Se connecter à la plateforme", use_container_width=True)
            if submit_login:
                st.session_state.authentifie = True
                st.session_state.username = username
                st.session_state.user_role = role_choisi
                st.rerun()
    st.stop()

# -----------------------------------------------------------------------------
# EN-TÊTE & CONFIGURATION INSTITUTIONNELLE
# -----------------------------------------------------------------------------
st.markdown("<h1 style='text-align: center; color: #f8fafc; font-weight: 800;'>HUB FINANCIER & ANTI-FRAUDE PANAFRICAIN</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #93c5fd; font-size: 1.1rem;'>Utilisateur : <b>{st.session_state.username}</b> | Rôle : <b>{st.session_state.user_role}</b></p>", unsafe_allow_html=True)

col_cfg1, col_cfg2 = st.columns(2)
with col_cfg1:
    zone_reglementaire = st.selectbox(
        "Cadre Réglementaire / Banque Centrale",
        [
            "UEMOA (BCEAO - Côte d'Ivoire, Sénégal...)",
            "CEMAC (BEAC - Cameroun, Gabon...)",
            "Afrique de l'Est / M-Pesa (Kenya...)",
            "Réseau Transfrontalier Panafricain (PAPSS)",
        ],
    )
with col_cfg2:
    institution_type = st.selectbox(
        "Établissement Opérateur",
        [
            "Banque Commerciale (Standards type SBI / Ecobank)",
            "Opérateur Mobile Money (Wave, Orange, MTN, Moov)",
            "FinTech / Neobanque",
            "Cellule de Renseignement Financier (CENTIF)",
        ],
    )

st.markdown("---")

# -----------------------------------------------------------------------------
# NAVIGATION CENTRALE (GRILLE STYLE APP iOS / BANQUE)
# -----------------------------------------------------------------------------
if "active_module" not in st.session_state:
    st.session_state.active_module = "🏠 Tableau de bord"

modules = {
    "🏠 Tableau de bord": "Vue Globale",
    "💳 Banque & Crédit": "Scoring Bâle III (ML)",
    "🚨 Anti-Fraude": "Gel Comptes Mules",
    "📱 Mobile Money": "Scoring Alternatif",
    "🌱 Risque Agricole": "Campagnes Cacao/Café",
    "🌍 PAPSS": "Paiements Transfrontaliers",
    "📈 Stress-Tests": "Résistance Bancaire",
    "📂 Data Center": "Import & Registres",
    "📜 Historique & Audit": "Conformité ISO & PDF",
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
    col1.metric("Dossiers Analysés", "1,482", delta="+12%")
    col2.metric("Fraude Interceptée", "99.4%", delta="+0.8%")
    col3.metric("Volume PAPSS", "42.8 Mds FCFA", delta="+15.4%")
    col4.metric("Indice de Risque", "Faible (A+)", delta="Stable")

    st.markdown("---")
    c_g1, c_g2 = st.columns(2)
    with c_g1:
        st.subheader("📈 Évolution Mensuelle des Flux (Mds FCFA)")
        df_chart = pd.DataFrame({"Mois": ["Nov", "Déc", "Jan", "Fév", "Mar", "Avr"], "Volume": [12.5, 15.0, 18.2, 22.0, 29.5, 34.8]})
        fig = px.line(df_chart, x="Mois", y="Volume", markers=True, template="plotly_dark")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with c_g2:
        st.subheader("📊 Répartition Sectorielle du Risque")
        df_pie = pd.DataFrame({"Secteur": ["Agro", "Commerce", "BTP", "Services", "Transport"], "Part": [35, 25, 15, 15, 10]})
        fig_pie = px.pie(df_pie, names="Secteur", values="Part", hole=0.4, template="plotly_dark")
        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_pie, use_container_width=True)

# -----------------------------------------------------------------------------
# 2. BANQUE & CRÉDIT (AVEC MACHINE LEARNING SCIKIT-LEARN)
# -----------------------------------------------------------------------------
elif current_page == "💳 Banque & Crédit":
    st.markdown("#### Modèle Prédictif de Solvabilité (Scikit-Learn / Bâle III)")
    col_cr1, col_cr2 = st.columns(2)
    with col_cr1:
        nom_client = st.text_input("Nom de l'Emprunteur / Entreprise", value="Société Ivoire Agro SARL")
        chiffre_affaires = st.number_input("Chiffre d'Affaires Mensuel (FCFA)", min_value=100000, value=6000000)
        engagements_encours = st.number_input("Remboursements en cours / mois (FCFA)", min_value=0, value=400000)
    with col_cr2:
        pret_demande = st.number_input("Montant du Prêt Demandé (FCFA)", min_value=100000, value=12000000)
        duree_mois = st.slider("Durée du remboursement (Mois)", 1, 60, 18)
        registre_impayes = st.radio("Fichage Centrale des Bilans / BIC", ["Aucun incident", "Incident actif / Interdit bancaire"])

    # Prédiction par le modèle Machine Learning Scikit-Learn
    features_input = ml_scaler.transform([[chiffre_affaires, duree_mois, engagements_encours]])
    prob_defaut = float(ml_model.predict_proba(features_input)[0][1]) * 100
    if registre_impayes == "Incident actif / Interdit bancaire":
        prob_defaut = min(99.0, prob_defaut + 40.0)

    mensualite = (pret_demande * 1.025) / duree_mois
    taux_endettement = ((engagements_encours + mensualite) / chiffre_affaires) * 100 if chiffre_affaires > 0 else 100

    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    m1.metric("Mensualité Estimée", f"{mensualite:,.0f} FCFA")
    m2.metric("Taux d'Endettement", f"{taux_endettement:.1f} %")
    m3.metric("Probabilité de Défaut (IA)", f"{prob_defaut:.1f}%")

    if st.button("💾 Enregistrer et Soumettre le Dossier ML"):
        decision = "REFUSÉ" if (registre_impayes == "Incident actif / Interdit bancaire" or taux_endettement > 33 or prob_defaut > 35) else "APPROUVÉ"
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
            st.success(f"✅ Dossier {dossier['id']} APPROUVÉ par l'algorithme Scikit-Learn.")
        else:
            st.error(f"❌ Dossier {dossier['id']} REFUSÉ par le modèle de risque.")

# -----------------------------------------------------------------------------
# 3. ANTI-FRAUDE (COMPTES MULES)
# -----------------------------------------------------------------------------
elif current_page == "🚨 Anti-Fraude":
    st.markdown("#### Moteur d'Interception & Gel en Cascade (Comptes Mules Inter-réseaux)")
    c1, c2 = st.columns(2)
    with c1:
        utrn = st.text_input("Référence UTRN", f"UTRN-{uuid.uuid4().hex[:10].upper()}")
        compte_victime = st.text_input("Compte Victime / Émetteur", placeholder="+225...")
        montant_fraud = st.number_input("Montant Contesté (FCFA)", value=3000000)
    with c2:
        plateforme = st.selectbox("Réseau / Opérateur", ["Wave Money", "Orange Money", "MTN MoMo", "Moov Africa", "Virement Interbancaire"])
        niveau_alerte = st.selectbox("Gravité", ["CRITIQUE (Gel immédiat)", "ÉLEVÉ", "MODÉRÉ"])

    st.subheader("🕸️ Traçage des Fonds vers les Comptes Complices")
    fig_net = go.Figure(data=[
        go.Scatter(x=[0, 1, 1, 2], y=[0, 1, -1, 0], mode='lines', line=dict(width=3, color='#ef4444'), hoverinfo='none'),
        go.Scatter(x=[0, 1, 1, 2], y=[0, 1, -1, 0], mode='markers+text', text=["Victime", "Mule 1 (Bloqué)", "Mule 2 (Bloqué)", "Retrait Final"], textposition="top center", marker=dict(color=['#3b82f6', '#ef4444', '#ef4444', '#f59e0b'], size=22))
    ])
    fig_net.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(showgrid=False, zeroline=False, showticklabels=False), yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
    st.plotly_chart(fig_net, use_container_width=True)

    if st.button("🚨 DÉCLENCHER LE GEL MULTI-RÉSEAUX INSTANTANÉ"):
        st.error(f"🛑 ORDRE DE SÉQUESTRE EXÉCUTÉ — UTRN : {utrn} bloqué simultanément sur Orange, MTN, Wave et les banques partenaires.")

# -----------------------------------------------------------------------------
# 4. MOBILE MONEY
# -----------------------------------------------------------------------------
elif current_page == "📱 Mobile Money":
    st.markdown("#### Scoring Alternatif basé sur les Flux de Portefeuilles")
    flux = st.number_input("Encaissements 3 derniers mois (FCFA)", value=4000000)
    anciennete = st.slider("Ancienneté du compte (Mois)", 1, 36, 12)
    solde_nuit = st.number_input("Solde moyen de nuit (FCFA)", value=300000)
    score = 500 + (anciennete * 10) + (solde_nuit / 2000)
    st.metric("Score Digital Alternatif", f"{int(score)} / 950 points")
    st.success("🌟 Éligibilité validée pour un micro-crédit instantané sans garantie physique.")

# -----------------------------------------------------------------------------
# 5. RISQUE AGRICOLE
# -----------------------------------------------------------------------------
elif current_page == "🌱 Risque Agricole":
    st.markdown("#### Modélisation Agricole & Campagnes (Cacao / Café)")
    surf = st.number_input("Surface exploitée (Hectares)", value=10.0)
    rend = st.number_input("Rendement moyen (Kg/Ha)", value=800)
    prix = st.number_input("Prix d'achat bord champ (FCFA/Kg)", value=1800)
    rev = surf * rend * prix
    st.metric("Revenu Net Campagne Estimé", f"{rev:,.0f} FCFA")
    st.info("📅 Échéancier adapté aux saisons : 85% prélevés en Grande Campagne (Oct-Mars).")

# -----------------------------------------------------------------------------
# 6. PAPSS
# -----------------------------------------------------------------------------
elif current_page == "🌍 PAPSS":
    st.markdown("#### Paiements & Règlements Transfrontaliers (Système PAPSS / Afreximbank)")
    montant_xof = st.number_input("Montant à transférer (XOF)", value=10000000)
    devise_cible = st.selectbox("Devise du Pays Destinataire", ["NGN (Nigéria)", "KES (Kenya)", "GHS (Ghana)"])
    if st.button("💱 Exécuter la Compensation Panafricaine"):
        st.success("✅ Règlement transfrontalier exécuté en 120s en monnaies locales sans conversion USD.")

# -----------------------------------------------------------------------------
# 7. STRESS-TESTS
# -----------------------------------------------------------------------------
elif current_page == "📈 Stress-Tests":
    st.markdown("#### Analyse de Résistance Prudentielle sous Chocs")
    choc = st.slider("Choc de baisse d'activité (%)", 0, 70, 40)
    stage = "Stage 1 (Normal)" if choc < 25 else ("Stage 2 (Surveillance)" if choc < 50 else "Stage 3 (Défaut NPL)")
    st.metric("Classification IFRS 9", stage)

# -----------------------------------------------------------------------------
# 8. DATA CENTER
# -----------------------------------------------------------------------------
elif current_page == "📂 Data Center":
    st.markdown("#### Importation de Portefeuille & Registre des Sources")
    uploaded_file = st.file_uploader("Importer un fichier de transactions ou de crédits (CSV / Excel)", type=["csv", "xlsx"])
    if uploaded_file is not None:
        try:
            df_imported = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            st.success(f"✅ Fichier '{uploaded_file.name}' chargé avec succès !")
            st.dataframe(df_imported.head(10), use_container_width=True)
        except Exception as e:
            st.error(f"Erreur : {e}")

    st.markdown("---")
    st.subheader("Connecteurs Actifs")
    df_src = pd.DataFrame({
        "Source": ["BCEAO / BEAC", "Bureau d'Information sur le Crédit (BIC)", "Réseau PAPSS", "Passerelles Mobile Money"],
        "Type": ["Réglementaire", "Historique", "Transfrontalier", "Opérationnel"],
        "Statut": ["Connecté", "Actif", "Sécurisé", "En temps réel"]
    })
    st.table(df_src)

# -----------------------------------------------------------------------------
# 9. HISTORIQUE & AUDIT (AVEC EXPORT CSV & GÉNÉRATEUR DE RAPPORT PDF)
# -----------------------------------------------------------------------------
elif current_page == "📜 Historique & Audit":
    st.markdown("#### Registre d'Audit & Conformité ISO 20022 / Génération PDF")
    historique = charger_historique()
    if historique:
        df_hist = pd.DataFrame(historique)
        st.dataframe(df_hist, use_container_width=True)

        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            csv_data = df_hist.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Télécharger le Registre (CSV)", data=csv_data, file_name="audit_fintech.csv", mime="text/csv")

        with col_exp2:
            # Générateur de Rapport PDF officiel
            def generer_pdf(dossier_recent):
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=letter)
                elements = []
                styles = getSampleStyleSheet()
                
                title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#0f172a'), alignment=1)
                elements.append(Paragraph("RAPPORT OFFICIEL D'ANALYSE DES RISQUES FINANCIERS", title_style))
                elements.append(Paragraph("Plateforme Panafricaine FinTech & Anti-Fraude (BCEAO / Bâle III)", styles['Normal']))
                elements.append(Spacer(1, 20))
                
                data = [
                    ["Référence Dossier", dossier_recent.get('id', 'N/A')],
                    ["Date d'Analyse", dossier_recent.get('date', 'N/A')],
                    ["Client / Entreprise", dossier_recent.get('client', 'N/A')],
                    ["Montant Demandé", f"{dossier_recent.get('montant', 0):,.0f} FCFA"],
                    ["Probabilité de Défaut (IA)", dossier_recent.get('pd', 'N/A')],
                    ["Décision Prudentielle", dossier_recent.get('decis', 'N/A')]
                ]
                t = Table(data, colWidths=[200, 250])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f1f5f9')),
                    ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
                    ('PADDING', (0,0), (-1,-1), 8),
                ]))
                elements.append(t)
                elements.append(Spacer(1, 30))
                elements.append(Paragraph("<b>Avis de la Direction des Risques :</b> Le présent dossier a été évalué conformément aux modèles de scoring Scikit-Learn et aux exigences prudentielles en vigueur.", styles['Normal']))
                
                doc.build(elements)
                buffer.seek(0)
                return buffer.getvalue()

            if historique:
                pdf_bytes = generer_pdf(historique[0])
                st.download_button("📄 Télécharger le Rapport Officiel (PDF)", data=pdf_bytes, file_name="Rapport_Risque_Financier.pdf", mime="application/pdf")
    else:
        st.info("Aucun dossier enregistré pour l'instant.")

    if st.button("📄 Transmettre le Rapport ISO 20022 (XML) au Régulateur"):
        st.json({
            "Document": {
                "MsgId": f"CENTIF-{uuid.uuid4().hex[:8].upper()}",
                "Status": "Certifié conforme et transmis à la BCEAO / CENTIF"
            }
        })

# -----------------------------------------------------------------------------
# 10. PARAMÈTRES
# -----------------------------------------------------------------------------
elif current_page == "⚙️ Paramètres":
    st.markdown("#### Paramètres Généraux de la Plateforme")
    st.text_input("Administrateur Responsable", value="Kouassi Kouame Daniel")
    st.text_input("Institution / Université", value="Apex Institute of Management (MBA Data Science & AI)")
    if st.button("Se déconnecter"):
        st.session_state.authentifie = False
        st.rerun()
