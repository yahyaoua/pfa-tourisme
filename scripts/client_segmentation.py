from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count, sum as spark_sum
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans

spark = SparkSession.builder \
    .appName("ClientSegmentation") \
    .master("spark://spark-master:7077") \
    .config("spark.sql.shuffle.partitions", "4") \
    .getOrCreate()

df = spark.read.parquet("/data/curated/reservations")

# 1. Agrege le comportement par client (un client = plusieurs reservations)
client_profile = df.groupBy("client_id").agg(
    count("reservation_id").alias("nb_reservations"),
    avg("total_price").alias("avg_spend"),
    avg("duration_nights").alias("avg_duration"),
    avg("lead_time_days").alias("avg_lead_time"),
    avg("n_travelers").alias("avg_travelers")
)

print("=== PROFIL CLIENT (agrege) ===")
client_profile.show(5)

# 2. Prepare les features pour KMeans
feature_cols = ["nb_reservations", "avg_spend", "avg_duration", "avg_lead_time", "avg_travelers"]
assembler = VectorAssembler(inputCols=feature_cols, outputCol="features_raw")
df_features = assembler.transform(client_profile)

scaler = StandardScaler(inputCol="features_raw", outputCol="features", withStd=True, withMean=True)
df_scaled = scaler.fit(df_features).transform(df_features)

# 3. KMeans avec 4 segments (voyageur economique, familial, premium, frequent)
kmeans = KMeans(k=4, seed=42, featuresCol="features", predictionCol="segment")
model = kmeans.fit(df_scaled)
df_result = model.transform(df_scaled)

print("=== TAILLE DES SEGMENTS ===")
df_result.groupBy("segment").count().orderBy("segment").show()

print("=== PROFIL MOYEN PAR SEGMENT (pour interpretation) ===")
df_result.groupBy("segment").agg(
    avg("nb_reservations").alias("avg_nb_reservations"),
    avg("avg_spend").alias("avg_spend"),
    avg("avg_duration").alias("avg_duration"),
    avg("avg_lead_time").alias("avg_lead_time"),
    avg("avg_travelers").alias("avg_travelers")
).orderBy("segment").show()

# 4. Ecriture du resultat (client_id + segment, exploitable directement en Power BI)
output = df_result.select("client_id", "nb_reservations", "avg_spend", "avg_duration",
                           "avg_lead_time", "avg_travelers", "segment")
output.write.mode("overwrite").parquet("/data/curated/client_segments")

print("=== ECRITURE TERMINEE : /data/curated/client_segments ===")

spark.stop()