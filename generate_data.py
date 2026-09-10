import numpy as np
import pandas as pd

np.random.seed(42)
n_samples = 1500

# 1. Répartition des profils dans la population active en Côte d'Ivoire
secteurs = np.random.choice(
    ['Planteur_Cacao', 'Commercant_Informel', 'Salarie_Prive', 'Fonctionnaire', 'Artisan'],
    size=n_samples,
    p=[0.35, 0.25, 0.20, 0.10, 0.10]
)

# 2. Attribution des revenus réalistes basés sur le SMIG ivoirien (75 000 FCFA) et les grilles locales
revenus = []
for s in secteurs:
    if s == 'Planteur_Cacao':
        # Revenus agricoles lissés (de 75 000 à 400 000 FCFA)
        revenus.append(np.random.uniform(75000, 400000))
    elif s == 'Commercant_Informel':
        # Commerçants des grands marchés : 150 000 à 600 000 FCFA
        revenus.append(np.random.uniform(150000, 600000))
    elif s == 'Salarie_Prive':
        # Salariés du secteur privé : 100 000 à 1 500 000 FCFA
        revenus.append(np.random.uniform(100000, 1500000))
    elif s == 'Fonctionnaire':
        # Fonctionnaires : de la base indiciaire (100k) jusqu'aux hauts cadres (10 millions FCFA)
        revenus.append(np.random.uniform(100000, 10000000))
    else: # Artisan
        revenus.append(np.random.uniform(75000, 350000))

# Respect strict du plancher légal (SMIG Côte d'Ivoire)
revenus = np.maximum(75000, revenus)

# Flux Mobile Money et épargne proportionnels aux revenus
volume_flux_mm = revenus * np.random.uniform(0.5, 1.8, size=n_samples)
solde_epargne = volume_flux_mm * np.random.uniform(0.02, 0.45, size=n_samples)

# 3. Métriques Prudentielles & Risque de Crédit
retards_paiement = np.random.poisson(lam=0.7, size=n_samples)
taux_endettement = np.random.uniform(0.05, 0.80, size=n_samples)
membre_cooperative = np.random.choice([1, 0], size=n_samples, p=[0.65, 0.35])
ratio_liquidite = solde_epargne / (revenus * 0.3 + 1)

# Modélisation du Défaut de Paiement
score_credit_brut = (
    (retards_paiement * 2.0)
    + (taux_endettement * 3.5)
    - (ratio_liquidite * 1.2)
    - (membre_cooperative * 0.8)
    + np.random.normal(0, 0.6, n_samples)
)
defaut_paiement = (score_credit_brut > 1.5).astype(int)

# 4. Indicateurs de Fraude Mobile Money (AML / Structuring / SIM Swap)
nb_depots_suspects_24h = np.random.poisson(lam=0.4, size=n_samples)
ratio_retrait_immediat = np.random.uniform(0.1, 0.99, size=n_samples)
changement_sim_recent = np.random.choice([1, 0], size=n_samples, p=[0.08, 0.92])

# Modélisation du Risque de Fraude
score_fraude_brut = (
    (nb_depots_suspects_24h * 1.8)
    + (ratio_retrait_immediat * 2.5)
    + (changement_sim_recent * 3.0)
    + np.random.normal(0, 0.4, n_samples)
)
est_fraude = (score_fraude_brut > 3.2).astype(int)

# Assemblage du Dataset final
df = pd.DataFrame({
    'secteur_activite': secteurs,
    'revenu_mensuel_estime_fcfa': np.round(revenus, -3),
    'volume_flux_mobile_money_fcfa': np.round(volume_flux_mm, -3),
    'solde_epargne_mobile_fcfa': np.round(solde_epargne, -3),
    'retards_paiement_6mois': retards_paiement,
    'taux_endettement': np.round(taux_endettement, 2),
    'membre_cooperative_tontine': membre_cooperative,
    'nb_depots_suspects_24h': nb_depots_suspects_24h,
    'ratio_retrait_immediat': np.round(ratio_retrait_immediat, 2),
    'changement_sim_recent': changement_sim_recent,
    'defaut_paiement': defaut_paiement,
    'est_fraude': est_fraude
})

# Exportation vers le fichier CSV
df.to_csv('donnees_fintech_uemoa.csv', index=False)
print("✅ Dataset 100% calibré sur le marché ivoirien (SMIG, Fonctionnaires jusqu'à 10M, Commerçants) généré avec succès !")