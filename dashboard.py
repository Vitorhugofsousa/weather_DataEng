import streamlit as st
import pandas as pd
import psycopg2
from pathlib import Path
from dotenv import load_dotenv
import os
import warnings

# Ignora o aviso do pandas sobre sqlalchemy
warnings.filterwarnings("ignore", category=UserWarning)

st.set_page_config(page_title="Petrolina Weather Dashboard", layout="wide")
st.title("☀️ Petrolina Real-Time Weather")

# Carregamento de Variáveis
project_root = Path(__file__).parent
env_path = project_root / 'config' / '.env'
load_dotenv(env_path)

host = "localhost"
port = os.getenv("port")
user = os.getenv("user")
password = os.getenv("password")
database = os.getenv("database")

def get_connection():
    return psycopg2.connect(
        host=host, port=port, database=database, user=user, password=password
    )

print(f"Conectando ao banco de dados em {database}:{port} com usuário {user}...")

try:
    conn = get_connection()
    query = "SELECT * FROM weather_data ORDER BY datetime DESC LIMIT 100"
    df = pd.read_sql(query, conn)
    conn.close()
    
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        latest = df.iloc[0]
        col1.metric("Temperatura", f"{latest['temperature']}°C")
        col2.metric("Umidade", f"{latest['humidity']}%")
        col3.metric("Data", f"{latest['datetime']}")
        st.line_chart(df.set_index('datetime')[['temperature']])
    else:
        st.warning("Tabela encontrada, mas sem dados.")

except Exception as e:
    if "does not exist" in str(e):
        st.error("A tabela 'weather_data' ainda não foi criada no banco.")
        st.info("👉 **Ação necessária:** Rode o script `python src/etl_combined.py` para criar a tabela e inserir os primeiros dados.")
    else:
        st.error(f"Erro: {e}")