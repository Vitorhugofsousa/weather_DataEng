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


env_path = Path(__file__).resolve().parent.parent / 'config' / '.env'
if not env_path.exists():
    env_path = Path('/opt/airflow/config/.env')
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv('API_KEY')
url = f"http://api.openweathermap.org/data/2.5/weather?q=Petrolina&units=metric&appid={API_KEY}"

@dag(
    dag_id="weather_etl_dag",
    default_args={
        'owner': 'airflow',
        'depends_on_past': False,
        'retries': 2,
        'retry_delay': timedelta(minutes=5),
    },
    description="A DAG to extract, transform and load weather data into a PostgreSQL database",
    schedule='0 */1 * * *',
    start_date=datetime(2026, 3, 10),
    catchup=False,
    tags=['weather', 'etl']
)
def weather_etl_dag():

    @task()
    def extract():
         return extract_weather_data(url)

    @task()
    def transform(raw_data):
        df = data_transformation(raw_data)
        
        temp_path = '/opt/airflow/data/temp_data.parquet'
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        df.to_parquet(temp_path, index=False)
        return temp_path 

    @task()
    def load(file_path):
        df = pd.read_parquet(file_path)
        db_name = os.getenv('database').strip("'\"")
        load_data(db_name, df)


    dados_brutos = extract()
    caminho_parquet = transform(dados_brutos)
    load(caminho_parquet)

weather_etl_dag()