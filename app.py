import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Système Anti-Fraude & Rétrocession en Cascade (Norme RBI/CENTIF)", layout="wide")

st.title("🛡️ Module National de Résolution des Litiges & Blocage en Cascade")
st.caption("Architecture conforme aux directives de la RBI (India Model) et de la BCEAO / CENTIF")

# 1. Barre latérale - Paramètres de conformité
st.sidebar.header("⚙️ Normes Réglementaires")
st.sidebar.markdown("**Cadre d'application :**")
st.sidebar.write("- Directive RBI/NPCI sur les transactions frauduleuses")
st.sidebar.write("- Instruction BCEAO LCB-FT / CENTIF")
st.sidebar.write("- Délai d'interception d'urgence (SLA) : **< 30 minutes**")

# Tabs pour l'application
tab_signalement, tab_traçage, tab_conformation = st.tabs([
    "🚨 1. Signalement & Ticket d'Urgence", 
    "🔍 2. Graphe de Traçage & Gel Conservatoire", 
    "📜 3. Rapport de Rétrocession & Conformité"
])

# ----------------------------------------------------
# TAB 1 : SIGNALEMENT ET CRÉATION DE TICKET
# ----------------------------------------------------
with tab_signalement:
    st.header("Déclaration Immédiate de Transfert Erroné / Suspect")
    
    col1, col2 = st.columns(2)
    with col1:
        id_transaction = st.text_input("Identifiant unique de transaction (UTRN / Ref)", "TXN-2026-9988234")
        emetteur_num = st.text_input("Numéro de l'expéditeur (Victime)", "+225 0701020304")
        montant = st.number_input("Montant contesté (FCFA)", min_value=1000, value=500000, step=5000)
    
    with col2:
        plateforme = st.selectbox("Canal d'origine", ["Wave", "Orange Money", "MTN MoMo", "Virement Interbancaire (BCEAO)"])
        motif_incident = st.selectbox(
            "Catégorie de l'incident", 
            [
                "Erreur de saisie de numéro (Wrong Beneficiary)",
                "Fraude / Ingestion par ingénierie sociale",
                "Transaction non autorisée (Vol de compte)",
                "Compte Mule suspecté"
            ]
        )
        horodatage = st.time_input("Heure exacte du transfert", datetime.time(11, 30))

    st.markdown("---")
    lancer_procedure = st.button("🚨 DÉCLENCHER LE PROTOCOLE DE GEL CONSERVATOIRE")

# ----------------------------------------------------
# TAB 2 : TRAÇAGE ET GEL DES COMPTES MULES (MULE HUNTER MODULE)
# ----------------------------------------------------
with tab_traçage:
    st.header("Mule Account Cascade Freezing Engine")
    
    if 'procedure_active' not in st.session_state:
        st.session_state.procedure_active = False

    if lancer_procedure:
        st.session_state.procedure_active = True

    if st.session_state.procedure_active:
        st.error(f"⚠️ PROTOCOLE D'URGENCE DÉCLENCHÉ POUR LA TRANSACTION : **{id_transaction}**")
        
        # Algorithme de simulation de traçage du flux (Niveaux X, Y, Z)
        data_chaine = [
            {
                "Niveau de Traçage": "Niveau 1 (Recepteur Direct X)",
                "Compte Identifié": "+225 0509080706",
                "Plateforme": plateforme,
                "Montant Reçu": f"{montant:,.0f} FCFA",
                "Solde Restant": f"{montant * 0.4:,.0f} FCFA",
                "Statut du Gel": "🛑 GELÉ (Hold)",
                "Action": "Blocage des retraits & Transferts"
            },
            {
                "Niveau de Traçage": "Niveau 2 (Compte Intermediate Y)",
                "Compte Identifié": "+225 0102030405",
                "Plateforme": "Wave",
                "Montant Reçu": f"{montant * 0.4:,.0f} FCFA",
                "Solde Restant": f"{montant * 0.2:,.0f} FCFA",
                "Statut du Gel": "🛑 GELÉ (Hold)",
                "Action": "Blocage des retraits & Transferts"
            },
            {
                "Niveau de Traçage": "Niveau 3 (Compte Terminus Z)",
                "Compte Identifié": "+225 0708091011",
                "Plateforme": "Orange Money",
                "Montant Reçu": f"{montant * 0.2:,.0f} FCFA",
                "Solde Restant": f"{montant * 0.2:,.0f} FCFA",
                "Statut du Gel": "🛑 GELÉ (Hold)",
                "Action": "Cash-Out Bloqué en Point de Vente"
            }
        ]
        
        df_mule = pd.DataFrame(data_chaine)
        st.subheader("Graphe de circulation des fonds et statut d'interception")
        st.table(df_mule)
        
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Fonds Secourus / Récupérables", f"{montant:,.0f} FCFA", "100%")
        col_b.metric("Nombre de comptes Mules bloqués", "3 comptes", "+3")
        col_c.metric("Temps d'exécution du gel", "1.2 seconde", "Automatique")

        st.warning(
            "🔒 **Saisie Conservatoire Automatique :** "
            "Les soldes des comptes X, Y et Z ont été restreints par clé API d'urgence. "
            "Aucune opération de retrait en liquide (Cash-Out) ou de transfert sortant n'est autorisée pour ces utilisateurs."
        )
    else:
        st.info("Veuillez d'abord remplir et valider un signalement dans l'onglet 1.")

# ----------------------------------------------------
# TAB 3 : RÉTROCESION ET PROCÈS-VERBAL CENTIF / REGULATEUR
# ----------------------------------------------------
with tab_conformation:
    st.header("Génération du Procès-Verbal de Rétrocession")
    
    st.markdown("""
    **Caractéristiques de l'Ordre de Rétrocession (Normes RBI / BCEAO) :**
    1. **Mandat de remboursement automatique :** Si aucune justification valide n'est fournie sous 24h par le tiers, les fonds en séquestre sont réacheminés vers l'émetteur.
    2. **Notification d'obligation :** Un SMS légal d'avertissement est envoyé aux détenteurs des comptes ciblés.
    3. **Enregistrement CENTIF :** Fiche d'incident générée pour inscription sur la liste des comptes suspects.
    """)
    
    if st.button("📄 Générer le Rapport Légal (PDF / Format CENTIF)"):
        st.success("✅ Rapport de gel conservatoire généré avec succès !")
        
        st.json({
            "Reference_Incident": id_transaction,
            "Norme_Applicable": "RBI Cyber Dispute / BCEAO AML-KYC",
            "Dispositif_Applique": "Cascade Account Freezing Protocol",
            "Montant_Total_Sous_Sequestre": montant,
            "Nombre_Comptes_Affectes": 3,
            "Statut_Dossier": "En cours de restitution"
        })