import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

df = pd.read_csv('donnees_fintech_uemoa.csv')

# --- 1. MODÈLE DE CREDIT SCORING ---
X_credit = df[['secteur_activite', 'revenu_mensuel_estime_fcfa', 'volume_flux_mobile_money_fcfa',
               'solde_epargne_mobile_fcfa', 'retards_paiement_6mois', 'taux_endettement', 'membre_cooperative_tontine']]
y_credit = df['defaut_paiement']

preprocessor_credit = ColumnTransformer(
    transformers=[
        ('num', 'passthrough', ['revenu_mensuel_estime_fcfa', 'volume_flux_mobile_money_fcfa',
                                'solde_epargne_mobile_fcfa', 'retards_paiement_6mois', 
                                'taux_endettement', 'membre_cooperative_tontine']),
        ('cat', OneHotEncoder(handle_unknown='ignore'), ['secteur_activite'])
    ]
)

model_credit = Pipeline(steps=[
    ('preprocessor', preprocessor_credit),
    ('classifier', RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42))
])

model_credit.fit(X_credit, y_credit)
joblib.dump(model_credit, 'modele_scoring_uemoa.pkl')
print("✅ Modèle de Scoring de Crédit entraîné et sauvegardé.")

# --- 2. MODÈLE DE DÉTECTION DE FRAUDE ---
X_fraude = df[['volume_flux_mobile_money_fcfa', 'solde_epargne_mobile_fcfa', 
               'nb_depots_suspects_24h', 'ratio_retrait_immediat', 'changement_sim_recent']]
y_fraude = df['est_fraude']

model_fraude = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
model_fraude.fit(X_fraude, y_fraude)
joblib.dump(model_fraude, 'modele_fraude_uemoa.pkl')
print("✅ Modèle de Détection de Fraude entraîné et sauvegardé.")