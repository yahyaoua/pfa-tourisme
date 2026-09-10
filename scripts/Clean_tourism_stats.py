from pyspark.sql import SparkSession
from pyspark.sql.functions import col, expr

spark = SparkSession.builder \
    .appName("CleanTourismStats") \
    .master("spark://spark-master:7077") \
    .config("spark.sql.shuffle.partitions", "4") \
    .getOrCreate()

df = spark.read.csv("/data/processed/tourism_stats/*.csv", header=True, inferSchema=True)

print("=== SCHEMA BRUT ===")
df.printSchema()

# Transformation format large -> format long (une ligne par destination/annee)
# Adapte la liste des annees si le fichier en contient d'autres (2012 a 2020 ici)
years = [str(y) for y in range(2012, 2021)]
stack_expr = "stack({0}, {1}) as (year, nuitees)".format(
    len(years),
    ", ".join([f"'{y}', `{y}`" for y in years])
)

df_long = df.select(
    col("provinces").alias("destination"),
    expr(stack_expr)
)

print("=== APERCU FORMAT LONG ===")
df_long.show(20)

print("=== NOMBRE DE LIGNES ===")
print(df_long.count())

df_long.write.mode("overwrite").parquet("/data/curated/tourism_stats_officielles")

print("=== ECRITURE TERMINEE : /data/curated/tourism_stats_officielles ===")

spark.stop()