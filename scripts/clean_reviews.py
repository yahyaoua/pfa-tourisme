from pyspark.sql import SparkSession
from pyspark.sql.functions import col, trim, length, current_timestamp, lower

spark = SparkSession.builder \
    .appName("CleanReviews") \
    .master("spark://spark-master:7077") \
    .config("spark.sql.shuffle.partitions", "4") \
    .getOrCreate()

# 1. Lecture des données brutes
df = spark.read.csv("/data/processed/reviews/*.csv", header=True, inferSchema=True)

# 2. Nettoyage de base
df_clean = (
    df
    .withColumn("Review", trim(col("Review")))
    .filter(col("Review").isNotNull())
    .filter(length(col("Review")) > 10)          # enleve les avis vides/trop courts
    .filter(col("Rating").isNotNull())
    .filter((col("Rating") >= 1) & (col("Rating") <= 5))  # ratings valides seulement
    .dropDuplicates(["Review"])                    # enleve les doublons exacts
)

# 3. Colonnes utiles pour la suite (sentiment, forecasting)
df_clean = (
    df_clean
    .withColumn("review_length", length(col("Review")))
    .withColumn("ingested_at", current_timestamp())
    .withColumnRenamed("Review", "review_text")
    .withColumnRenamed("Rating", "rating")
)

print("=== APERCU DONNEES NETTOYEES ===")
df_clean.show(5, truncate=False)

print("=== NOMBRE DE LIGNES APRES NETTOYAGE ===")
print(df_clean.count())

# 4. Ecriture en zone curated (format Parquet, standard en Big Data)
df_clean.write.mode("overwrite").parquet("/data/curated/reviews")

print("=== ECRITURE TERMINEE : /data/curated/reviews ===")

spark.stop()