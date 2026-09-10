from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date

spark = SparkSession.builder \
    .appName("CleanWeather") \
    .master("spark://spark-master:7077") \
    .config("spark.sql.shuffle.partitions", "4") \
    .getOrCreate()

df = spark.read.csv("/data/processed/weather/*.csv", header=True, inferSchema=True)

df_clean = (
    df
    .withColumn("date", to_date(col("date")))
    .filter(col("destination").isNotNull())
    .filter(col("temp_max").isNotNull())
    .dropDuplicates(["date", "destination"])
)

print("=== APERCU METEO NETTOYEE ===")
df_clean.show(5)

print("=== NOMBRE DE LIGNES ===")
print(df_clean.count())

df_clean.write.mode("overwrite").parquet("/data/curated/weather")

print("=== ECRITURE TERMINEE : /data/curated/weather ===")

spark.stop()