import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import os
from PIL import Image
import cv2
import numpy as np
import altair as alt


# Configurações
CSV_PATH = "detecoes.csv"
IMG_PATH = "frame_mais_recente.jpg"
IMG_W, IMG_H = 640, 360
OBJETOS_INTERESSE = ['chair', 'dining table', 'person']

st.set_page_config(page_title="YOLO Monitor", layout="wide")
st.title("📡 Monitor de Detecções YOLO")

# 🔄 Atualiza automaticamente a cada 5 segundos
st_autorefresh(interval=5000, key="auto-refresh")

# Função para carregar dados
@st.cache_data(ttl=5)
def carregar_dados():
    if not os.path.exists(CSV_PATH):
        return pd.DataFrame()


    df = pd.read_csv(CSV_PATH)

    # Conversões
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.dropna(subset=['timestamp'])

    df['label'] = df['label'].astype(str).str.strip().str.lower()
    df = df[df['label'].isin(OBJETOS_INTERESSE)]
    df = df[df['timestamp'] > pd.Timestamp.now() - pd.Timedelta(minutes=5)]

    return df

# Carrega dados
df = carregar_dados()


STOP_FLAG = "stop.flag"

st.sidebar.title("⚙️ Controles")
if not os.path.exists(STOP_FLAG):
    if st.sidebar.button("🛑 Parar Detecção"):
        open(STOP_FLAG, "w").close()
        st.sidebar.success("Detecção será encerrada em instantes.")
else:
    st.sidebar.info("🚦 Detecção PARADA")

# Se a detecção já parou, mostra resumo
if os.path.exists(STOP_FLAG):
    st.subheader("📊 Resumo das Detecções")

    if not df.empty:
        # --- Contagem por objeto ---
        resumo = df.groupby("label").size().reset_index(name="quantidade")
        st.markdown("#### 🔍 Detecções por Categoria")
        st.bar_chart(resumo.set_index("label"))

        # --- Timeline ---
        st.markdown("#### ⏳ Detecções ao Longo do Tempo")
        df['minuto'] = df['timestamp'].dt.floor('min')  # agrupa por minuto
        timeline = df.groupby(['minuto', 'label']).size().reset_index(name='count')

        chart = (
            alt.Chart(timeline)
            .mark_line(point=True)
            .encode(
                x='minuto:T',
                y='count:Q',
                color='label:N',
                tooltip=['minuto:T', 'label:N', 'count:Q']
            )
            .properties(width=800, height=400)
            .interactive()
        )
        st.altair_chart(chart, use_container_width=True)

        # --- Tabela final ---
        st.markdown("#### 📜 Tabela Completa")
        st.dataframe(df.sort_values("timestamp", ascending=False))
    else:
        st.info("Nenhuma detecção registrada.")



# Indicadores
col1, col2, col3, col4 = st.columns(4)
col1.metric("📦 Total de Detecções", len(df))
col2.metric("🙋‍♂️ Pessoas", len(df[df['label'] == 'person']))
col3.metric("🪑 Cadeiras", len(df[df['label'] == 'chair']))
col4.metric("🍽️ Mesas", len(df[df['label'] == 'dining table']))

# Mostra imagem mais recente
st.subheader("🖼️ Frame mais recente")
if os.path.exists(IMG_PATH):
    imagem = Image.open(IMG_PATH)
    st.image(imagem, caption="Imagem da Câmera", width=500)
else:
    st.info("Aguardando captura da câmera...")
