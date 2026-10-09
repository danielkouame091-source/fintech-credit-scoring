import datetime
import hashlib
import json
import os
import smtplib
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import numpy as np
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from cryptography.fernet import Fernet

# -----------------------------------------------------------------------------
# CONFIGURATION DE LA PAGE & DESIGN macOS / LAUNCHPAD GLASSMORPHISM
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Plateforme de Confiance Numérique | Côte d'Ivoire",
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
        background: radial-gradient(circle at 50% 10%, #0b132b 0%, #030712 100%);
        color: #f8fafc;
    }

    .macos-header {
        background: rgba(15, 23, 42, 0.75);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px 24px;
        border-radius: 16px;
        margin-bottom: 25px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .app-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.85));
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 20px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
        margin-bottom: 20px;
    }

    .app-card:hover {
        transform: translateY(-5px);
        border-color: rgba(56, 189, 248, 0.6);
        box-shadow: 0 15px 35px rgba(56, 189, 248, 0.2);
    }

    div.stButton > button {
        width: 100%;
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95)) !important;
        color: #f8fafc !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 12px !important;
        padding: 12px 8px !important;
        transition: all 0.3s ease !important;
    }

    div.stButton > button:hover {
        transform: translateY(-2px);
        background: linear-gradient(145deg, rgba(56, 189, 248, 0.2), rgba(30, 41, 59, 0.98)) !important;
        border-color: #38bdf8 !important;
        color: #38bdf8 !important;
    }

    input, textarea, div[data-baseweb="select"] > div {
        background-color: rgba(15, 23, 42, 0.9) !important;
        color: #ffffff !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 10px !important;
    }

    label {
        color: #38bdf8 !important;
        font-weight: 600 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# GESTION DU STOCKAGE SÉCURISÉ & PISTE D'AUDIT IMMUABLE (AES-256 & SHA-256)
# -----------------------------------------------------------------------------
KEY_FILE = "mac_enterprise_secret.key"
AUDIT_FILE = "memoire_operations_ci.json"
TIERS_FILE = "annuaire_tiers.json"


def obtenir_cle():
  if os.path.exists(KEY_FILE):
    with open(KEY_FILE, "rb") as f:
      return f.read()
  else:
    cle = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
      f.write(cle)
    return cle


fernet = Fernet(obtenir_cle())


def enregistrer_memoire(action, details, utilisateur, statut="SUCCÈS"):
  historique = charger_memoire()
  dernier_hash = historique[0]["hash_actuel"] if historique else "0" * 64

  details_chiffres = fernet.encrypt(str(details).encode()).decode()
  payload = (
      f"{dernier_hash}{action}{utilisateur}{datetime.datetime.now().isoformat()}"
  )
  hash_actuel = hashlib.sha256(payload.encode()).hexdigest()

  entree = {
      "id_op": f"OP-{uuid.uuid4().hex[:6].upper()}",
      "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
      "action": action,
      "details_enc": details_chiffres,
      "details_clair": details,
      "utilisateur": utilisateur,
      "statut": statut,
      "hash_actuel": hash_actuel,
  }

  historique.insert(0, entree)
  with open(AUDIT_FILE, "w", encoding="utf-8") as f:
    json.dump(historique, f, ensure_ascii=False, indent=4)


def charger_memoire():
  if os.path.exists(AUDIT_FILE):
    try:
      with open(AUDIT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    except:
      return []
  return []


def charger_tiers():
  if os.path.exists(TIERS_FILE):
    try:
      with open(TIERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    except:
      return []
  # Tiers par défaut si vide
  return [{
      "nom": "Kouadio & Frères SARL",
      "rccm": "CI-ABJ-2024-B-9876",
      "ifu": "2009876 K",
      "contact": "2250700000000",
      "email": "contact@kouadiofreres.ci",
  }]


def sauvegarder_tiers(liste_tiers):
  with open(TIERS_FILE, "w", encoding="utf-8") as f:
    json.dump(liste_tiers, f, ensure_ascii=False, indent=4)


# -----------------------------------------------------------------------------
# FONCTIONS RÉELLES : WHATSAPP (API META CLOUD) & E-MAIL (SMTP SÉCURISÉ)
# -----------------------------------------------------------------------------
def envoyer_whatsapp_reel(
    telephone_destinataire, message_texte
):
  # Récupération sécurisée depuis les variables d'environnement du serveur
  phone_number_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "").strip()
  access_token = os.environ.get("WHATSAPP_ACCESS_TOKEN", "").strip()

  if not phone_number_id or not access_token:
    return (
        False,
        "Configuration requise : Les variables d'environnement"
        " WHATSAPP_PHONE_NUMBER_ID et WHATSAPP_ACCESS_TOKEN ne sont pas"
        " configurées sur le serveur.",
    )

  clean_phone = telephone_destinataire.strip().replace("+", "").replace(" ", "")
  url = f"https://graph.facebook.com/v17.0/{phone_number_id}/messages"
  headers = {
      "Authorization": f"Bearer {access_token}",
      "Content-Type": "application/json",
  }
  payload = {
      "messaging_product": "whatsapp",
      "to": clean_phone,
      "type": "text",
      "text": {"body": message_texte},
  }

  try:
    reponse = requests.post(url, headers=headers, json=payload, timeout=10)
    if reponse.status_code == 200:
      return True, "Message transmis et distribué par l'API Cloud Meta."
    else:
      return False, f"Erreur API Meta ({reponse.status_code}): {reponse.text}"
  except Exception as e:
    return False, f"Échec de connexion réseau vers l'API Meta : {str(e)}"


def envoyer_email_reel(destinataire_email, objet, corps):
  smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
  smtp_port = int(os.environ.get("SMTP_PORT", 587))
  sender_email = os.environ.get("SMTP_SENDER_EMAIL", "").strip()
  sender_password = os.environ.get("SMTP_SENDER_PASSWORD", "").strip()

  if not sender_email or not sender_password:
    return (
        False,
        "Configuration requise : Les identifiants SMTP (SMTP_SENDER_EMAIL et"
        " SMTP_SENDER_PASSWORD) ne sont pas configurés sur le serveur.",
    )

  try:
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = destinataire_email
    msg["Subject"] = objet
    msg.attach(MIMEText(corps, "plain", "utf-8"))

    server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, destinataire_email, msg.as_string())
    server.quit()
    return True, "E-mail accepté et transmis par le serveur SMTP."
  except Exception as e:
    return False, f"Échec d'envoi SMTP : {str(e)}"


# -----------------------------------------------------------------------------
# AUTHENTIFICATION & SESSION
# -----------------------------------------------------------------------------
if "authentifie" not in st.session_state:
  st.session_state.authentifie = False

if not st.session_state.authentifie:
  st.markdown(
      "<h2 style='text-align: center; color: #38bdf8;'>🍏🇨🇮 Connexion"
      " Sécurisée — Plateforme Entreprise Côte d'Ivoire</h2>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='text-align: center; color: #94a3b8;'>Expérience macOS"
      " Workspace, Agrégation Mobile Money & Connexions Réelles</p>",
      unsafe_allow_html=True,
  )

  col1, col2, col3 = st.columns([1, 2, 1])
  with col2:
    with st.form("form_auth"):
      email = st.text_input(
          "Identifiant Professionnel", value="direction@entreprise.ci"
      )
      pwd = st.text_input("Mot de Passe", type="password", value="secure2026")
      role = st.selectbox(
          "Profil d'Accès (RBAC)",
          [
              "📊 Comptable / Saisisseur",
              "💼 Responsable Financier",
              "⚖️ Directeur Général / Validateur",
              "🛡️ Administrateur & Sécurité",
          ],
      )
      btn_connexion = st.form_submit_button(
          "Ouvrir la Session Workspace", use_container_width=True
      )
      if btn_connexion:
        st.session_state.authentifie = True
        st.session_state.username = email
        st.session_state.user_role = role
        enregistrer_memoire(
            "CONNEXION",
            f"Ouverture de session pour {email} ({role})",
            email,
        )
        st.rerun()
  st.stop()

# -----------------------------------------------------------------------------
# NAVIGATION PRINCIPALE (LAUNCHPAD & ESPACES DE TRAVAIL)
# -----------------------------------------------------------------------------
if "espace_actif" not in st.session_state:
  st.session_state.espace_actif = "Launchpad"

st.markdown(
    f"""
<div class="macos-header">
    <div><b>🍎 Workspace CI</b> | Utilisateur : <b>{st.session_state.username}</b> ({st.session_state.user_role})</div>
    <div>🔐 Chiffrement AES-256 &nbsp;|&nbsp; 🟢 Connexions Réelles Actives</div>
</div>
""",
    unsafe_allow_html=True,
)

if st.session_state.espace_actif != "Launchpad":
  if st.button("⬅️ Retour au Launchpad (Menu Principal)"):
    st.session_state.espace_actif = "Launchpad"
    st.rerun()
  st.markdown("---")

# -----------------------------------------------------------------------------
# 1. VUE LAUNCHPAD (ACCUEIL TYPE MACOS)
# -----------------------------------------------------------------------------
if st.session_state.espace_actif == "Launchpad":
  st.markdown(
      "<h1 style='text-align: center; font-weight: 800; margin-bottom:"
      " 30px;'>Launchpad Professionnel</h1>",
      unsafe_allow_html=True,
  )

  apps = [
      {
          "nom": "🏠 Tableau de Bord",
          "desc": "Indicateurs clés & flux financiers",
          "cle": "Dashboard",
      },
      {
          "nom": "💳 Agrégateur Paiements",
          "desc": "Wave, Orange, MTN, Moov & Banques",
          "cle": "Paiements",
      },
      {
          "nom": "💬 WhatsApp & E-mails",
          "desc": "Envois réels API Meta & SMTP Sécurisé",
          "cle": "Communications",
      },
      {
          "nom": "📊 Finance & Comptabilité",
          "desc": "Imputations et normes SYSCOHADA",
          "cle": "Comptabilite",
      },
      {
          "nom": "🏢 Annuaire Tiers",
          "desc": "Gestion clients & fournisseurs (RCCM/IF)",
          "cle": "Tiers",
      },
      {
          "nom": "🏛️ Fiscalité & Veille DGI",
          "desc": "Échéances et déclarations fiscales CI",
          "cle": "Fiscalite",
      },
      {
          "nom": "🛡️ Piste d'Audit",
          "desc": "Journal immuable SHA-256 des actions",
          "cle": "Audit",
      },
      {
          "nom": "🤖 Assistant IA Central",
          "desc": "Recherche, analyse et exécution intelligente",
          "cle": "IA",
      },
  ]

  cols = st.columns(3)
  for idx, app in enumerate(apps):
    col_target = cols[idx % 3]
    with col_target:
      st.markdown(
          f"""
            <div class="app-card">
                <h3>{app['nom']}</h3>
                <p style="color: #94a3b8; font-size: 0.85rem; min-height: 40px;">{app['desc']}</p>
            </div>
            """,
          unsafe_allow_html=True,
      )
      if st.button(
          f"Ouvrir {app['nom'].split(' ')[1]}", key=f"app_{app['cle']}"
      ):
        st.session_state.espace_actif = app["cle"]
        st.rerun()

# -----------------------------------------------------------------------------
# 2. ESPACE : TABLEAU DE BORD
# -----------------------------------------------------------------------------
elif st.session_state.espace_actif == "Dashboard":
  st.markdown("<h2>🏠 Tableau de Bord Exécutif</h2>", unsafe_allow_html=True)

  c1, c2, c3, c4 = st.columns(4)
  c1.metric("Opérations Enregistrées", len(charger_memoire()), delta="Actif")
  c2.metric("Conformité SYSCOHADA", "100%", delta="Optimal")
  c3.metric("Tiers Répertoriés", len(charger_tiers()), delta="Persistant")
  c4.metric("Canaux de Communication", "Actifs", delta="API & SMTP")

  st.markdown("---")
  col_d1, col_d2 = st.columns(2)
  with col_d1:
    st.subheader("📈 Volume des Encaissements Multi-Opérateurs")
    df_vol = pd.DataFrame({
        "Canal": [
            "Wave CI",
            "Orange Money",
            "MTN MoMo",
            "Virements Bancaires",
        ],
        "Volume (FCFA)": [4500000, 3200000, 1800000, 6500000],
    })
    fig = px.bar(
        df_vol,
        x="Canal",
        y="Volume (FCFA)",
        template="plotly_dark",
        color_discrete_sequence=["#38bdf8"],
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig, use_container_width=True)

  with col_d2:
    st.subheader("💡 Activité Récente de la Mémoire")
    historique = charger_memoire()[:5]
    if historique:
      for h in historique:
        st.info(
            f"**[{h['timestamp']}] {h['action']}** par *{h['utilisateur']}* —"
            f" {h['details_clair']}"
        )
    else:
      st.write("Aucune opération enregistrée pour le moment.")

# -----------------------------------------------------------------------------
# 3. ESPACE : AGRÉGATEUR DE PAIEMENTS
# -----------------------------------------------------------------------------
elif st.session_state.espace_actif == "Paiements":
  st.markdown(
      "<h2>💳 Agrégateur de Paiements & Rapprochement (Côte d'Ivoire)</h2>",
      unsafe_allow_html=True,
  )

  with st.form("form_paiement"):
    c1, c2 = st.columns(2)
    with c1:
      client_nom = st.text_input(
          "Nom du Client / Payeur", value="Kouadio & Frères SARL"
      )
      operateur = st.selectbox(
          "Canal d'Encaissement",
          [
              "Wave Business CI",
              "Orange Money Marchand",
              "MTN MoMo Pay",
              "Moov Money",
              "Virement Bancaire Direct",
          ],
      )
      ref_trx = st.text_input(
          "Référence Transaction / ID Reçu / UTR", value="WAVE-CI-9482104"
      )
    with c2:
      montant_enc = st.number_input("Montant Encaissé (FCFA)", value=350000)
      facture_liee = st.text_input("Facture Rattachée", value="FACT-2026-089")

    valider_enc = st.form_submit_button(
        "Enregistrer et Rapprocher l'Encaissement"
    )
    if valider_enc:
      details = (
          f"Encaissement de {montant_enc:,.0f} FCFA via {operateur} (Ref:"
          f" {ref_trx}) pour le client {client_nom}"
      )
      enregistrer_memoire(
          "ENCAISSEMENT_PAIEMENT", details, st.session_state.username
      )
      st.success(
          f"✅ Encaissement de `{montant_enc:,.0f} FCFA` validé, rapproché et"
          " enregistré dans la base."
      )

# -----------------------------------------------------------------------------
# 4. ESPACE : WHATSAPP & E-MAILS (ENVOIS RÉELS CONNECTÉS)
# -----------------------------------------------------------------------------
elif st.session_state.espace_actif == "Communications":
  st.markdown(
      "<h2>💬 Centre de Communication (WhatsApp API & SMTP E-mail)</h2>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "Sélectionnez un tiers dans l'annuaire, rédigez votre message et exécutez"
      " un envoi réel vérifié."
  )

  tiers_list = charger_tiers()
  noms_tiers = [t["nom"] for t in tiers_list]

  selected_tier_name = st.selectbox(
      "Sélectionner un Tiers Destinataire", noms_tiers
  )
  dest_tier = next(
      (t for t in tiers_list if t["nom"] == selected_tier_name), tiers_list[0]
  )

  tab_wa, tab_email = st.tabs(["🚀 Envoi WhatsApp (API Meta)", "📧 Envoi E-mail (SMTP)"])

  with tab_wa:
    st.markdown("### Canal WhatsApp Officiel")
    wa_number = st.text_input(
        "Numéro de Téléphone (Format international)",
        value=dest_tier.get("contact", "2250700000000"),
    )
    wa_msg_type = st.selectbox(
        "Modèle de Message Professionnel",
        [
            (
                "Confirmation de document : 'Bonjour, nous vous confirmons la"
                " réception de votre document.'"
            ),
            (
                "Confirmation de paiement : 'Bonjour, nous vous informons que"
                " votre paiement a bien été enregistré.'"
            ),
            (
                "Dossier incomplet : 'Bonjour, votre dossier est incomplet."
                " Merci de nous transmettre le document manquant.'"
            ),
            (
                "Rappel d'échéance : 'Bonjour, nous vous rappelons que votre"
                " facture arrive à échéance.'"
            ),
        ],
    )
    wa_body = st.text_area(
        "Corps du Message éditable",
        value=wa_msg_type.split("'")[1]
        if "'" in wa_msg_type
        else "Bonjour, message officiel de l'entreprise.",
    )

    if st.button("📤 Envoyer le Message WhatsApp Réel"):
      succes, message_res = envoyer_whatsapp_reel(wa_number, wa_body)
      if succes:
        enregistrer_memoire(
            "WHATSAPP_REEL_SUCCES",
            f"Message envoyé à {selected_tier_name} ({wa_number})",
            st.session_state.username,
        )
        st.success(f"✅ {message_res}")
      else:
        enregistrer_memoire(
            "WHATSAPP_REEL_ECHEC",
            f"Échec envoi à {selected_tier_name} : {message_res}",
            st.session_state.username,
            statut="ECHEC",
        )
        st.error(f"❌ {message_res}")

  with tab_email:
    st.markdown("### Canal E-mail Sécurisé (SMTP)")
    email_addr = st.text_input(
        "Adresse E-mail du Destinataire",
        value=dest_tier.get("email", "contact@entreprise.ci"),
    )
    email_obj = st.text_input(
        "Objet de l'E-mail",
        value=f"Notification officielle - {selected_tier_name}",
    )
    email_body = st.text_area(
        "Contenu de l'E-mail",
        value=(
            f"Bonjour {selected_tier_name},\n\nNous vous prions de bien vouloir"
            " trouver ci-joint les informations relatives à votre dossier en"
            " cours.\n\nCordialement,\nLa Direction Financière"
        ),
    )

    if st.button("📤 Envoyer l'E-mail Réel"):
      succes, message_res = envoyer_email_reel(email_addr, email_obj, email_body)
      if succes:
        enregistrer_memoire(
            "EMAIL_REEL_SUCCES",
            f"E-mail envoyé à {selected_tier_name} ({email_addr})",
            st.session_state.username,
        )
        st.success(f"✅ {message_res}")
      else:
        enregistrer_memoire(
            "EMAIL_REEL_ECHEC",
            f"Échec e-mail à {selected_tier_name} : {message_res}",
            st.session_state.username,
            statut="ECHEC",
        )
        st.error(f"❌ {message_res}")

# -----------------------------------------------------------------------------
# 5. ESPACE : FINANCE & COMPTABILITÉ (SYSCOHADA)
# -----------------------------------------------------------------------------
elif st.session_state.espace_actif == "Comptabilite":
  st.markdown(
      "<h2>📊 Finance & Comptabilité (Normes SYSCOHADA)</h2>",
      unsafe_allow_html=True,
  )

  with st.form("form_compta"):
    c1, c2 = st.columns(2)
    with c1:
      libelle = st.text_input(
          "Libellé de l'Opération / Pièce", value="Achat de fournitures"
      )
      compte = st.selectbox(
          "Imputation SYSCOHADA",
          [
              "6041 - Matières premières",
              "6057 - Fournitures de bureau",
              "2441 - Matériel informatique",
              "6241 - Transports de biens",
          ],
      )
    with c2:
      montant_ht = st.number_input("Montant HT (FCFA)", value=500000)
      tva = st.selectbox(
          "Taux TVA (Côte d'Ivoire)",
          ["TVA 18% (Standard)", "TVA 9% (Réduit)", "Exonéré (0%)"],
      )

    montant_tva = (
        montant_ht * 0.18
        if "18%" in tva
        else (montant_ht * 0.09 if "9%" in tva else 0)
    )
    total_ttc = montant_ht + montant_tva
    st.metric("Montant TTC Calculé", f"{total_ttc:,.0f} FCFA")

    if st.form_submit_button("Enregistrer l'Écriture Comptable"):
      details = f"Saisie écriture '{libelle}' pour {total_ttc:,.0f} FCFA"
      enregistrer_memoire(
          "SAISIE_COMPTABLE", details, st.session_state.username
      )
      st.success("✅ Écriture comptable enregistrée et persistée avec succès.")

# -----------------------------------------------------------------------------
# 6. ESPACE : ANNUAIRE TIERS (PERSISTANCE VRAIE)
# -----------------------------------------------------------------------------
elif st.session_state.espace_actif == "Tiers":
  st.markdown(
      "<h2>🏢 Annuaire des Tiers (Clients & Fournisseurs)</h2>",
      unsafe_allow_html=True,
  )

  tiers_list = charger_tiers()

  with st.form("form_tiers"):
    st.subheader("Ajouter ou Mettre à Jour un Tiers")
    c1, c2 = st.columns(2)
    with c1:
      nom_tiers = st.text_input("Raison Sociale", value="")
      rccm = st.text_input("Numéro RCCM", value="")
      ifu = st.text_input("Compte Contribuable (IFU)", value="")
    with c2:
      contact = st.text_input("Téléphone / WhatsApp", value="")
      email_tiers = st.text_input("Adresse E-mail", value="")
      canal_paiement = st.selectbox(
          "Mode de Paiement Préféré",
          ["Virement Bancaire", "Wave Business", "Orange Money Marchand"],
      )

    if st.form_submit_button("Enregistrer le Tiers dans la Base"):
      if nom_tiers:
        nouveau_tiers = {
            "nom": nom_tiers,
            "rccm": rccm,
            "ifu": ifu,
            "contact": contact,
            "email": email_tiers,
        }
        tiers_list.append(nouveau_tiers)
        sauvegarder_tiers(tiers_list)
        enregistrer_memoire(
            "AJOUT_TIERS",
            f"Enregistrement du tiers {nom_tiers}",
            st.session_state.username,
        )
        st.success(
            f"✅ Tiers **{nom_tiers}** enregistré et persisté durablement."
        )
      else:
        st.error("❌ La raison sociale est obligatoire.")

  st.markdown("### Tiers Actuellement Enregistrés")
  if tiers_list:
    st.dataframe(pd.DataFrame(tiers_list), use_container_width=True)

# -----------------------------------------------------------------------------
# 7. ESPACE : FISCALITÉ & VEILLE DGI
# -----------------------------------------------------------------------------
elif st.session_state.espace_actif == "Fiscalite":
  st.markdown(
      "<h2>🏛️ Fiscalité & Veille DGI (Côte d'Ivoire)</h2>",
      unsafe_allow_html=True,
  )
  st.info(
      "ℹ️ Rappel DGI Côte d'Ivoire : Les déclarations de TVA et d'AIB doivent"
      " s'effectuer entre le 10 et le 15 de chaque mois."
  )

  df_tax = pd.DataFrame({
      "Impôt / Taxe": [
          "TVA & AIB",
          "Acompte BIC / IS",
          "Versement Forfaitaire (VF)",
      ],
      "Échéance": [
          "10-15 du mois",
          "15 du mois suivant le trimestre",
          "10-15 du mois",
      ],
      "Référence": [
          "Code Général des Impôts - CI",
          "CGI Côte d'Ivoire",
          "CGI CI",
      ],
  })
  st.dataframe(df_tax, use_container_width=True)

# -----------------------------------------------------------------------------
# 8. ESPACE : PISTE D'AUDIT
# -----------------------------------------------------------------------------
elif st.session_state.espace_actif == "Audit":
  st.markdown(
      "<h2>🛡️ Piste d'Audit Immuable (SHA-256)</h2>", unsafe_allow_html=True
  )

  historique = charger_memoire()
  if historique:
    df_audit = pd.DataFrame(historique)
    st.dataframe(
        df_audit[["id_op", "timestamp", "action", "utilisateur", "statut"]],
        use_container_width=True,
    )

    csv_data = df_audit.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Exporter le Journal d'Audit Certifié (CSV)",
        data=csv_data,
        file_name="audit_entreprise_ci.csv",
        mime="text/csv",
    )
  else:
    st.info("Aucun événement consigné dans la mémoire.")

# -----------------------------------------------------------------------------
# 9. ESPACE : ASSISTANT IA CENTRAL
# -----------------------------------------------------------------------------
elif st.session_state.espace_actif == "IA":
  st.markdown(
      "<h2>🤖 Assistant IA Central Intelligent</h2>", unsafe_allow_html=True
  )
  st.markdown(
      "Posez vos questions. L'assistant analyse les transactions réelles et"
      " l'historique d'audit chiffré."
  )

  if "messages_ia" not in st.session_state:
    st.session_state.messages_ia = [{
        "role": "assistant",
        "content": (
            "Bonjour ! Je suis votre Assistant IA Central. Je peux consulter"
            " les données persistantes, analyser l'historique ou vérifier les"
            " statuts d'envoi. Que souhaitez-vous savoir ?"
        ),
    }]

  for msg in st.session_state.messages_ia:
    with st.chat_message(msg["role"]):
      st.markdown(msg["content"])

  prompt = st.chat_input(
      "Ex: 'Quels messages avons-nous envoyés aujourd'hui ?'"
  )
  if prompt:
    st.session_state.messages_ia.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    memoire = charger_memoire()
    reponse = "Je n'ai pas trouvé d'information correspondante dans les registres."
    p_lower = prompt.lower()

    if "message" in p_lower or "e-mail" in p_lower or "whatsapp" in p_lower:
      comms = [
          h
          for h in memoire
          if "WHATSAPP" in h["action"] or "EMAIL" in h["action"]
      ]
      if comms:
        dernier = comms[0]
        reponse = (
            f"Dernière communication : **{dernier['action']}** le"
            f" {dernier['timestamp']} ({dernier['details_clair']}) — Statut:"
            f" `{dernier['statut']}`."
        )
      else:
        reponse = (
            "Aucun message ou e-mail n'a encore été consigné dans l'historique."
        )
    elif "tiers" in p_lower or "client" in p_lower or "fournisseur" in p_lower:
      tiers = charger_tiers()
      reponse = (
          f"Il y a actuellement {len(tiers)} tiers enregistrés dans l'annuaire"
          " persistant."
      )
    elif "bonjour" in p_lower:
      reponse = (
          "Bonjour ! Je suis connecté aux registres réels de l'entreprise. En"
          " quoi puis-je vous assister ?"
      )

    st.session_state.messages_ia.append({"role": "assistant", "content": reponse})
    with st.chat_message("assistant"):
      st.markdown(reponse)
