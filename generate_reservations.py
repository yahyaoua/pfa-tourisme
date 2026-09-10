"""
Generation d'un dataset synthetique de reservations touristiques au Maroc.
Calibre sur des patterns realistes : saisonnalite, destinations, prix, duree de sejour.
A lancer en local (pas besoin de Spark) : python generate_reservations.py
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker()
random.seed(42)
np.random.seed(42)

# --- Configuration ---
N_RESERVATIONS = 25000
START_DATE = datetime(2022, 1, 1)
END_DATE = datetime(2026, 8, 1)  # ~4.5 ans d'historique pour un forecasting plus robuste

# Destinations avec un poids de popularite (plus haut = plus visite)
DESTINATIONS = {
    "Marrakech":   {"weight": 30, "base_price": 450, "peak_months": [3, 4, 5, 9, 10, 11]},
    "Chefchaouen": {"weight": 12, "base_price": 300, "peak_months": [4, 5, 6, 9, 10]},
    "Essaouira":   {"weight": 10, "base_price": 350, "peak_months": [6, 7, 8]},
    "Fes":         {"weight": 12, "base_price": 380, "peak_months": [3, 4, 5, 10]},
    "Agadir":      {"weight": 15, "base_price": 400, "peak_months": [6, 7, 8, 12]},
    "Casablanca":  {"weight": 8,  "base_price": 350, "peak_months": [5, 6, 9]},
    "Tanger":      {"weight": 7,  "base_price": 320, "peak_months": [6, 7, 8]},
    "Merzouga":    {"weight": 6,  "base_price": 500, "peak_months": [3, 4, 10, 11]},
}

NATIONALITIES = {
    "Maroc": 0.30, "France": 0.25, "Espagne": 0.12, "Royaume-Uni": 0.10,
    "Allemagne": 0.08, "Etats-Unis": 0.07, "Belgique": 0.05, "Autre": 0.03
}

def seasonal_weight(month, peak_months):
    return 3.0 if month in peak_months else 1.0

def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))

rows = []
dest_names = list(DESTINATIONS.keys())
dest_weights = [d["weight"] for d in DESTINATIONS.values()]

for i in range(N_RESERVATIONS):
    destination = random.choices(dest_names, weights=dest_weights, k=1)[0]
    dest_info = DESTINATIONS[destination]

    # Date de voyage biaisee par saisonnalite : on tire une date candidate,
    # on la garde avec une proba plus forte si elle tombe en periode peak
    for _ in range(5):  # jusqu'a 5 tentatives pour respecter la saisonnalite
        travel_date = random_date(START_DATE, END_DATE)
        w = seasonal_weight(travel_date.month, dest_info["peak_months"])
        if random.random() < (w / 3.0):
            break

    lead_time_days = int(np.clip(np.random.exponential(scale=30), 1, 180))
    booking_date = travel_date - timedelta(days=lead_time_days)

    duration_nights = int(np.clip(np.random.normal(5, 2), 1, 14))
    n_travelers = random.choices([1, 2, 3, 4, 5, 6], weights=[15, 40, 15, 20, 5, 5])[0]

    season_multiplier = seasonal_weight(travel_date.month, dest_info["peak_months"]) / 2.0
    price_noise = np.random.normal(1.0, 0.15)
    price_per_night = round(dest_info["base_price"] * season_multiplier * price_noise, 2)
    total_price = round(price_per_night * duration_nights * (1 + 0.15 * (n_travelers - 1)), 2)

    nationality = random.choices(list(NATIONALITIES.keys()), weights=list(NATIONALITIES.values()), k=1)[0]
    age = int(np.clip(np.random.normal(38, 12), 18, 75))

    rows.append({
        "reservation_id": f"RES{i+1:06d}",
        "client_id": f"CLI{random.randint(1, N_RESERVATIONS // 3):05d}",  # certains clients reviennent
        "destination": destination,
        "booking_date": booking_date.strftime("%Y-%m-%d"),
        "travel_date": travel_date.strftime("%Y-%m-%d"),
        "duration_nights": duration_nights,
        "n_travelers": n_travelers,
        "price_per_night": price_per_night,
        "total_price": total_price,
        "nationality": nationality,
        "client_age": age,
    })

df = pd.DataFrame(rows)
df = df.sort_values("booking_date").reset_index(drop=True)

output_path = "data/raw/reservations/reservations.csv"
df.to_csv(output_path, index=False)

print(f"{len(df)} reservations generees -> {output_path}")
print(df.head())
print("\nRepartition par destination :")
print(df["destination"].value_counts())