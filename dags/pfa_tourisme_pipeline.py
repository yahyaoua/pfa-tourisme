
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

SPARK_SUBMIT = "docker exec spark-master /opt/spark/bin/spark-submit --driver-memory 512m --executor-memory 512m --total-executor-cores 1"

with DAG(
    dag_id="pfa_tourisme_pipeline",
    description="Pipeline Big Data tourisme : nettoyage + IA",
    start_date=datetime(2026, 8, 1),
    schedule_interval="@daily",
    catchup=False,
) as dag:

    clean_reservations = BashOperator(
        task_id="clean_reservations",
        bash_command=f"{SPARK_SUBMIT} /scripts/clean_reservations.py",
    )

    client_segmentation = BashOperator(
        task_id="client_segmentation",
        bash_command=f"{SPARK_SUBMIT} /scripts/client_segmentation.py",
    )

    clean_reviews = BashOperator(
        task_id="clean_reviews",
        bash_command=f"{SPARK_SUBMIT} /scripts/clean_reviews.py",
    )

    sentiment_analysis = BashOperator(
        task_id="sentiment_analysis",
        bash_command=f"{SPARK_SUBMIT} /scripts/sentiment_analysis.py",
    )

    # Reservations -> segmentation (dependance logique)
    clean_reservations >> client_segmentation

    # Reviews -> sentiment (dependance logique)
    clean_reviews >> sentiment_analysis