"""
Prevision de la demande touristique par destination.
Tourne en LOCAL sur le PC (pas dans Docker) - lit directement les fichiers
Parquet generes par Spark dans data/curated/reservations.

Installation prealable :
    pip install pandas pyarrow prophet
"""

import pandas as pd
from prophet import Prophet
import glob

# 1. Lecture des fichiers Parquet (Spark en ecrit plusieurs, on les combine)
parquet_files = glob.glob("data/curated/reservations/*.parquet")
df = pd.concat([pd.read_parquet(f) for f in parquet_files], ignore_index=True)

df["travel_date"] = pd.to_datetime(df["travel_date"])

print(f"{len(df)} reservations chargees.")
print("Destinations :", df["destination"].unique())

# 2. Agregation mensuelle par destination (nombre de reservations = proxy de la demande)
results = {}
forecasts_all = []

for destination in df["destination"].unique():
    df_dest = df[df["destination"] == destination].copy()

    monthly = (
        df_dest
        .set_index("travel_date")
        .resample("MS")  # regroupement par mois (Month Start)
        .size()
        .reset_index(name="y")
        .rename(columns={"travel_date": "ds"})
    )

    if len(monthly) < 6:
        print(f"[{destination}] pas assez de donnees, ignore.")
        continue

    # 3. Entrainement Prophet
    model = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
    model.fit(monthly)

    # 4. Prevision des 6 prochains mois
    future = model.make_future_dataframe(periods=6, freq="MS")
    forecast = model.predict(future)

    forecast_future_only = forecast[forecast["ds"] > monthly["ds"].max()][["ds", "yhat", "yhat_lower", "yhat_upper"]]
    forecast_future_only["destination"] = destination

    print(f"\n=== PREVISION 6 MOIS : {destination} ===")
    print(forecast_future_only.round(1).to_string(index=False))

    forecasts_all.append(forecast_future_only)

# 5. Sauvegarde des previsions (exploitable en Power BI)
final = pd.concat(forecasts_all, ignore_index=True)
final.to_csv("data/curated/demand_forecast.csv", index=False)
print("\n=== ECRITURE TERMINEE : data/curated/demand_forecast.csv ===")