import re
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorClient

# --- Configurações ---
MONGO_URI = "mongodb+srv://darknnes99:sEnh4d0crl4@usuarios.nvvj4tz.mongodb.net/?retryWrites=true&w=majority&appName=Usuarios"
DB_NAME = "analytics"
COLLECTION_RAW = "raw_detections"

OBJETOS_INTERESSE = ["chair", "dining table", "person"]
INTERVALO_GRAFICO_MIN = 2
# ---


# =====================================================
# 🔹 Conexão Mongo
# =====================================================
async def obter_colecao(nome_colecao: str):
    client = AsyncIOMotorClient(MONGO_URI)
    db = client["Usuarios"]
    return db[nome_colecao]


# =====================================================
# 🔹 Funções auxiliares
# =====================================================
def normalizar_cnpj(valor: str) -> str:
    if valor is None:
        return ""
    return re.sub(r"\D", "", str(valor)).strip()


def converter_valor_bson(valor):
    if isinstance(valor, dict):
        if "$numberInt" in valor:
            return int(valor["$numberInt"])
        if "$numberDouble" in valor:
            return float(valor["$numberDouble"])
        if "$numberLong" in valor:
            return int(valor["$numberLong"])
    return valor


def converter_timestamp_bson(ts_raw):
    if isinstance(ts_raw, dict) and "$date" in ts_raw:
        inner = ts_raw["$date"]
        if isinstance(inner, dict) and "$numberLong" in inner:
            millis = int(inner["$numberLong"])
            return datetime.utcfromtimestamp(millis / 1000.0)
        if isinstance(inner, str):
            return pd.to_datetime(inner, utc=True, errors="coerce")
    return pd.to_datetime(ts_raw, utc=True, errors="coerce")


# =====================================================
# 🔹 Descoberta de CNPJs existentes (para fallback)
# =====================================================
async def _listar_cnpjs_existentes(colecao, limite: int = 500) -> List[str]:
    cursor = colecao.find(
        {"$or": [{"cnpj": {"$exists": True}}, {"CNPJ": {"$exists": True}}]},
        {"cnpj": 1, "CNPJ": 1},
        limit=limite,
    )
    docs = await cursor.to_list(length=limite)
    valores = []
    for doc in docs:
        if "cnpj" in doc and doc["cnpj"] is not None:
            valores.append(str(doc["cnpj"]))
        if "CNPJ" in doc and doc["CNPJ"] is not None:
            valores.append(str(doc["CNPJ"]))
    seen = set()
    uniq = []
    for v in valores:
        if v not in seen:
            uniq.append(v)
            seen.add(v)
    return uniq


# =====================================================
# 🔹 Busca dados YOLO / LLaMA
# =====================================================
async def buscar_dados_mongo_duplo(cnpj: str):
    colecao = await obter_colecao(COLLECTION_RAW)

    cnpj_limpo = normalizar_cnpj(cnpj)
    base_or = [
        {"cnpj": cnpj_limpo},
        {"CNPJ": cnpj_limpo},
    ]
    if cnpj_limpo.isdigit():
        base_or.extend([
            {"cnpj": int(cnpj_limpo)},
            {"CNPJ": int(cnpj_limpo)},
        ])

    query = {"$or": base_or}
    cursor = colecao.find(query)
    docs = await cursor.to_list(length=None)

    if not docs:
        existentes = await _listar_cnpjs_existentes(colecao, limite=500)
        existentes_norm = [(orig, normalizar_cnpj(orig)) for orig in existentes]
        candidatos_reais = [orig for (orig, norm) in existentes_norm if norm == cnpj_limpo]

        if candidatos_reais:
            query2 = {"$or": [{"cnpj": {"$in": candidatos_reais}},
                              {"CNPJ": {"$in": candidatos_reais}}]}
            cursor2 = colecao.find(query2)
            docs = await cursor2.to_list(length=None)

    if not docs:
        df_vazio = pd.DataFrame(columns=["timestamp", "label"])
        return df_vazio, df_vazio

    registros_yolo, registros_llama = [], []

    for doc in docs:
        ts = converter_timestamp_bson(doc.get("timestamp"))

        # YOLO
        for det in doc.get("detections_yolo", []):
            label = str(det.get("label", "")).replace("_", " ").lower()
            conf = converter_valor_bson(det.get("confidence", 0))
            registros_yolo.append({
                "timestamp": ts,
                "label": label,
                "confidence": conf
            })

        # LLaMA
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

    return pd.DataFrame(registros_yolo), pd.DataFrame(registros_llama)


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
        return gerar_metricas_vazias("YOLO")

    # Normalização
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df["label"] = df["label"].str.replace("_", " ").str.lower()
    df = df[df["label"].isin(OBJETOS_INTERESSE)]
    if df.empty:
        return gerar_metricas_vazias("YOLO")

    # 🔹 Quantidade atual = contagem no ÚLTIMO FRAME
    ultimo_ts = df["timestamp"].max()
    df_atual = df[df["timestamp"] == ultimo_ts]
    contagem_atual = df_atual.groupby("label").size().to_dict()
    quantidade_atual = {obj.replace(" ", "_"): int(contagem_atual.get(obj, 0)) for obj in OBJETOS_INTERESSE}

    # 🔹 Métricas corretas por FRAME (não por minuto)
    #   - contagem de pessoas em cada frame
    df_pessoas = df[df["label"] == "person"].copy()
    contagem_por_frame = (
        df_pessoas.groupby("timestamp").size()  # cada linha = nº de pessoas naquele frame
    )

    media_total = round(contagem_por_frame.mean(), 2) if not contagem_por_frame.empty else 0.0
    pico_total = int(contagem_por_frame.max()) if not contagem_por_frame.empty else 0

    # 🔹 Razão pessoa/cadeira no último frame (como antes)
    cadeiras = quantidade_atual.get("chair", 0)
    pessoas = quantidade_atual.get("person", 0)
    razao_pessoa_cadeira = round(pessoas / cadeiras, 2) if cadeiras > 0 else ("inf" if pessoas > 0 else 0.0)

    return {
        "fonte": "YOLO",
        "quantidade_atual": quantidade_atual,
        "media_total": media_total,  # média por frame
        "pico_total": pico_total,    # pico por frame
        "razao_pessoa_cadeira": razao_pessoa_cadeira,
        "ultima_atualizacao": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
    }


# =====================================================
# 🔹 Métricas LLaMA
# =====================================================
def calcular_metricas_llama(df):
    if df.empty:
        return gerar_metricas_vazias("LLaMA")

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df["label"] = df["label"].str.replace("_", " ").str.lower()
    df = df[df["label"].isin(OBJETOS_INTERESSE)]

    pivot = df.pivot_table(index="timestamp", columns="label", values="contagem", fill_value=0)
    ultimo = pivot.tail(1).to_dict(orient="records")[0] if not pivot.empty else {}

    media_total = {k.replace(" ", "_"): round(v, 2) for k, v in pivot.mean().to_dict().items()}
    pico_total = {k.replace(" ", "_"): int(v) for k, v in pivot.max().to_dict().items()}

    razao_pessoa_cadeira = 0.0
    if "chair" in ultimo and "person" in ultimo:
        c = ultimo["chair"]
        p = ultimo["person"]
        razao_pessoa_cadeira = round(p / c, 2) if c > 0 else ("inf" if p > 0 else 0.0)

    return {
        "fonte": "LLaMA",
        "quantidade_atual": {k.replace(" ", "_"): int(v) for k, v in ultimo.items()},
        "media_total": media_total,
        "pico_total": pico_total,
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
        "media_total": 0.0,
        "pico_total": 0,
        "razao_pessoa_cadeira": 0.0,
        "ultima_atualizacao": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
    }


# =====================================================
# 🔹 Pipeline completo
# =====================================================
async def gerar_analises_duplas(cnpj: str) -> Dict[str, Any]:
    df_yolo, df_llama = await buscar_dados_mongo_duplo(cnpj)
    analise_yolo = calcular_metricas_yolo(df_yolo)
    analise_llama = calcular_metricas_llama(df_llama)
    return {
        "yolo_analysis": analise_yolo,
        "llama_analysis": analise_llama,
        "resumo": {
            "media_total": {
                "YOLO": analise_yolo.get("media_total", 0),
                "LLaMA": analise_llama.get("media_total", {}),
            },
            "pico_total": {
                "YOLO": analise_yolo.get("pico_total", 0),
                "LLaMA": analise_llama.get("pico_total", {}),
            },
        },
    }
