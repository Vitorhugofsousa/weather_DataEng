import pandas as pd
import sys, os
from datetime import datetime, timedelta
from airflow.sdk import dag, task
from pathlib import Path
from dotenv import load_dotenv

base_path = Path(__file__).resolve().parent.parent
src_path = (base_path / 'src')
if src_path not in sys.path:
    sys.path.append(str(src_path))
from etl_combined import extract_weather_data, data_transformation, load_data # type: ignore

# Try the Relative Path first, then a fixed absolute path for Docker
env_path = Path(__file__).resolve().parent.parent / 'config' / '.env'

if not env_path.exists():
    # Default path where Docker Compose maps the config
    env_path = Path('/opt/airflow/config/.env')

load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv('API_KEY')
url = f"http://api.openweathermap.org/data/2.5/weather?q=Petrolina&units=metric&appid={API_KEY}&units=metric&"

db_user = os.getenv("database")

database = os.getenv('database')


@dag(
    dag_id="weather_etl_dag",
    default_args={
        'owner': 'airflow',
        'depends_on_past': False,
        'retries': 2,
        'retry_delay': timedelta(minutes=5),
    },
    description="A DAG to extract, transform and load weather data into a PostgreSQL database",
    schedule='0 */1 * * *',  # Run every hour
    start_date=datetime(2026, 3, 10),
    catchup=False,
    tags=['weather', 'etl']
)

def weather_etl_dag():
    @task()
    def extract():
         extract_weather_data(url)

    @task()
    def transform():
        df = data_transformation()
        df.to_parquet('/opt/airflow/data/temp_data.parquet', index=False)
        return df

    @task()
    def load():
        df = pd.read_parquet('/opt/airflow/data/temp_data.parquet')
        load_data(database, df)

    extract() >> transform() >> load()

weather_etl_dag()