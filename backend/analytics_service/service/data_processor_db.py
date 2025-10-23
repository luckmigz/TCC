import pandas as pd
from datetime import datetime
from typing import Dict, List, Any
from motor.motor_asyncio import AsyncIOMotorClient
import os

# --- Configurações ---
MONGO_URI = "mongodb+srv://darknnes99:sEnh4d0crl4@usuarios.nvvj4tz.mongodb.net/?retryWrites=true&w=majority&appName=Usuarios"
DB_NAME = "analytics"
COLLECTION_RAW = "raw_detections"

OBJETOS_INTERESSE = ['chair', 'dining table', 'person']
INTERVALO_GRAFICO_MIN = 2 
JANELA_CURTO_PRAZO_MIN = 5 
JANELA_LONGO_PRAZO_MIN = 60 
# ---


# =====================================================
# 🔹 Função utilitária para conexão Mongo
# =====================================================
async def obter_colecao(nome_colecao: str):
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    return db[nome_colecao]


# =====================================================
# 🔹 Busca registros crus do Mongo e converte em DataFrames separados (YOLO / LLaMA)
# =====================================================
async def buscar_dados_mongo_duplo(cnpj: str, limite_minutos: int = 120):
    """
    Busca as detecções recentes no MongoDB (padrão: últimas 2h).
    Retorna dois DataFrames: (df_yolo, df_llama)
    """
    colecao = await obter_colecao(COLLECTION_RAW)
    limite_tempo = datetime.utcnow() - pd.Timedelta(minutes=limite_minutos)

    cursor = colecao.find({
        "cnpj": cnpj,
        "timestamp": {"$gte": limite_tempo}
    })

    docs = await cursor.to_list(length=None)

    if not docs:
        df_vazio = pd.DataFrame(columns=["timestamp", "label"])
        return df_vazio, df_vazio

    registros_yolo = []
    registros_llama = []

    for doc in docs:
        ts = doc.get("timestamp")

        # --- YOLO ---
        for det in doc.get("detections_yolo", []):
            registros_yolo.append({
                "timestamp": ts,
                "label": det.get("label", ""),
                "confidence": det.get("confidence", 0.0)
            })

        # --- LLaMA ---
        visao_llama = doc.get("detections_llama", {})
        for label, contagem in visao_llama.items():
            if isinstance(contagem, (int, float)):
                registros_llama.append({
                    "timestamp": ts,
                    "label": label,
                    "contagem": contagem
                })

    df_yolo = pd.DataFrame(registros_yolo)
    df_llama = pd.DataFrame(registros_llama)

    return df_yolo, df_llama


# =====================================================
# 🔹 Série temporal
# =====================================================
def calcular_serie_temporal(df, label, intervalo_min):
    """Calcula a série temporal de contagem (MAX) para um objeto específico."""
    
    df_obj = df[df['label'] == label].copy()
    if df_obj.empty:
        return []

    df_obj['timestamp'] = pd.to_datetime(df_obj['timestamp'], errors='coerce')
    df_obj['periodo'] = df_obj['timestamp'].dt.floor(f'{intervalo_min}min')
    
    historico = (
        df_obj
        .groupby(['periodo', 'timestamp'])
        .size().reset_index(name='contagem_frame')
        .groupby('periodo')
        .agg(contagem=('contagem_frame', 'max'))
        .reset_index()
        .sort_values('periodo')
    )
    
    return [
        {"timestamp": row['periodo'].strftime('%Y-%m-%d %H:%M:%S'), label.replace(' ', '_'): int(row['contagem'])}
        for _, row in historico.iterrows()
    ]


# =====================================================
# 🔹 Cálculo das métricas YOLO (como antes)
# =====================================================
def calcular_metricas_yolo(df):
    """Calcula todas as métricas em tempo real com base nos dados do YOLO."""
    if df.empty:
        return gerar_metricas_vazias()

    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.dropna(subset=['timestamp'])
    df = df[df['label'].isin(OBJETOS_INTERESSE)]

    ultimo_timestamp = df['timestamp'].max()
    df_atual = df[df['timestamp'] == ultimo_timestamp]

    contagem_atual = df_atual.groupby("label").size().to_dict()
    quantidade_atual = {obj.replace(' ', '_'): contagem_atual.get(obj, 0) for obj in OBJETOS_INTERESSE}

    limite_1h = pd.Timestamp.now() - pd.Timedelta(minutes=JANELA_LONGO_PRAZO_MIN)
    df_recente_1h = df[df['timestamp'] > limite_1h]
    df_pessoas_1h = df_recente_1h[df_recente_1h['label'] == 'person']
    contagem_por_frame_1h = df_pessoas_1h.groupby('timestamp').size().reset_index(name='contagem')

    limite_5min = pd.Timestamp.now() - pd.Timedelta(minutes=JANELA_CURTO_PRAZO_MIN)
    df_pessoas_5min = df[(df['timestamp'] > limite_5min) & (df['label'] == 'person')]
    contagem_por_frame_5min = df_pessoas_5min.groupby('timestamp').size().reset_index(name='contagem')

    media_pessoas_5min = round(contagem_por_frame_5min['contagem'].mean(), 2) if not contagem_por_frame_5min.empty else 0.0
    media_pessoas_1h = round(contagem_por_frame_1h['contagem'].mean(), 2) if not contagem_por_frame_1h.empty else 0.0
    pico_pessoas_1h = int(contagem_por_frame_1h['contagem'].max()) if not contagem_por_frame_1h.empty else 0

    cadeiras = quantidade_atual.get('chair', 0)
    pessoas = quantidade_atual.get('person', 0)
    razao_pessoa_cadeira = round(pessoas / cadeiras, 2) if cadeiras > 0 else ("inf" if pessoas > 0 else 0.0)

    historico_pessoas = calcular_serie_temporal(df, 'person', INTERVALO_GRAFICO_MIN)
    historico_cadeiras = calcular_serie_temporal(df, 'chair', INTERVALO_GRAFICO_MIN)
    historico_mesas = calcular_serie_temporal(df, 'dining table', INTERVALO_GRAFICO_MIN)
    
    return {
        "fonte": "YOLO",
        "quantidade_atual": quantidade_atual,
        "media_pessoas_5min": media_pessoas_5min,
        "media_pessoas_1h": media_pessoas_1h,
        "pico_pessoas_1h": pico_pessoas_1h,
        "razao_pessoa_cadeira": razao_pessoa_cadeira,
        "historico_pessoas_2min": historico_pessoas,
        "historico_cadeiras_2min": historico_cadeiras,
        "historico_mesas_2min": historico_mesas,
        "ultima_atualizacao": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


# =====================================================
# 🔹 Cálculo das métricas LLaMA (baseadas em contagens agregadas)
# =====================================================
def calcular_metricas_llama(df):
    """Calcula métricas de tendência a partir das contagens LLaMA."""
    if df.empty:
        return gerar_metricas_vazias(fonte="LLaMA")

    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.dropna(subset=['timestamp'])
    df = df[df['label'].isin(OBJETOS_INTERESSE)]

    pivot = df.pivot_table(index='timestamp', columns='label', values='contagem', fill_value=0)
    ultimo = pivot.tail(1).to_dict(orient='records')[0] if not pivot.empty else {}

    media_5min = pivot.tail(5).mean().to_dict() if len(pivot) >= 5 else pivot.mean().to_dict()
    media_1h = pivot.mean().to_dict()

    razao_pessoa_cadeira = 0.0
    if "chair" in ultimo and "person" in ultimo:
        c = ultimo["chair"]
        p = ultimo["person"]
        razao_pessoa_cadeira = round(p / c, 2) if c > 0 else ("inf" if p > 0 else 0.0)

    return {
        "fonte": "LLaMA",
        "quantidade_atual": {k.replace(' ', '_'): int(v) for k, v in ultimo.items()},
        "media_5min": {k.replace(' ', '_'): round(v, 2) for k, v in media_5min.items()},
        "media_1h": {k.replace(' ', '_'): round(v, 2) for k, v in media_1h.items()},
        "razao_pessoa_cadeira": razao_pessoa_cadeira,
        "ultima_atualizacao": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


# =====================================================
# 🔹 Métricas padrão vazias
# =====================================================
def gerar_metricas_vazias(fonte: str = "YOLO"):
    return {
        "fonte": fonte,
        "quantidade_atual": {"person": 0, "chair": 0, "dining_table": 0},
        "media_pessoas_5min": 0.0,
        "media_pessoas_1h": 0.0,
        "pico_pessoas_1h": 0,
        "razao_pessoa_cadeira": 0.0,
        "historico_pessoas_2min": [],
        "historico_cadeiras_2min": [],
        "historico_mesas_2min": [],
        "ultima_atualizacao": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


# =====================================================
# 🔹 Pipeline completo: YOLO + LLaMA
# =====================================================
async def gerar_analises_duplas(cnpj: str) -> Dict[str, Any]:
    """
    Busca dados no Mongo e gera duas análises separadas:
    - YOLO: baseada em detections_yolo
    - LLaMA: baseada em detections_llama
    """
    df_yolo, df_llama = await buscar_dados_mongo_duplo(cnpj)
    analise_yolo = calcular_metricas_yolo(df_yolo)
    analise_llama = calcular_metricas_llama(df_llama)
    return {
        "yolo_analysis": analise_yolo,
        "llama_analysis": analise_llama
    }
