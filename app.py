import datetime
import uuid
import pandas as pd
import streamlit as st

# -----------------------------------------------------------------------------
# CONFIGURATION DE LA PAGE & STYLE CSS (Navigation Verticale iOS & 3D Glassmorphism)
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

    /* Arrière-plan global : Dégradé bleu nuit profond et sophistiqué */
    .stApp {
        background: linear-gradient(145deg, #070b19 0%, #0f172a 50%, #090d16 100%);
        color: #f8fafc;
    }

    /* --- CARTES GLASSMORPHISM & EFFET 3D (Style visionOS / iOS 18) --- */
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

    .dashboard-card:hover, div[data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 24px 48px 0 rgba(0, 0, 0, 0.5), 
                    inset 0 1px 0 0 rgba(255, 255, 255, 0.25);
        border: 1px solid rgba(59, 130, 246, 0.4);
    }

    /* --- BARRE LATÉRALE STYLE iOS VERTICALE --- */
    section[data-testid="stSidebar"] {
        background: rgba(11, 18, 32, 0.92);
        backdrop-filter: blur(25px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Boutons de navigation verticale façon vignettes iOS */
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
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.3);
    }

    /* Champs de saisie modernes */
    input, select, textarea, div[data-baseweb="select"] {
        border-radius: 12px !important;
        background-color: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        color: white !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# BARRE LATÉRALE : NAVIGATION VERTICALE TYPE iPHONE / iOS
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
        (
            "Banque Commerciale (SGBCI, Ecobank, Coris, Attijariwafa, UBA,"
            " Stanbic)"
        ),
        (
            "Opérateur Mobile Money (Wave, Orange Money, MTN MoMo, Moov, M-Pesa,"
            " Airtel)"
        ),
        "FinTech / Neobanque (Djamo, Kuda, Chipper Cash)",
        "Institution de Microfinance (Baobab, Advans, Cofina)",
        (
            "Régulateur / Cellule de Renseignement Financier (CENTIF, ANIF,"
            " BCEAO)"
        ),
    ],
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧭 Navigation iOS Verticale")

# Gestion de la page active via des boutons verticaux dans la sidebar
if "active_module" not in st.session_state:
    st.session_state.active_module = "🏠 Tableau de bord"

# Définition des modules et icônes
modules = {
    "🏠 Tableau de bord": "Tableau de bord exécutif et indicateurs globaux",
    "💳 Banque & Scoring Crédit": "Scoring d'octroi prudentiel (Bâle III)",
    "🚨 Détection de Fraude": "Gel en cascade et traçage des comptes mules",
    "📱 Mobile Money & Néobanques": "Scoring alternatif pour secteur informel",
    "🌱 Risque Agricole": "Modélisation agro-saisonnier (Cacao/Café)",
    "🌍 Paiements Transfrontaliers": "Interconnexion PAPSS / Afreximbank",
    "📈 Stress-Tests Prudentiels": "Analyse de résistance sous chocs",
    "📂 Sources de Données": "Registre et dictionnaire des indicateurs (Data Center)",
    "📜 Rapports & Historique": "Conformité CENTIF/ANIF & export ISO 20022",
    "⚙️ Paramètres": "Configuration et méthodologie de la plateforme",
}

for mod_name, mod_desc in modules.items():
    if st.sidebar.button(mod_name, key=f"nav_{mod_name}"):
        st.session_state.active_module = mod_name

st.sidebar.markdown("---")
st.sidebar.subheader("🔒 Protocoles Actifs")
st.sidebar.write("✔️ Standard ISO 20022")
st.sidebar.write("✔️ Règlementation LCB-FT")
st.sidebar.write("✔️ Compensation PAPSS")

# -----------------------------------------------------------------------------
# ZONE PRINCIPALE : AFFICHAGE DU MODULE ACTIF SÉLECTIONNÉ
# -----------------------------------------------------------------------------
current_page = st.session_state.active_module

# En-tête contextuel
st.title(f"{current_page}")
st.caption(
    f"Plateforme unifiée — Zone : **{zone_reglementaire}** | Organisme :"
    f" **{institution_type}**"
)
st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 1. TABLEAU DE BORD EXÉCUTIF
# -----------------------------------------------------------------------------
if current_page == "🏠 Tableau de bord":
    st.header("Vue d'ensemble de la Sécurité Financière & du Scoring")
    st.info(
        "Bienvenue sur le tableau de bord exécutif. Retrouvez ci-dessous les"
        " indicateurs clés consolidés de la plateforme."
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "Dossiers Analysés", "1,482", delta="+12% ce mois", delta_color="normal"
    )
    col2.metric(
        "Taux de Fraude Intercepté",
        "99.4%",
        delta="+0.8%",
        delta_color="normal",
    )
    col3.metric(
        "Volume Traité (PAPSS)",
        "42.8 Mds FCFA",
        delta="+15.4%",
        delta_color="normal",
    )
    col4.metric(
        "Indice de Risque Global", "Faible (A+)", delta="Stable", delta_color="off"
    )

    st.markdown("---")
    st.subheader("📊 Performance Opérationnelle Récente")
    chart_data = pd.DataFrame(
        {
            "Mois": ["Nov", "Déc", "Jan", "Fév", "Mar", "Avr"],
            "Crédits Octroyés": [120, 150, 180, 220, 290, 340],
            "Fraudes Bloquées": [15, 22, 18, 30, 45, 38],
        }
    )
    st.line_chart(chart_data.set_index("Mois"))

# -----------------------------------------------------------------------------
# 2. BANQUE ET SCORING DE CRÉDIT
# -----------------------------------------------------------------------------
elif current_page == "💳 Banque & Scoring Crédit":
    st.header(
        "Analyse Solvabilité & Octroi Prudentiel (BCEAO / BEAC / Bâle III)"
    )
    st.info(
        "Évaluation automatique du risque de crédit pour les entreprises, PME"
        " et particuliers."
    )

    col_cr1, col_cr2 = st.columns(2)
    with col_cr1:
        secteur = st.selectbox(
            "Secteur d'Activité",
            [
                "Agro-industrie",
                "Commerce Général & Import-Export",
                "BTP & Infrastructure",
                "Transport & Logistique",
                "Services & Salariés",
            ],
        )
        chiffre_affaires = st.number_input(
            "Chiffre d'Affaires / Revenu mensuel moyen (FCFA)",
            min_value=100000,
            value=5000000,
            step=100000,
        )
        engagements_encours = st.number_input(
            "Remboursements de prêts en cours / mois (FCFA)",
            min_value=0,
            value=500000,
            step=20000,
        )

    with col_cr2:
        pret_demande = st.number_input(
            "Montant du Prêt Demandé (FCFA)",
            min_value=100000,
            value=10000000,
            step=250000,
        )
        duree_mois = st.slider("Durée du remboursement (Mois)", 1, 60, 12)
        registre_impayes = st.radio(
            "Fichage Banque Centrale (CIP / Bureau de Crédit)",
            ["Aucun incident", "Régularisé", "Incident actif / Interdit bancaire"],
        )

    mensualite = (pret_demande * 1.02) / duree_mois
    taux_endettement = (
        ((engagements_encours + mensualite) / chiffre_affaires) * 100
        if chiffre_affaires > 0
        else 100
    )

    st.markdown("---")
    st.subheader("📋 Décision Automatisée d'Octroi de Crédit")

    m1, m2, m3 = st.columns(3)
    m1.metric("Mensualité Calculée", f"{mensualite:,.0f} FCFA / mois")
    m2.metric(
        "Taux d'Endettement Projeté",
        f"{taux_endettement:.1f} %",
        delta=(
            "Norme max : 33%"
            if taux_endettement <= 33
            else "Dépassement de norme"
        ),
        delta_color="normal" if taux_endettement <= 33 else "inverse",
    )
    m3.metric(
        "Capacité d'Endettement Dispo",
        f"{max(0, (chiffre_affaires * 0.33) - engagements_encours):,.0f} FCFA",
    )

    if registre_impayes == "Incident actif / Interdit bancaire":
        st.error(
            "❌ **OCTROI REFUSÉ :** Emprunteur fiché au Bureau d'Information sur"
            " le Crédit (BIC)."
        )
    elif taux_endettement > 33:
        st.error(
            f"❌ **OCTROI REFUSÉ :** Taux d'endettement ({taux_endettement:.1f}%)"
            " supérieur au plafond réglementaire de 33%."
        )
    else:
        st.success(
            f"✅ **PRÊT VALIDÉ :** Déblocage autorisé de {pret_demande:,.0f}"
            " FCFA."
        )

# -----------------------------------------------------------------------------
# 3. DÉTECTION DE FRAUDE
# -----------------------------------------------------------------------------
elif current_page == "🚨 Détection de Fraude":
    st.header(
        "Moteur d'Interception des Fraudes & Traçage des Comptes Mules"
    )
    st.info(
        "Interconnexion multi-réseaux pour geler instantanément la chaîne de"
        " comptes complices."
    )

    c1, c2 = st.columns(2)
    with c1:
        utrn = st.text_input(
            "Référence Transactionnelle Unique (UTRN)",
            f"UTRN-{uuid.uuid4().hex[:10].upper()}",
        )
        compte_victime = st.text_input(
            "Compte Émetteur / Déclarant", placeholder="+225 07 00 00 00 00"
        )
        montant_contesté = st.number_input(
            "Montant de la Transaction Contestée",
            min_value=1000,
            value=2500000,
            step=50000,
        )

    with c2:
        plateforme_source = st.selectbox(
            "Plateforme d'Origine",
            [
                "Wave",
                "Orange Money",
                "MTN MoMo",
                "Moov Money",
                "M-Pesa",
                "Virement Interbancaire",
            ],
        )
        typologie_fraude = st.selectbox(
            "Typologie de l'Incident",
            [
                "Erreur de Saisie de Numéro",
                "Ingénierie Sociale / Phishing",
                "Compte Mule / Blanchiment Suspecté",
                "Piratage SIM Swap",
            ],
        )
        niveau_urgence = st.select_slider(
            "Urgence Réglementaire",
            options=["CRITIQUE (Gel < 30 secondes)", "ÉLEVÉ", "MODÉRÉ"],
        )

    st.subheader("🕸️ Reconstitution Dynamique du Graphe de Transferts")
    nb_niveaux = st.slider("Nombre de comptes récepteurs détectés", 1, 5, 3)

    comptes_chaine = []
    mules_bloquees = [
        "+225 05 09 08 07 06",
        "+237 6 90 00 11 22",
        "+254 7 12 34 56 78",
    ]

    for i in range(nb_niveaux):
        col_n1, col_n2, col_n3, col_n4 = st.columns([2, 2, 2, 2])
        with col_n1:
            compte_id = st.text_input(
                f"Compte Récepteur N{i+1}",
                key=f"c_pan_{i}",
                placeholder="+225...",
            )
        with col_n2:
            op_id = st.selectbox(
                f"Établissement N{i+1}",
                [
                    "Wave",
                    "Orange Money",
                    "MTN MoMo",
                    "M-Pesa",
                    "Ecobank",
                    "SGBCI",
                    "Coris Bank",
                    "UBA",
                ],
                key=f"op_pan_{i}",
            )
        with col_n3:
            ratio_part = st.slider(
                f"Part transmise N{i+1} (%)", 10, 100, 100 - (i * 15), key=f"rat_pan_{i}"
            )
            montant_niveau = (montant_contesté * ratio_part) / 100
        with col_n4:
            is_mule = compte_id in mules_bloquees
            st.markdown(
                "Status : "
                + (
                    "<span style='color:#ef4444; font-weight:bold;'>🚨"
                    " RÉSIDIVISTE</span>"
                    if is_mule
                    else "<span style='color:#f59e0b;'>⚠️ POTENTIEL</span>"
                ),
                unsafe_allow_html=True,
            )

        if compte_id:
            comptes_chaine.append(
                {
                    "Niveau": f"Niveau {i+1}",
                    "Identifiant Compte": compte_id,
                    "Opérateur / Banque": op_id,
                    "Montant Localisé": f"{montant_niveau:,.0f} FCFA / Unités",
                    "Risque Récidive": "CRITIQUE" if is_mule else "MODÉRÉ",
                    "Action Exécutée": "SÉQUESTRE CONSERVATOIRE (HOLD)",
                }
            )

    st.markdown("---")
    if st.button("🚨 DÉCLENCHER L'ORDRE NATIONAL / PANAFRICAIN DE GEL"):
        if not compte_victime or len(comptes_chaine) == 0:
            st.error(
                "⚠️ Veuillez saisir le compte émetteur et au moins un compte"
                " récepteur."
            )
        else:
            st.error(
                f"🛑 ORDRE DE BLOCAGE SYSTÉMIQUE TRANSMIS — RÉF : {utrn}"
            )
            st.table(pd.DataFrame(comptes_chaine))
            st.success(
                "✅ **Mesures de blocage actives :** Retraits DAB/Kiosques"
                " désactivés et virements sortants bloqués."
            )

# -----------------------------------------------------------------------------
# 4. MOBILE MONEY ET NÉOBANQUES
# -----------------------------------------------------------------------------
elif current_page == "📱 Mobile Money & Néobanques":
    st.header(
        "Alternative Credit Scoring pour le Secteur Informel & Neobanques"
    )
    st.info(
        "Octroi de crédit basé sur les données de portefeuilles électroniques"
        " (Wave, Orange, MTN, M-Pesa)."
    )

    col_mb1, col_mb2 = st.columns(2)
    with col_mb1:
        flux_entrants_3mois = st.number_input(
            "Cumul des encaissements sur 3 mois (FCFA)",
            min_value=50000,
            value=3000000,
        )
        frequence_vente_jour = st.number_input(
            "Nombre moyen de paiements reçus par jour", min_value=1, value=25
        )
        anciennete_portefeuille = st.slider(
            "Ancienneté du compte marchand (Mois)", 1, 48, 18
        )

    with col_mb2:
        solde_moyen_nuit = st.number_input(
            "Solde moyen conservé à la fermeture (FCFA)",
            min_value=0,
            value=250000,
        )
        taux_retrait_cash = st.slider(
            "% du solde converti immédiatement en espèces", 0, 100, 35
        )
        stabilité_geographique = st.selectbox(
            "Stabilité de la zone d'activité",
            [
                "Très stable (Même commune/marché)",
                "Mobile (Régional)",
                "Instable",
            ],
        )

    score_fintech = 400
    if anciennete_portefeuille >= 12:
        score_fintech += 120
    if solde_moyen_nuit >= 100000:
        score_fintech += 180
    if taux_retrait_cash < 50:
        score_fintech += 150
    if stabilité_geographique == "Très stable (Même commune/marché)":
        score_fintech += 100

    st.markdown("---")
    st.subheader("📊 Score FinTech Alternative")
    st.metric("Score de Crédit Digital", f"{score_fintech} / 950 points")

    if score_fintech >= 750:
        st.success(
            "🌟 **Catégorie A (Excellente) :** Prêt de trésorerie instantané"
            " déblocable en 1 clic."
        )
    elif score_fintech >= 600:
        st.warning(
            "⚡ **Catégorie B (Modérée) :** Prêt accordé avec plafonnement à"
            " 50%."
        )
    else:
        st.error("🚫 **Catégorie C (Élevée) :** Solde de nuit insuffisant.")

# -----------------------------------------------------------------------------
# 5. RISQUE AGRICOLE
# -----------------------------------------------------------------------------
elif current_page == "🌱 Risque Agricole":
    st.header(
        "Modélisation Agricole Panafricaine & Campagnes Cacao / Café"
    )
    st.info(
        "Ajuste les échéanciers de remboursement des coopératives sur les cycles"
        " réels."
    )

    col_ag1, col_ag2 = st.columns(2)
    with col_ag1:
        bassin_prod = st.selectbox(
            "Zone de Production",
            [
                "Côte d'Ivoire - Bas-Sassandra",
                "Côte d'Ivoire - Haut-Sassandra",
                "Ghana - Ashanti Region",
                "Cameroun",
                "Kenya",
            ],
        )
        culture_type = st.selectbox(
            "Culture Spéculative",
            ["Cacao", "Café", "Anacarde (Cajou)", "Coton", "Hévéa / Palmier"],
        )
        surface_ha = st.number_input(
            "Surface exploitée (Hectares)", min_value=0.5, value=8.0
        )

    with col_ag2:
        rendement_estime = st.number_input(
            "Rendement moyen (Kg / Hectare)", min_value=100, value=750
        )
        prix_fixe_etat = st.number_input(
            "Prix d'achat bord champ (FCFA / Kg)", min_value=500, value=1500
        )
        aléa_climatique = st.select_slider(
            "Risque Météo / Sécheresse",
            options=[
                "Conditions Optimales",
                "Déficit hydrique modéré",
                "Sécheresse Sévère / Inondation",
            ],
        )

    prod_totale = surface_ha * rendement_estime
    revenu_agri = prod_totale * prix_fixe_etat
    if aléa_climatique == "Sécheresse Sévère / Inondation":
        revenu_agri *= 0.55

    st.markdown("---")
    st.subheader("📅 Échéancier Flottant Aligné sur les Récoltes")
    st.metric("Revenu Net Estimé de la Campagne", f"{revenu_agri:,.0f} FCFA")
    st.write(
        "• **Grande Campagne (Octobre à Mars) :** Prélèvement de 85%."
    )
    st.write("• **Petite Campagne (Avril à Juillet) :** Prélèvement de 15%.")
    st.write(
        "• **Période de Soudure (Août/Septembre) :** Suspension des"
        " échéances."
    )

# -----------------------------------------------------------------------------
# 6. PAIEMENTS TRANSFRONTALIERS
# -----------------------------------------------------------------------------
elif current_page == "🌍 Paiements Transfrontaliers":
    st.header(
        "Plateforme Interbancaire de Paiement Transfrontalier (PAPSS)"
    )
    st.info(
        "Règlements instantanés et conversion automatique des devises locales"
        " entre pays d'Afrique."
    )

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        pays_origine = st.selectbox(
            "Pays Émetteur",
            [
                "Côte d'Ivoire (XOF)",
                "Sénégal (XOF)",
                "Nigéria (NGN)",
                "Kenya (KES)",
                "Cameroun (XAF)",
            ],
        )
        banque_emetteur = st.selectbox(
            "Banque / Opérateur Source",
            ["Ecobank", "SGBCI", "Wave CI", "Zenith Bank", "KCB Kenya"],
        )
        montant_devise_source = st.number_input(
            "Montant à envoyer (Monnaie Locale)", min_value=10000, value=5000000
        )

    with col_p2:
        pays_destination = st.selectbox(
            "Pays Destinataire",
            ["Nigéria (NGN)", "Kenya (KES)", "Ghana (GHS)", "Côte d'Ivoire (XOF)"],
        )
        banque_destinataire = st.selectbox(
            "Banque / Opérateur Cible",
            ["Access Bank", "M-Pesa Kenya", "GCB Ghana", "NSIA Banque"],
        )
        motif_commercial = st.selectbox(
            "Type d'Échange ZLECAF",
            [
                "Importation Marchandises B2B",
                "Règlement Prestation",
                "Trésorerie Filiale",
            ],
        )

    st.markdown("---")
    if st.button("💱 SIMULER LA COMPENSATION EN MONNAIE LOCALE VIA PAPSS"):
        st.success(
            "✅ **Règlement Transfrontalier Autorisé sous Accord Afreximbank"
            " :**"
        )
        st.write(
            "• **Élimination du besoin en USD / Euros :** Conversion directe"
            " XOF ↔ NGN/KES."
        )
        st.write("• **Temps de Règlement :** Exécuté sous 120 secondes.")

# -----------------------------------------------------------------------------
# 7. STRESS-TESTS PRUDENTIELS
# -----------------------------------------------------------------------------
elif current_page == "📈 Stress-Tests Prudentiels":
    st.header("Module Prudentiel d'Analyse des Chocs (Bâle III / IFRS 9)")
    st.info(
        "Évalue la résistance du portefeuille face aux chocs macroéconomiques."
    )

    col_st1, col_st2 = st.columns(2)
    with col_st1:
        choc_chiffre_affaires = st.slider(
            "Choc de baisse du Chiffre d'Affaires (%)", 0, 70, 35
        )
        hausse_taux_interet = st.slider(
            "Hausse du taux directeur (+ points de base)", 0, 500, 150
        )

    with col_st2:
        provision_requise_ifrs9 = (
            "Stage 1 (Normal)"
            if choc_chiffre_affaires < 20
            else (
                "Stage 2 (Dégradation significative)"
                if choc_chiffre_affaires < 40
                else "Stage 3 (Défaillance / NPL)"
            )
        )
        st.metric("Classification IFRS 9 du Prêt", provision_requise_ifrs9)

    st.markdown("---")
    st.subheader("🧪 Résultat de la Simulation sous Choc")
    if choc_chiffre_affaires > 30:
        st.error(
            "🚨 **RISQUE DE DÉFAUT ÉLEVÉ :** Nécessite une restructuration de"
            " dette."
        )
    else:
        st.success("🛡️ **CAPACITÉ DE RÉSISTANCE CONFIRMÉE.**")

# -----------------------------------------------------------------------------
# 8. SOURCES DE DONNÉES (DATA CENTER)
# -----------------------------------------------------------------------------
elif current_page == "📂 Sources de Données":
    st.header("Data Center & Registre des Sources")
    st.info(
        "Traçabilité complète des sources de données réglementaires et"
        " internes."
    )

    sources_df = pd.DataFrame(
        {
            "Source / Base": [
                "BCEAO / BEAC Central Repository",
                "Bureau d'Information sur le Crédit (BIC)",
                "PAPSS Transaction Network",
                "Portefeuilles Mobile Money (Wave/Orange/MTN)",
            ],
            "Type de Données": [
                "Réglementaire & Prudentiel",
                "Historique d'impayés / CIP",
                "Flux transfrontaliers instantanés",
                "Comportementales & Alternatives",
            ],
            "Fréquence de Mise à Jour": [
                "Quotidienne",
                "Temps réel",
                "Instantané (<120s)",
                "En continu",
            ],
            "Statut": ["Connecté", "Actif", "Sécurisé", "Actif"],
        }
    )
    st.table(sources_df)

# -----------------------------------------------------------------------------
# 9. RAPPORTS ET HISTORIQUE
# -----------------------------------------------------------------------------
elif current_page == "📜 Rapports & Historique":
    st.header("Registre d'Audit & Rapports Réglementaires")
    st.markdown(
        "Exportation automatisée des déclarations de transactions suspectes"
        " (DTS) vers les cellules de renseignement financier."
    )

    if st.button(
        "📄 GÉNÉRER LE RAPPORT STRUCTURÉ D'ALERTE (ISO 20022 camt.056)"
    ):
        rapport_iso = {
            "Document": {
                "FIToFIPmtCxlReq": {
                    "GrpHdr": {
                        "MsgId": f"CENTIF-CI-{uuid.uuid4().hex[:12].upper()}",
                        "CreDtTm": datetime.datetime.now().isoformat(),
                        "NbOfTxs": "1",
                    },
                    "TxInf": {
                        "CancellationReasonInformation": {
                            "Rsn": {"Cd": "FRAD"},
                            "AddtlInf": (
                                "Mule Account Cascade Freezing Executed under"
                                " BCEAO Regulations"
                            ),
                        }
                    },
                }
            }
        }
        st.json(rapport_iso)
        st.success(
            "✅ Fichier d'instruction réglementaire prêt pour transmission"
            " sécurisée."
        )

# -----------------------------------------------------------------------------
# 10. PARAMÈTRES
# -------------------------------------------------------------
elif current_page == "⚙️ Paramètres":
    st.header("Paramètres de la Plateforme & Méthodologie")
    st.info(
        "Configuration générale des seuils de risque et des modèles de"
        " Scoring."
    )

    st.text_input("Nom de l'administrateur", value="Kouassi Kouame Daniel")
    st.text_input("Email institutionnel", value="daniel.kouassi@fintech-panafricaine.com")
    st.slider("Seuil d'alerte critique de fraude (Score)", 50, 100, 85)
    
    if st.button("Enregistrer les modifications"):
        st.success("✅ Paramètres mis à jour avec succès.")
