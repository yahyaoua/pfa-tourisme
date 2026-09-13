"""
Conversion fiable du fichier de statistiques touristiques vers un CSV propre.
Gere le format francais source : separateur point-virgule, nombres avec
espaces comme separateurs de milliers (ex: "4 558 091").
A lancer en local : python convert_tourism_stats.py
"""

import pandas as pd

INPUT_PATH = "data/raw/tourism_stats/nuitees_destinations.csv"
OUTPUT_PATH = "data/raw/tourism_stats/nuitees_destinations_clean.csv"

# Lecture avec le vrai separateur (point-virgule)
df = pd.read_csv(INPUT_PATH, sep=";")
print("Fichier lu avec separateur ';'.")

print("\n=== APERCU BRUT ===")
print(df.head())
print("\n=== COLONNES ===")
print(df.columns.tolist())

# Les colonnes annees contiennent des espaces (classiques ou insecables) comme
# separateurs de milliers (ex: "4 558 091") -> on les nettoie et on convertit en entier
import re

year_columns = [c for c in df.columns if c != "provinces"]

# Supprime les lignes totalement vides (souvent une derniere ligne parasite)
df = df.dropna(how="all")
df = df[df["provinces"].notna()]

for col in year_columns:
    df[col] = (
        df[col]
        .astype(str)
        .apply(lambda x: re.sub(r"\s+", "", x))  # attrape TOUS les types d'espaces
    )
    df[col] = pd.to_numeric(df[col], errors="coerce")

print("\n=== VALEURS NON CONVERTIES (si probleme restant) ===")
print(df[df[year_columns].isna().any(axis=1)])

df[year_columns] = df[year_columns].astype("Int64")

print("\n=== APERCU NETTOYE ===")
print(df.head())

# Ecriture en CSV propre, separateur virgule standard, encodage UTF-8
df.to_csv(OUTPUT_PATH, index=False, sep=",", encoding="utf-8")
print(f"\nFichier propre ecrit -> {OUTPUT_PATH}")