import streamlit as st
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine


st.set_page_config(page_title="Capitals Weather | Brasil", page_icon="🌤️", layout="wide")
st.title("🌤️ Brazilian Capitals Weather")
st.markdown("interactive Dashboard made with a pipeline in Airflow & Open-Meteo using the data of 25/26 Summer.")

# Data loading function with caching to optimize performance
@st.cache_data(ttl=3600)
def load_data():
    load_dotenv('config/.env')
    user = os.getenv("user")
    password = os.getenv("password")
    database = os.getenv("database")
    host = os.getenv("host")
    
    if host == 'host.docker.internal':
        host = 'localhost'
        
    engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:5432/{database}")
    df = pd.read_sql("SELECT * FROM weather_data", engine)
    df['date'] = pd.to_datetime(df['date'])
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Erro ao conectar no banco de dados: {e}")
    st.stop()

# Displaying key metrics
st.markdown("### 🏆 Summer Records")


idx_min = df['temperature'].idxmin()
idx_max = df['temperature'].idxmax()

cidade_fria = df.loc[idx_min, 'city_name']
temp_fria = df.loc[idx_min, 'temperature']
data_fria = df.loc[idx_min, 'date'].strftime('%d/%m/%Y')

cidade_quente = df.loc[idx_max, 'city_name']
temp_quente = df.loc[idx_max, 'temperature']
data_quente = df.loc[idx_max, 'date'].strftime('%d/%m/%Y')

df_chuva_acumulada = df.groupby('city_name')['precipitation'].sum()
cidade_mais_chuvosa = df_chuva_acumulada.idxmax()
chuva_maxima = df_chuva_acumulada.max()

cidade_mais_seca = df_chuva_acumulada.idxmin()
chuva_minima = df_chuva_acumulada.min()

col1, col2, col3, col4 = st.columns(4)
col1.metric("🥶 Coldest City", f"{temp_fria} °C", f"{cidade_fria} ({data_fria})")
col2.metric("🔥 Hottest City", f"{temp_quente} °C", f"{cidade_quente} ({data_quente})")
col3.metric("🌧️ Most Rainy City", f"{chuva_maxima:.1f} mm", f"{cidade_mais_chuvosa} (Acumulated)")
col4.metric("🏜️ Least Rainy City", f"{chuva_minima:.1f} mm", f"{cidade_mais_seca} (Acumulated)")

st.divider()

col_esquerda, col_direita = st.columns([1, 1.5], gap="medium")

# Ranking by average temperature
with col_esquerda:
    st.markdown("### 📊 Ranking by Average Temp")

    tipo_ranking = st.radio(
        "Toggle Visualization:", 
        ["🔥 Hottest Cities", "❄️ Coldest Cities"], 
        horizontal=True
    )

    df_media_temp = df.groupby('city_name')['temperature'].mean().reset_index()

    if tipo_ranking == "🔥 Hottest Cities":
        df_plot_rank = df_media_temp.sort_values(by='temperature', ascending=False).head(5)
        escala_cor = 'Reds'
    else:
        df_plot_rank = df_media_temp.sort_values(by='temperature', ascending=True).head(5)
        escala_cor = 'Blues'

    fig_bar = px.bar(
        df_plot_rank, 
        x='temperature', 
        y='city_name', 
        orientation='h',
        text_auto='.1f',
        labels={'temperature': 'Avg Temp (°C)', 'city_name': 'Capital'},
        color='temperature',
        color_continuous_scale=escala_cor
    )

    # Reducing margins and adjusting y-axis order based on the ranking type
    fig_bar.update_layout(
        yaxis={'categoryorder':'total ascending' if tipo_ranking == "🔥 Hottest Cities" else 'total descending'},
        height=380, 
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# Comparative between capitals
with col_direita:
    st.markdown("### 🔎 Comparative Between Capitals")

    cidades_disponiveis = sorted(df['city_name'].unique())
    cidades_selecionadas = st.multiselect(
        "Select up to 2 capitals to compare:",
        options=cidades_disponiveis,
        default=["Boa Vista", "Curitiba"],
        max_selections=2
    )

    if not cidades_selecionadas:
        st.warning("Select at least one city to display the comparison.")
    else:
        df_filtrado = df[df['city_name'].isin(cidades_selecionadas)].copy()
        
        df_diario = df_filtrado.groupby(['date', 'city_name']).agg(
            temp_media=('temperature', 'mean'),
            chuva_total=('precipitation', 'sum')
        ).reset_index()

        # Creating tabs for temperature and rainfall visualizations
        tab_temp, tab_chuva = st.tabs(["🌡️ Temperature", "🌧️ Rainfall Volume"])

        with tab_temp:
            fig_line = px.line(
                df_diario, 
                x='date', 
                y='temp_media',
                color='city_name', 
                markers=True,
                labels={'temp_media': 'Daily Avg Temp (°C)', 'date': 'Date', 'city_name': 'Capital'},
            )
            fig_line.update_layout(height=340, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig_line, use_container_width=True)

        with tab_chuva:
            fig_bar_chuva = px.bar(
                df_diario,
                x='date',
                y='chuva_total',
                color='city_name',
                barmode='group', 
                labels={'chuva_total': 'Daily Rain Vol (mm)', 'date': 'Date', 'city_name': 'Capital'},
            )
            fig_bar_chuva.update_layout(height=340, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig_bar_chuva, use_container_width=True)