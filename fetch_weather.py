"""
Recuperation des donnees meteo historiques pour les 8 destinations,
via l'API gratuite Open-Meteo (aucune cle requise, aucune facturation).
A lancer en local : python fetch_weather.py
"""

import requests
import pandas as pd
import time

# Coordonnees des 8 destinations (memes que le dataset reservations)
DESTINATIONS = {
    "Marrakech":   (31.6295, -7.9811),
    "Agadir":      (30.4278, -9.5981),
    "Chefchaouen": (35.1688, -5.2636),
    "Fes":         (34.0331, -5.0003),
    "Essaouira":   (31.5085, -9.7595),
    "Casablanca":  (33.5731, -7.5898),
    "Tanger":      (35.7595, -5.8340),
    "Merzouga":    (31.0801, -4.0133),
}

START_DATE = "2022-01-01"
END_DATE = "2026-08-01"

BASE_URL = "https://archive-api.open-meteo.com/v1/archive"

all_weather = []

for destination, (lat, lon) in DESTINATIONS.items():
    print(f"Recuperation meteo pour {destination}...")
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto",
    }
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame({
        "date": data["daily"]["time"],
        "temp_max": data["daily"]["temperature_2m_max"],
        "temp_min": data["daily"]["temperature_2m_min"],
        "precipitation": data["daily"]["precipitation_sum"],
    })
    df["destination"] = destination
    all_weather.append(df)

    time.sleep(1)  # pause polie entre les appels

weather_df = pd.concat(all_weather, ignore_index=True)

output_path = "data/raw/weather/weather.csv"
weather_df.to_csv(output_path, index=False)

print(f"\n{len(weather_df)} lignes meteo generees -> {output_path}")
print(weather_df.head())