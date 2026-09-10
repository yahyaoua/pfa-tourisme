from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.types import StringType, FloatType
from textblob import TextBlob

spark = SparkSession.builder \
    .appName("SentimentAnalysis") \
    .master("spark://spark-master:7077") \
    .config("spark.sql.shuffle.partitions", "4") \
    .getOrCreate()

# 1. Lecture des donnees nettoyees (etape precedente)
df = spark.read.parquet("/data/curated/reviews")

# 2. Fonctions de sentiment (TextBlob : polarite entre -1 et 1)
def get_polarity(text):
    if text is None:
        return 0.0
    return float(TextBlob(text).sentiment.polarity)

def get_sentiment_label(polarity):
    if polarity > 0.1:
        return "positive"
    elif polarity < -0.1:
        return "negative"
    else:
        return "neutral"

polarity_udf = udf(get_polarity, FloatType())
label_udf = udf(get_sentiment_label, StringType())

# 3. Application sur les avis
df_sentiment = (
    df
    .withColumn("polarity", polarity_udf(col("review_text")))
    .withColumn("sentiment", label_udf(col("polarity")))
)

print("=== APERCU AVEC SENTIMENT ===")
df_sentiment.select("review_text", "rating", "polarity", "sentiment").show(10, truncate=80)

print("=== REPARTITION DES SENTIMENTS ===")
df_sentiment.groupBy("sentiment").count().show()

print("=== SENTIMENT MOYEN PAR RATING (verification coherence) ===")
df_sentiment.groupBy("rating").avg("polarity").orderBy("rating").show()

# 4. Ecriture du resultat
df_sentiment.write.mode("overwrite").parquet("/data/curated/reviews_sentiment")

print("=== ECRITURE TERMINEE : /data/curated/reviews_sentiment ===")

spark.stop()