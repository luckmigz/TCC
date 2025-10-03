import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import os
from PIL import Image
import altair as alt
import datetime
from .database import detections_collection, control_collection

st.set_page_config(page_title="YOLO Monitor", layout="wide")
st.title("📡 Dashboard de Monitoramento")

st_autorefresh(interval=10000, key="dashboard_refresh")

OBJETOS_INTERESSE = ['chair', 'dining table', 'person']
IMG_PATH = "frame_mais_recente.jpg"

@st.cache_data(ttl=10)
def carregar_dados():
    ten_minutes_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=10)
    query = {"label": {"$in": OBJETOS_INTERESSE}, "timestamp": {"$gte": ten_minutes_ago}}
    data = list(detections_collection.find(query, {'_id': 0}))
    
    if not data:
        return pd.DataFrame()
        
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

df = carregar_dados()

# Controles na barra lateral
st.sidebar.title("⚙️ Controles do Worker")
is_stopped = control_collection.find_one({"signal": "stop"})

if is_stopped:
    st.sidebar.warning("🚦 Worker de detecção PARADO.")
    if st.sidebar.button("▶️ Iniciar Worker"):
        control_collection.delete_one({"signal": "stop"})
        st.rerun()
else:
    st.sidebar.info("🟢 Worker de detecção ATIVO.")
    if st.sidebar.button("🛑 Parar Worker"):
        control_collection.insert_one({"signal": "stop"})
        st.rerun()

# Layout do Dashboard
if not df.empty:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Detecções (10 min)", len(df))
    col2.metric("🙋‍♂️ Pessoas", len(df[df['label'] == 'person']))
    col3.metric("🪑 Cadeiras", len(df[df['label'] == 'chair']))
    col4.metric("🍽️ Mesas", len(df[df['label'] == 'dining table']))

    col_img, col_chart = st.columns(2)
    with col_img:
        st.subheader("🖼️ Frame mais recente")
        if os.path.exists(IMG_PATH):
            st.image(Image.open(IMG_PATH), use_column_width=True)
        else:
            st.info("Aguardando captura de frame...")
    
    with col_chart:
        st.subheader("⏳ Detecções ao Longo do Tempo")
        df['minuto'] = df['timestamp'].dt.floor('T')
        timeline = df.groupby(['minuto', 'label']).size().reset_index(name='count')
        
        chart = alt.Chart(timeline).mark_line(point=True).encode(
            x='minuto:T', y='count:Q', color='label:N'
        ).interactive()
        st.altair_chart(chart, use_container_width=True)
    
    st.subheader("📜 Dados Recentes")
    st.dataframe(df.sort_values("timestamp", ascending=False))
else:
    st.info("Nenhuma detecção encontrada nos últimos 10 minutos.")