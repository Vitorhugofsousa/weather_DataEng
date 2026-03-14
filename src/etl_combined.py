# export
##Setup Lines
import requests
import pandas as pd
import json
import logging
from pathlib import Path
import json
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# export
## Extract data function
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_weather_data(url:str) -> list:
    response = requests.get(url)
    data = response.json()


    if response.status_code != 200:
        logging.error(f"Failed to fetch data. Status code: {response.status_code}, Response: {data}")
        return []

    if not data:
        logging.warning("No data found in the response.")
        return []

    output_path = Path("../data/weather_data.json")
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)


    with open(output_path, "w") as f:
        json.dump(data, f, indent=4)
    

    print(f"Data extracted and saved to {output_path}")
    return data



# export
## Transform data functions
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


if "__file__" in globals():
    project_root = Path(__file__).resolve().parent.parent
else: 
    project_root = Path.cwd().parent if Path.cwd().name in ['src', 'notebooks', 'dags'] else Path.cwd()

path_name = project_root / 'data' / 'weather_data.json' 
parquet_path = project_root / 'data' / 'temp_data.parquet' 
path_name.parent.mkdir(parents=True, exist_ok=True)


columns_to_drop = ['weather', 'weather_icon', 'sys.type']
columns_names_to_rename = {
    "base": "base",
    "visibility": "visibility",
    "dt": "datetime",
    "timezone": "timezone",
    "id": "city_id",
    "name": "city_name",
    "cod": "code",
    "coord.lon": "longitude",
    "coord.lat": "latitude",
    "main.temp": "temperature",
    "main.feels_like": "feels_like",
    "main.temp_min": "temp_min",
    "main.temp_max": "temp_max",
    "main.pressure": "pressure",
    "main.humidity": "humidity",
    "main.sea_level": "sea_level",
    "main.grnd_level": "grnd_level",
    "wind.speed": "wind_speed",
    "wind.deg": "wind_deg",
    "wind.gust": "wind_gust",
    "clouds.all": "clouds",
    "sys.type": "sys_type",
    "sys.id": "sys_id",
    "sys.country": "country",
    "sys.sunrise": "sunrise",
    "sys.sunset": "sunset",
}
columns_to_normalize_date = ['datetime', 'sunrise', 'sunset']

def create_dataframe(path_name:str) -> pd.DataFrame:

    logging.info(f"Creating dataframe from {path_name}.json")
    path = path_name

    if not path.exists():
        logging.error(f"File {path} does not exist or is not found.")

    with open(path) as f:
        data = json.load(f)

    df= pd.json_normalize(data)
    logging.info(f"Dataframe created successfully from {path_name}.json")
    return df

def normalize_weather_columns(df: pd.DataFrame) -> pd.DataFrame:
    df_weather = pd.json_normalize(df['weather'].apply(lambda x: x[0]))
    
    df_weather = df_weather.rename(columns={
        'id': 'weather_id',
        'main': 'weather_main',
        'description': 'weather_description',
        'icon': 'weather_icon'
    })

    df = pd.concat([df, df_weather], axis=1)
    logging.info("Weather columns normalized successfully.")
    return df

def drop_columns(df: pd.DataFrame, columns_names:list[str]) -> pd.DataFrame:
    df = df.drop(columns=columns_names)
    logging.info(f"Columns {columns_names} dropped successfully.")
    return df
   
def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns=columns_names_to_rename)
    logging.info("Columns renamed successfully.")
    return df

def normalize_date_columns(df: pd.DataFrame, columns_names:list[str]) -> pd.DataFrame:
    for name in columns_names:
        df[name] = pd.to_datetime(df[name], unit='s', utc=True).dt.tz_convert('America/Sao_Paulo')
    logging.info(f"Date columns {columns_names} normalized successfully.")
    return df


def data_transformation():
    print("Starting data transformation...")
    df = create_dataframe(path_name)
    df = normalize_weather_columns(df) 
    df = drop_columns(df, columns_to_drop)
    df = rename_columns(df)
    df = normalize_date_columns(df, columns_to_normalize_date)
    logging.info("Data transformation completed successfully.")
    return df



# export 
## Load data function
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

     
if "__file__" in globals():
    # Contexto: Script .py (Airflow / Docker)
    project_root = Path(__file__).resolve().parent.parent
else:
    # Contexto: Jupyter Notebook (.ipynb)
    # No notebook, Path.cwd() geralmente é a pasta onde o .ipynb está
    project_root = Path.cwd().parent

# 2. Define o caminho do .env baseado na raiz
env_path = project_root / 'config' / '.env'

# 3. Log de segurança (ajuda muito no Airflow)
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"✅ .env carregado de: {env_path}")
else:
    # Fallback para Docker Airflow (caso a estrutura mude)
    fallback_path = Path('/opt/airflow/config/.env')
    if fallback_path.exists():
        load_dotenv(dotenv_path=fallback_path)
        print(f"✅ .env carregado via Fallback Docker: {fallback_path}")
    else:
        print(f"❌ Erro: Arquivo .env não encontrado em {env_path}")

user = os.getenv("user") or "postgres"
password = str(os.getenv("password") or "")
database = os.getenv("database") or "postgres"
host = os.getenv("host") or "postgres"

def get_engine():
        logging.info(f"Connecting to the database {database} at {host} with user {user}.")
        connection_string = f"postgresql+psycopg2://{user}:{quote_plus(password)}@{host}:5432/{database}"
        return create_engine(connection_string)

engine = get_engine()

def load_data(table_name:str, df):
        df.to_sql(table_name, con=engine, if_exists='append', index=False)
        logging.info(f"Data loaded successfully into the {table_name} table.")
        df_check = pd.read_sql(text(f"SELECT * FROM {table_name}"), con=engine)
        logging.info(f"Data in {table_name} table:{len(df_check)}\n")

print(user, password, database, host)
