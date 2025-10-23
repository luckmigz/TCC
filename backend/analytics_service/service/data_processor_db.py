import pandas as pd
from datetime import datetime
from typing import Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient

# --- Configurações ---
MONGO_URI = "mongodb+srv://darknnes99:sEnh4d0crl4@usuarios.nvvj4tz.mongodb.net/?retryWrites=true&w=majority&appName=Usuarios"
DB_NAME = "analytics"
COLLECTION_RAW = "raw_detections"

OBJETOS_INTERESSE = ["chair", "dining table", "person"]
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
# 🔹 Funções auxiliares de conversão BSON → Python
# =====================================================
def converter_valor_bson(valor):
    """Converte tipos {'$numberInt': '3'} ou {'$numberDouble': '0.5'} em int/float."""
    if isinstance(valor, dict):
        if "$numberInt" in valor:
            return int(valor["$numberInt"])
        if "$numberDouble" in valor:
            return float(valor["$numberDouble"])
        if "$numberLong" in valor:
            return int(valor["$numberLong"])
    return valor


def converter_timestamp_bson(ts_raw):
    """Converte {'$date': {'$numberLong': '1761190423439'}} → datetime UTC."""
    if isinstance(ts_raw, dict) and "$date" in ts_raw:
        inner = ts_raw["$date"]
        if isinstance(inner, dict) and "$numberLong" in inner:
            millis = int(inner["$numberLong"])
            return datetime.utcfromtimestamp(millis / 1000.0)
    return pd.to_datetime(ts_raw, utc=True, errors="coerce")


# =====================================================
# 🔹 Busca dados YOLO / LLaMA no Mongo (sem filtro de tempo)
# =====================================================
async def buscar_dados_mongo_duplo(cnpj: str, limite_minutos: int = 120):
    """
    Busca todas as detecções no MongoDB filtrando apenas pelo CNPJ.
    Retorna dois DataFrames: (df_yolo, df_llama)
    """
    colecao = await obter_colecao(COLLECTION_RAW)

    cursor = colecao.find({
        "$or": [{"cnpj": cnpj}, {"CNPJ": cnpj}]
    })

    docs = await cursor.to_list(length=None)

    if not docs:
        df_vazio = pd.DataFrame(columns=["timestamp", "label"])
        return df_vazio, df_vazio

    registros_yolo, registros_llama = [], []

    for doc in docs:
        ts = converter_timestamp_bson(doc.get("timestamp"))

        # --- YOLO ---
        for det in doc.get("detections_yolo", []):
            label = str(det.get("label", "")).replace("_", " ").lower()
            conf = converter_valor_bson(det.get("confidence", 0))
            registros_yolo.append({
                "timestamp": ts,
                "label": label,
                "confidence": conf
            })

        # --- LLaMA ---
        visao_llama = doc.get("detections_llama", {})
        if isinstance(visao_llama, dict):
            for label, valor in visao_llama.items():
                contagem = converter_valor_bson(valor)
                if isinstance(contagem, (int, float)):
                    registros_llama.append({
                        "timestamp": ts,
                        "label": label.replace("_", " ").lower(),
                        "contagem": contagem
                    })

    df_yolo = pd.DataFrame(registros_yolo)
    df_llama = pd.DataFrame(registros_llama)
    return df_yolo, df_llama


# =====================================================
# 🔹 Série temporal
# =====================================================
def calcular_serie_temporal(df, label, intervalo_min):
    if df.empty:
        return []
    df = df[df["label"] == label].copy()
    if df.empty:
        return []

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df["periodo"] = df["timestamp"].dt.floor(f"{intervalo_min}min")

    hist = (
        df.groupby(["periodo", "timestamp"])
        .size()
        .reset_index(name="contagem_frame")
        .groupby("periodo")["contagem_frame"]
        .max()
        .reset_index()
    )

    return [
        {
            "timestamp": row["periodo"].strftime("%Y-%m-%d %H:%M:%S"),
            label.replace(" ", "_"): int(row["contagem_frame"]),
        }
        for _, row in hist.iterrows()
    ]


# =====================================================
# 🔹 Métricas YOLO
# =====================================================
def calcular_metricas_yolo(df):
    if df.empty:
        return gerar_metricas_vazias()

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df["label"] = df["label"].str.replace("_", " ").str.lower()
    df = df[df["label"].isin(OBJETOS_INTERESSE)]

    if df.empty:
        return gerar_metricas_vazias()

    df["timestamp_min"] = df["timestamp"].dt.floor("1min")
    ultimo_timestamp = df["timestamp_min"].max()
    df_atual = df[df["timestamp_min"] == ultimo_timestamp]

    contagem_atual = df_atual.groupby("label").size().to_dict()
    quantidade_atual = {obj.replace(" ", "_"): contagem_atual.get(obj, 0) for obj in OBJETOS_INTERESSE}

    limite_1h = pd.Timestamp.utcnow() - pd.Timedelta(minutes=JANELA_LONGO_PRAZO_MIN)
    limite_5min = pd.Timestamp.utcnow() - pd.Timedelta(minutes=JANELA_CURTO_PRAZO_MIN)

    df_pessoas_1h = df[(df["timestamp"] > limite_1h) & (df["label"] == "person")]
    df_pessoas_5min = df[(df["timestamp"] > limite_5min) & (df["label"] == "person")]

    contagem_por_frame_1h = df_pessoas_1h.groupby("timestamp_min").size()
    contagem_por_frame_5min = df_pessoas_5min.groupby("timestamp_min").size()

    media_pessoas_5min = round(contagem_por_frame_5min.mean(), 2) if not contagem_por_frame_5min.empty else 0.0
    media_pessoas_1h = round(contagem_por_frame_1h.mean(), 2) if not contagem_por_frame_1h.empty else 0.0
    pico_pessoas_1h = int(contagem_por_frame_1h.max()) if not contagem_por_frame_1h.empty else 0

    cadeiras = quantidade_atual.get("chair", 0)
    pessoas = quantidade_atual.get("person", 0)
    razao_pessoa_cadeira = round(pessoas / cadeiras, 2) if cadeiras > 0 else ("inf" if pessoas > 0 else 0.0)

    historico_pessoas = calcular_serie_temporal(df, "person", INTERVALO_GRAFICO_MIN)
    historico_cadeiras = calcular_serie_temporal(df, "chair", INTERVALO_GRAFICO_MIN)
    historico_mesas = calcular_serie_temporal(df, "dining table", INTERVALO_GRAFICO_MIN)

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
        "ultima_atualizacao": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
    }


# =====================================================
# 🔹 Métricas LLaMA
# =====================================================
def calcular_metricas_llama(df):
    if df.empty:
        return gerar_metricas_vazias(fonte="LLaMA")

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df["label"] = df["label"].str.replace("_", " ").str.lower()
    df = df[df["label"].isin(OBJETOS_INTERESSE)]

    if df.empty:
        return gerar_metricas_vazias(fonte="LLaMA")

    pivot = df.pivot_table(index="timestamp", columns="label", values="contagem", fill_value=0)
    ultimo = pivot.tail(1).to_dict(orient="records")[0] if not pivot.empty else {}
    media_5min = pivot.tail(5).mean().to_dict() if len(pivot) >= 5 else pivot.mean().to_dict()
    media_1h = pivot.mean().to_dict()

    razao_pessoa_cadeira = 0.0
    if "chair" in ultimo and "person" in ultimo:
        c = ultimo["chair"]
        p = ultimo["person"]
        razao_pessoa_cadeira = round(p / c, 2) if c > 0 else ("inf" if p > 0 else 0.0)

    return {
        "fonte": "LLaMA",
        "quantidade_atual": {k.replace(" ", "_"): int(v) for k, v in ultimo.items()},
        "media_5min": {k.replace(" ", "_"): round(v, 2) for k, v in media_5min.items()},
        "media_1h": {k.replace(" ", "_"): round(v, 2) for k, v in media_1h.items()},
        "razao_pessoa_cadeira": razao_pessoa_cadeira,
        "ultima_atualizacao": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
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
        "ultima_atualizacao": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
    }


# =====================================================
# 🔹 Pipeline completo
# =====================================================
async def gerar_analises_duplas(cnpj: str) -> Dict[str, Any]:
    df_yolo, df_llama = await buscar_dados_mongo_duplo(cnpj)
    analise_yolo = calcular_metricas_yolo(df_yolo)
    analise_llama = calcular_metricas_llama(df_llama)
    return {"yolo_analysis": analise_yolo, "llama_analysis": analise_llama}
