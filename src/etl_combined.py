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
import time
from dotenv import load_dotenv
from urllib.parse import quote_plus

# export
## Extract data function

CAPITAIS_COORDS = {
    "Rio Branco": {"lat": -9.97499, "lon": -67.8243},
    "Maceió": {"lat": -9.6658, "lon": -35.7353},
    "Macapá": {"lat": 0.0389, "lon": -51.0664},
    "Manaus": {"lat": -3.1019, "lon": -60.0250},
    "Salvador": {"lat": -12.9714, "lon": -38.5014},
    "Fortaleza": {"lat": -3.7172, "lon": -38.5431},
    "Brasília": {"lat": -15.7801, "lon": -47.9292},
    "Vitória": {"lat": -20.3155, "lon": -40.3128},
    "Goiânia": {"lat": -16.6869, "lon": -49.2643},
    "São Luís": {"lat": -2.5297, "lon": -44.3028},
    "Cuiabá": {"lat": -15.6014, "lon": -56.0979},
    "Campo Grande": {"lat": -20.4428, "lon": -54.6464},
    "Belo Horizonte": {"lat": -19.9208, "lon": -43.9378},
    "Belém": {"lat": -1.4558, "lon": -48.5044},
    "João Pessoa": {"lat": -7.1150, "lon": -34.8631},
    "Curitiba": {"lat": -25.4284, "lon": -49.2733},
    "Recife": {"lat": -8.0476, "lon": -34.8770},
    "Teresina": {"lat": -5.0892, "lon": -42.8016},
    "Rio de Janeiro": {"lat": -22.9068, "lon": -43.1729},
    "Natal": {"lat": -5.7945, "lon": -35.2110},
    "Porto Alegre": {"lat": -30.0346, "lon": -51.2177},
    "Porto Velho": {"lat": -8.7612, "lon": -63.9039},
    "Boa Vista": {"lat": 2.8235, "lon": -60.6758},
    "Florianópolis": {"lat": -27.5969, "lon": -48.5495},
    "São Paulo": {"lat": -23.5505, "lon": -46.6333},
    "Aracaju": {"lat": -10.9472, "lon": -37.0731},
    "Palmas": {"lat": -10.2128, "lon": -48.3603}
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_weather_data(start_date="2025-12-21", end_date="2026-03-17"):
    all_weather_data = []
    
    for city, coords in CAPITAIS_COORDS.items():
        try:
            url = (
                f"https://archive-api.open-meteo.com/v1/archive?"
                f"latitude={coords['lat']}&longitude={coords['lon']}&"
                f"start_date={start_date}&end_date={end_date}&"
                f"hourly=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m&"
                f"timezone=America/Sao_Paulo"
            )
            
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                data['city_name'] = city
                all_weather_data.append(data)
                logging.info(f"✅ Historical data extracted successfully: {city} (Lat: {coords['lat']}, Lon: {coords['lon']})")
            else:
                logging.error(f"❌ Error in API for {city}: {response.status_code} - {response.text}")


            time.sleep(1)
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Failure in the network request when trying to extract data from {city}: {e}")
            
    logging.info(f"Extraction finished. Total cities processed: {len(all_weather_data)}")
    return all_weather_data



# export
## Transform data functions
import pandas as pd
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if "__file__" in globals():
    project_root = Path(__file__).resolve().parent.parent
else: 
    project_root = Path.cwd().parent if Path.cwd().name in ['src', 'notebooks', 'dags'] else Path.cwd()


parquet_path = project_root / 'data' / 'temp_data.parquet' 
parquet_path.parent.mkdir(parents=True, exist_ok=True)


def data_transformation(raw_data_list):

    logging.info("Starting data transformation for Open-Meteo...")
    
    lista_dfs = []
    
    
    for city_data in raw_data_list:
        
       
        hourly_data = city_data.get('hourly', {})
        if not hourly_data:
            continue
            
        
        df_cidade = pd.DataFrame(hourly_data)
        
       
        df_cidade['city_name'] = city_data.get('city_name')
        df_cidade['latitude'] = city_data.get('latitude')
        df_cidade['longitude'] = city_data.get('longitude')
        
        lista_dfs.append(df_cidade)
        
    if not lista_dfs:
        logging.error("No valid data to transform.")
        return None
        
    
    df_final = pd.concat(lista_dfs, ignore_index=True)
    
    
    df_final = df_final.rename(columns={
        'time': 'datetime',
        'temperature_2m': 'temperature',
        'relative_humidity_2m': 'humidity',
        'wind_speed_10m': 'wind_speed',
        'precipitation': 'precipitation'
    })
    
    df_final['datetime'] = pd.to_datetime(df_final['datetime'])
    
    df_final['date'] = df_final['datetime'].dt.date
    df_final['time'] = df_final['datetime'].dt.time
    
    
    df_final = df_final.drop(columns=['datetime'])
    
    colunas_ordenadas = [
        'date', 'time', 'temperature', 'humidity', 'precipitation', 
        'wind_speed', 'city_name', 'latitude', 'longitude'
    ]
    df_final = df_final[colunas_ordenadas]
    
    logging.info(f"Data transformation completed successfully! Total rows: {len(df_final)}")
    
    df_final.to_parquet(parquet_path, index=False)
    
    return str(parquet_path)

# export 
## Load data function
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

     
if "__file__" in globals():
    # to run in script
    project_root = Path(__file__).resolve().parent.parent
else:
    # change for notebook
    project_root = Path.cwd().parent

# 2. define .env path based on root
env_path = project_root / 'config' / '.env'

# 3. security log
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"✅ .env loaded from: {env_path}")
else:
    # Fallback path where Docker Compose maps the config
    fallback_path = Path('/opt/airflow/config/.env')
    if fallback_path.exists():
        load_dotenv(dotenv_path=fallback_path)
        print(f"✅ .env loaded by Docker Fallback: {fallback_path}")
    else:
        print(f"❌ Error: .env file does not exist in {env_path}")

user = str(os.getenv("user", "")).strip("'\"") 
password = str(os.getenv("password", "")).strip("'\"")
database = str(os.getenv("database", "")).strip("'\"")
host = str(os.getenv("host", "")).strip("'\"")

def get_engine():
    logging.info(f"Connecting to the database {database} at {host} with user {user}.")
    connection_string = f"postgresql+psycopg2://{user}:{quote_plus(password)}@{host}:5432/{database}"
    return create_engine(connection_string)



def load_data(table_name:str, df):

    engine = get_engine()
    df.to_sql(table_name, con=engine, if_exists='append', index=False)
    logging.info(f"Data loaded successfully into the {table_name} table.")
    with engine.connect() as conn:
        df_check = pd.read_sql(text(f"SELECT COUNT(*) as total FROM {table_name}"), con=conn)
        total_linhas = df_check['total'].iloc[0]
        logging.info(f"📊 Total registries in DB'{table_name}': {total_linhas}\n")

