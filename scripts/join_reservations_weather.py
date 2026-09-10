from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg

spark = SparkSession.builder \
    .appName("JoinReservationsWeather") \
    .master("spark://spark-master:7077") \
    .config("spark.sql.shuffle.partitions", "4") \
    .getOrCreate()

reservations = spark.read.parquet("/data/curated/reservations")
weather = spark.read.parquet("/data/curated/weather")

# Jointure : la meteo du jour du voyage, pour la destination concernee
enriched = reservations.join(
    weather,
    (reservations.destination == weather.destination) &
    (reservations.travel_date == weather.date),
    how="left"
).select(
    reservations["*"],
    weather["temp_max"],
    weather["temp_min"],
    weather["precipitation"]
)

print("=== APERCU RESERVATIONS + METEO ===")
enriched.show(5)

print("=== TAUX DE JOINTURE REUSSIE ===")
total = enriched.count()
matched = enriched.filter(col("temp_max").isNotNull()).count()
print(f"{matched}/{total} reservations avec meteo correspondante ({100*matched/total:.1f}%)")

print("=== TEMPERATURE MOYENNE PAR DESTINATION (jour de voyage) ===")
enriched.groupBy("destination").agg(avg("temp_max").alias("temp_moyenne")).orderBy("destination").show()

enriched.write.mode("overwrite").parquet("/data/curated/reservations_weather")

print("=== ECRITURE TERMINEE : /data/curated/reservations_weather ===")

spark.stop()