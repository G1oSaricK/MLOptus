#!/usr/bin/env python3
import argparse
import logging
import sys
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# Настройка логирования для оркестратора (Airflow, Dagster, Prefect)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def parse_args():
    """Парсинг аргументов командной строки."""
    parser = argparse.ArgumentParser(description="PySpark ETL: Параметризованная очистка транзакций")
    parser.add_argument("--input-path", required=True, help="Путь к исходным локальным TXT файлам")
    parser.add_argument("--output-path", required=True, help="Путь для сохранения очищенного Parquet на диске")
    parser.add_argument("--bad-dates", default="", help="Список дат для исключения через запятую (например: 2022-11-24,2022-11-25)")
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Парсим строку с датами в чистый Python-список
    # Очищаем от случайных пробелов. Если пришла пустая строка, список будет пустым []
    bad_dates = [d.strip() for d in args.bad_dates.split(",") if d.strip()]
    
    logger.info("Инициализация локальной Spark-сессии...")
    try:
        spark = SparkSession.builder \
            .appName("Production-Parametrized-ETL") \
            .config("spark.driver.memory", "8g") \
            .config("spark.executor.memory", "8g") \
            .config("spark.sql.parquet.compression.codec", "snappy") \
            .config("spark.sql.sources.partitionOverwriteMode", "dynamic") \
            .getOrCreate()
    except Exception as e:
        logger.error(f"Ошибка при запуске Spark-сессии: {e}")
        sys.exit(1)

    logger.info(f"Шаг 1: Чтение исходных текстовых файлов: {args.input_path}")
    try:
        df_raw = spark.read \
            .format("csv") \
            .option("header", "false") \
            .option("comment", "#") \
            .load(args.input_path) \
            .toDF('transaction_id', 'tx_datetime', 'customer_id', 'terminal_id', 'tx_amount', 
                  'tx_time_seconds', 'tx_time_days', 'tx_fraud', 'tx_fraud_scenario')
    except Exception as e:
        logger.error(f"Ошибка чтения данных: {e}")
        spark.stop()
        sys.exit(1)

    logger.info("Шаг 2: Трансформация типов и очистка аномалий...")
    df_cleaned = df_raw \
        .withColumn("tx_amount", F.col("tx_amount").cast("double")) \
        .withColumn("tx_fraud", F.col("tx_fraud").cast("int")) \
        .withColumn("tx_fraud_scenario", F.col("tx_fraud_scenario").cast("int")) \
        .withColumn("tx_date", F.to_date(F.col("tx_datetime")))

    # Если передан список "плохих" дат, фильтруем их
    if bad_dates:
        logger.info(f"Применяется фильтрация. Будет исключено дней: {len(bad_dates)} ({bad_dates})")
        df_cleaned = df_cleaned.filter(~F.col("tx_date").isin(bad_dates))
    else:
        logger.info("Фильтрация дат пропущена (список bad_dates пуст).")

    # Удаление пропусков в критических полях и исправление аномалий чека
    df_cleaned = df_cleaned \
        .dropna(subset=["transaction_id", "customer_id", "tx_datetime", "tx_date"]) \
        .withColumn("tx_amount", F.when(F.col("tx_amount") < 0, F.abs(F.col("tx_amount")))
                                 .otherwise(F.coalesce(F.col("tx_amount"), F.lit(0.0)))) \
        .fillna({"tx_fraud": 0, "tx_fraud_scenario": 0})

    logger.info(f"Шаг 3: Локальная запись Parquet с партиционированием по датам: {args.output_path}")
    try:
        df_cleaned.write \
            .mode("overwrite") \
            .format("parquet") \
            .option("compression", "snappy") \
            .partitionBy("tx_date") \
            .save(args.output_path)
        logger.info("🚀 Пайплайн успешно завершен! Чистые данные записаны.")
    except Exception as e:
        logger.error(f"Критическая ошибка при записи Parquet на диск: {e}")
        sys.exit(1)
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
