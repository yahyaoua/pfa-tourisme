from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("InspectReviews") \
    .master("spark://spark-master:7077") \
    .getOrCreate()

# Adapte le chemin si ton fichier a un autre nom
df = spark.read.csv("/data/processed/reviews/*.csv", header=True, inferSchema=True)

print("=== SCHEMA ===")
df.printSchema()

print("=== NOMBRE DE LIGNES ===")
print(df.count())

print("=== 5 PREMIERES LIGNES ===")
df.show(5, truncate=False)

spark.stop()