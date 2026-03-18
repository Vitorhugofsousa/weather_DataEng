import pandas as pd
import sys, os
from datetime import datetime, timedelta
from airflow.decorators import dag, task
from pathlib import Path
from dotenv import load_dotenv


base_path = Path(__file__).resolve().parent.parent
src_path = (base_path / 'src')
if str(src_path) not in sys.path:
    sys.path.append(str(src_path))

from etl_combined import extract_weather_data, data_transformation, load_data


@dag(
    dag_id="weather_etl_dag1",
    default_args={
        'owner': 'airflow',
        'depends_on_past': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=2),
    },
    description="A DAG to extract, transform and load weather data into a PostgreSQL database",
    schedule='@once',
    start_date=datetime(2026, 3, 18),
    catchup=False,
    tags=['weather', 'etl']
)
def weather_etl_dag():

    @task()
    def extract():
        data_inicio = "2025-12-21"
        data_fim = "2026-03-17"
        return extract_weather_data(data_inicio, data_fim)


    @task()
    def transform(raw_data):
        path_parquet = data_transformation(raw_data)
        return path_parquet

    @task()
    def load(file_path):
        df = pd.read_parquet(file_path)
        db_name = os.getenv('database').strip("'\"")
        load_data(db_name, df)


    dados_brutos = extract()
    path_parquet = transform(dados_brutos)
    load(path_parquet)

weather_etl_dag()