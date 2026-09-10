from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, current_timestamp, datediff

spark = SparkSession.builder \
    .appName("CleanReservations") \
    .master("spark://spark-master:7077") \
    .config("spark.sql.shuffle.partitions", "4") \
    .getOrCreate()

df = spark.read.csv("/data/processed/reservations/*.csv", header=True, inferSchema=True)

df_clean = (
    df
    .withColumn("booking_date", to_date(col("booking_date")))
    .withColumn("travel_date", to_date(col("travel_date")))
    .filter(col("destination").isNotNull())
    .filter(col("total_price") > 0)
    .filter(col("duration_nights") > 0)
    .filter(col("n_travelers") > 0)
    .dropDuplicates(["reservation_id"])
    .withColumn("lead_time_days", datediff(col("travel_date"), col("booking_date")))
    .withColumn("ingested_at", current_timestamp())
)

print("=== APERCU ===")
df_clean.show(5, truncate=False)

print("=== NOMBRE DE LIGNES ===")
print(df_clean.count())

print("=== RESA PAR DESTINATION ===")
df_clean.groupBy("destination").count().orderBy(col("count").desc()).show()

df_clean.write.mode("overwrite").parquet("/data/curated/reservations")

print("=== ECRITURE TERMINEE : /data/curated/reservations ===")

spark.stop()