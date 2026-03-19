import pandas as pd
import sys, os
from datetime import datetime, timedelta
from airflow.decorators import dag, task
from pathlib import Path
from airflow.sdk import Param
import logging


base_path = Path(__file__).resolve().parent.parent
src_path = (base_path / 'src')
if str(src_path) not in sys.path:
    sys.path.append(str(src_path))

from etl_combined import extract_weather_data, data_transformation, load_data

# DAG definition
@dag(
    dag_id="weather_etl_dag",
    default_args={
        'owner': 'airflow',
        'retries': 1,
        'retry_delay': timedelta(minutes=2),
    },
    description="A DAG to extract, transform and load weather data into a PostgreSQL database",
    schedule='@once',
    start_date=datetime(2026, 3, 18),
    catchup=False,
    tags=['weather', 'etl'],
    params={
        "start_date": Param("2025-12-21", type="string", format="date", description="Start Date (YYYY-MM-DD)"),
        "end_date": Param("2026-03-17", type="string", format="date", description="End Date (YYYY-MM-DD)"),
        "dry_run": Param(True, type="boolean", description="FOR TESTS ONLY: If True, the DAG will run without loading data into the database")
    }
)
def weather_etl_dag():
    # Load environment variables for database connection
    @task()
    def extract(**kwargs):
        params = kwargs.get('params', {})
        start = params.get('start_date')
        end = params.get('end_date')
        
        logging.info(f"Starting data extraction for the period: {start} to {end}")
        return extract_weather_data(start_date=start, end_date=end)

    # Transform raw data into a structured formatsuitable for loading into the database
    @task()
    def transform(raw_data):
        path_parquet = data_transformation(raw_data)
        return path_parquet
    # Load the transformed data into the PostgreSQL database
    @task()
    def load(file_path, **kwargs):
        params = kwargs.get('params', {})
        is_dry_run = params.get('dry_run', True) # THE SAFE DEFAULT IS DRY RUN, TO AVOID UNINTENTIONAL DATA LOADS DURING TESTS
        
        df = pd.read_parquet(file_path)
        
        if is_dry_run:
            logging.info("⚠️ DRY RUN ACTIVATED: Simulating load to the database...")
            logging.info(f"Data that would be inserted: {len(df)} rows.")
            logging.info("No changes were made to the PostgreSQL database.")
        else:
            logging.info("🚀 PRODUCTION: Starting real load to the database...")
            load_data('weather_data', df)

    # Flow orchestration
    raw = extract()
    parquet = transform(raw)
    load(parquet)

weather_etl_dag()