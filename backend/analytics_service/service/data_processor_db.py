import pandas as pd
from datetime import datetime
from typing import Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
import os

# --- Configurações ---
MONGO_URI = "mongodb+srv://darknnes99:sEnh4d0crl4@usuarios.nvvj4tz.mongodb.net/?retryWrites=true&w=majority&appName=Usuarios"
DB_NAME = "analytics"
COLLECTION_RAW = "raw_detections"

OBJETOS_INTERESSE = [
    'chair', 'chairs',
    'dining table', 'dining_table', 'table',
    'person', 'people'
]

INTERVALO_GRAFICO_MIN = 2
JANELA_CURTO_PRAZO_MIN = 5
JANELA_LONGO_PRAZO_MIN = 60
# ---


# =====================================================
# 🔹 Conexão Mongo
# =====================================================
async def obter_colecao(nome_colecao: str):
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    return db[nome_colecao]


# =====================================================
# 🔹 Busca e separação dos dados YOLO / LLaMA
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
            label = det.get("label", "").replace("_", " ").lower()
            registros_yolo.append({
                "timestamp": ts,
                "label": label,
                "confidence": det.get("confidence", 0.0)
            })

        # --- LLaMA ---
        visao_llama = doc.get("detections_llama", {})

        # Pode ser dict ou lista
        if isinstance(visao_llama, dict):
            for label, contagem in visao_llama.items():
                if isinstance(contagem, (int, float)):
                    registros_llama.append({
                        "timestamp": ts,
                        "label": label.replace("_", " ").lower(),
                        "contagem": contagem
                    })
        elif isinstance(visao_llama, list):
            for item in visao_llama:
                label = str(item.get("label", "")).replace("_", " ").lower()
                contagem = item.get("count") or item.get("contagem") or 0
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
    if df.empty:
        return []

    df_obj = df[df['label'] == label].copy()
    if df_obj.empty:
        return []

    df_obj['timestamp'] = pd.to_datetime(df_obj['timestamp'], utc=True, errors='coerce')
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
# 🔹 Métricas YOLO
# =====================================================
def calcular_metricas_yolo(df):
    """Calcula métricas em tempo real com base nos dados YOLO."""
    if df.empty:
        return gerar_metricas_vazias()

    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True, errors='coerce')
    df = df.dropna(subset=['timestamp'])
    df['label'] = df['label'].str.replace('_', ' ').str.lower()
    df = df[df['label'].isin(OBJETOS_INTERESSE)]

    if df.empty:
        return gerar_metricas_vazias()

    # Agrupamento por minuto para evitar variações de milissegundos
    df['timestamp_min'] = df['timestamp'].dt.floor('1min')
    ultimo_timestamp = df['timestamp_min'].max()
    df_atual = df[df['timestamp_min'] == ultimo_timestamp]

    contagem_atual = df_atual.groupby("label").size().to_dict()
    quantidade_atual = {obj.replace(' ', '_'): int(contagem_atual.get(obj, 0)) for obj in OBJETOS_INTERESSE}

    # Usar UTC para consistência
    limite_1h = pd.Timestamp.utcnow() - pd.Timedelta(minutes=JANELA_LONGO_PRAZO_MIN)
    limite_5min = pd.Timestamp.utcnow() - pd.Timedelta(minutes=JANELA_CURTO_PRAZO_MIN)

    # Cálculo das médias e picos
    df_pessoas_1h = df[(df['timestamp'] > limite_1h) & (df['label'] == 'person')]
    df_pessoas_5min = df[(df['timestamp'] > limite_5min) & (df['label'] == 'person')]

    contagem_por_frame_1h = df_pessoas_1h.groupby('timestamp_min').size().reset_index(name='contagem')
    contagem_por_frame_5min = df_pessoas_5min.groupby('timestamp_min').size().reset_index(name='contagem')

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
        "ultima_atualizacao": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    }


# =====================================================
# 🔹 Métricas LLaMA
# =====================================================
def calcular_metricas_llama(df):
    """Calcula métricas de tendência com base nas contagens LLaMA."""
    if df.empty:
        return gerar_metricas_vazias(fonte="LLaMA")

    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True, errors='coerce')
    df = df.dropna(subset=['timestamp'])
    df['label'] = df['label'].str.replace('_', ' ').str.lower()
    df = df[df['label'].isin(OBJETOS_INTERESSE)]

    if df.empty:
        return gerar_metricas_vazias(fonte="LLaMA")

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
        "ultima_atualizacao": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
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
        "ultima_atualizacao": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
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
