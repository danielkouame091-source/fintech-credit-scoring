import base64
import os
import sqlite3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime
from urllib.parse import quote
import pandas as pd
import requests
import streamlit as st

# =========================================================
# CONFIGURATION & STYLING 3D / GLASSMORPHISM
# =========================================================
st.set_page_config(
    page_title="Kelanewin Transit - SYDAM Pro Enterprise",
    page_icon="🇨🇮",
    layout="wide",
)

st.markdown(
    """
<style>
.stApp {
    background-color: #0B0F19;
    color: #F8FAFC;
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
}
.header-banner {
    background: linear-gradient(135deg, #047857 0%, #10B981 50%, #0284C7 100%);
    padding: 30px;
    border-radius: 20px;
    color: white;
    margin-bottom: 25px;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.15);
}
.custom-card-3d {
    background: #1E293B;
    border-radius: 18px;
    padding: 25px;
    border: 1px solid #334155;
    margin-bottom: 25px;
    box-shadow: 8px 8px 16px #070a11, -8px -8px 16px #151a27;
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# GESTION BASE DE DONNÉES SQLITE
# =========================================================
DB_NAME = "transit_enterprise.db"
UPLOAD_DIR = "uploads_dossiers"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT UNIQUE,
        sh TEXT,
        dd REAL,
        categorie TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dossiers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        client TEXT,
        email_client TEXT,
        tel_client TEXT,
        article TEXT,
        fob_xof REAL,
        total_facture REAL,
        solde_du REAL,
        statut TEXT,
        document_path TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

def get_dossiers_db():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM dossiers ORDER BY id DESC", conn)
    conn.close()
    return df

# =========================================================
# FONCTION D'ENVOI E-MAIL SMTP RÉEL & SÉCURISÉ
# =========================================================
def envoyer_email_smtp(destinataire, objet, corps, pdf_path=None):
    # Récupération sécurisée depuis os.environ ou st.secrets (Streamlit Cloud)
    smtp_server = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    sender_email = os.environ.get("SMTP_SENDER_EMAIL", "")
    smtp_password = os.environ.get("SMTP_SENDER_PASSWORD", "")

    # Fallback sur st.secrets si disponible
    if not sender_email and "SMTP_SENDER_EMAIL" in st.secrets:
        sender_email = st.secrets["SMTP_SENDER_EMAIL"]
    if not smtp_password and "SMTP_SENDER_PASSWORD" in st.secrets:
        smtp_password = st.secrets["SMTP_SENDER_PASSWORD"]

    if not sender_email or not smtp_password:
        return False, "Configuration requise : Les variables SMTP_SENDER_EMAIL et SMTP_SENDER_PASSWORD ne sont pas configurées sur le serveur."

    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = destinataire
        msg['Subject'] = objet
        msg.attach(MIMEText(corps, 'plain', 'utf-8'))

        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                p = MIMEApplication(f.read(), Name=os.path.basename(pdf_path))
            p.add_header('Content-Disposition', 'attachment', filename=os.path.basename(pdf_path))
            msg.attach(p)

        server = smtplib.SMTP(smtp_server, smtp_port, timeout=15)
        server.starttls()
        server.login(sender_email, smtp_password)
        server.sendmail(sender_email, destinataire, msg.as_string())
        server.quit()
        return True, "E-mail professionnel envoyé avec succès par le serveur SMTP."
    except Exception as e:
        return False, f"Erreur d'envoi SMTP : {str(e)}"

# =========================================================
# INTERFACE PRINCIPALE
# =========================================================
st.markdown('<div class="header-banner"><h1>🇨🇮 Kelanewin Transit - SYDAM Pro Enterprise</h1><p>Plateforme de Dédouanement, Transit et Automatisation Intelligente</p></div>', unsafe_allow_html=True)

tab_facturation, tab_crm, tab_config = st.tabs(["📊 Facturation & Communications", "📁 Suivi CRM", "⚙️ Configuration Serveur"])

with tab_facturation:
    st.markdown('<div class="custom-card-3d">', unsafe_allow_html=True)
    st.subheader("📤 Envoi de Documents, E-mails & WhatsApp")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        client_nom = st.text_input("Nom du Client", value="Kouadio & Frères")
        email_client = st.text_input("E-mail du Client", value="client@domaine.ci")
        tel_client = st.text_input("Téléphone WhatsApp", value="+2250700000000")
    with col_f2:
        montant_facture = st.number_input("Montant Total (FCFA)", value=250000)
        message_personnalise = st.text_area("Message / Objet", value="Bonjour, veuillez trouver ci-joint votre facture et l'état de votre dossier de transit.")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("📧 Envoyer l'E-mail Réel (SMTP)", use_container_width=True):
            succes, msg_res = envoyer_email_smtp(email_client, "Avis de Dossier - Kelanewin Transit", message_personnalise)
            if succes:
                st.success(f"✅ {msg_res}")
            else:
                st.error(f"❌ {msg_res}")

    with col_s2:
        # Intégration WhatsApp professionnelle (Lien API direct ou Cloud API)
        clean_tel = tel_client.strip().replace("+", "").replace(" ", "")
        whatsapp_url = f"https://wa.me/{clean_tel}?text={quote(message_personnalise)}"
        st.link_button("💬 Envoyer par WhatsApp", whatsapp_url, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

with tab_config:
    st.markdown('<div class="custom-card-3d">', unsafe_allow_html=True)
    st.subheader("⚙️ Diagnostic & Paramètres d'Environnement SMTP")
    
    env_email = os.environ.get("SMTP_SENDER_EMAIL", "Non défini")
    has_pass = "Défini (Sécurisé)" if os.environ.get("SMTP_SENDER_PASSWORD") else "Non défini"
    
    st.info(f"""
    * **Serveur SMTP Actuel :** {os.environ.get('SMTP_HOST', 'smtp.gmail.com')} (Port {os.environ.get('SMTP_PORT', 587)})
    * **Expéditeur configuré (`SMTP_SENDER_EMAIL`) :** `{env_email}`
    * **Mot de passe (`SMTP_SENDER_PASSWORD`) :** `{has_pass}`
    """)
    
    st.markdown("### Comment configurer vos identifiants :")
    st.markdown("""
    1. **En local :** Définissez les variables d'environnement dans votre terminal avant de lancer Streamlit :
       ```bash
       export SMTP_SENDER_EMAIL="votre-email@gmail.com"
       export SMTP_SENDER_PASSWORD="votre-mot-de-passe-application"
       streamlit run app.py
       ```
    2. **Sur Streamlit Cloud / Hébergeur :** Rendez-vous dans les paramètres de votre application (`App Settings > Secrets`) et ajoutez :
       ```toml
       SMTP_SENDER_EMAIL = "votre-email@gmail.com"
       SMTP_SENDER_PASSWORD = "votre-mot-de-passe-application"
       ```
    """)
    st.markdown('</div>', unsafe_allow_html=True)
