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


# =====================================================
# 🔹 Conexão Mongo
# =====================================================
async def obter_colecao(nome_colecao: str):
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    return db[nome_colecao]


# =====================================================
# 🔹 Conversores BSON → Python
# =====================================================
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
    return pd.to_datetime(ts_raw, utc=True, errors="coerce")


# =====================================================
# 🔹 Busca dados (somente CNPJ) + debug
# =====================================================
async def buscar_dados_mongo_duplo(cnpj: str):
    colecao = await obter_colecao(COLLECTION_RAW)
    query = {"$or": [{"cnpj": cnpj}, {"CNPJ": cnpj}]}

    print(f"\n[DEBUG] 🔎 Executando busca Mongo para CNPJ={cnpj}")
    cursor = colecao.find(query)
    docs = await cursor.to_list(length=20)
    print(f"[DEBUG] 📦 {len(docs)} documentos encontrados")

    if not docs:
        print("[DEBUG] ⚠️ Nenhum documento encontrado.")
        df_vazio = pd.DataFrame(columns=["timestamp", "label"])
        return df_vazio, df_vazio

    registros_yolo, registros_llama = [], []

    for i, doc in enumerate(docs):
        ts = converter_timestamp_bson(doc.get("timestamp"))
        if i == 0:
            print(f"[DEBUG] 🕓 Exemplo timestamp bruto: {doc.get('timestamp')}")
            print(f"[DEBUG] 🕓 Convertido → {ts}")

        for det in doc.get("detections_yolo", []):
            label = str(det.get("label", "")).replace("_", " ").lower()
            conf = converter_valor_bson(det.get("confidence", 0))
            registros_yolo.append({"timestamp": ts, "label": label, "confidence": conf})

        visao_llama = doc.get("detections_llama", {})
        if isinstance(visao_llama, dict):
            for label, valor in visao_llama.items():
                contagem = converter_valor_bson(valor)
                registros_llama.append({
                    "timestamp": ts,
                    "label": label.replace("_", " ").lower(),
                    "contagem": contagem
                })

    df_yolo = pd.DataFrame(registros_yolo)
    df_llama = pd.DataFrame(registros_llama)

    print(f"[DEBUG] 📊 YOLO linhas: {len(df_yolo)} | LLaMA linhas: {len(df_llama)}")
    if not df_yolo.empty:
        print(f"[DEBUG] 🔸 Exemplo YOLO:\n{df_yolo.head(3)}")
    if not df_llama.empty:
        print(f"[DEBUG] 🔸 Exemplo LLaMA:\n{df_llama.head(3)}")

    return df_yolo, df_llama


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
        print("[DEBUG] ⚠️ YOLO DF vazio após normalização de labels.")
        return gerar_metricas_vazias()

    df["timestamp_min"] = df["timestamp"].dt.floor("1min")
    ultimo_timestamp = df["timestamp_min"].max()
    df_atual = df[df["timestamp_min"] == ultimo_timestamp]

    contagem_atual = df_atual.groupby("label").size().to_dict()
    quantidade_atual = {obj.replace(" ", "_"): contagem_atual.get(obj, 0) for obj in OBJETOS_INTERESSE}

    cadeiras = quantidade_atual.get("chair", 0)
    pessoas = quantidade_atual.get("person", 0)
    razao = round(pessoas / cadeiras, 2) if cadeiras > 0 else ("inf" if pessoas > 0 else 0.0)

    print(f"[DEBUG] ✅ YOLO quantidade_atual={quantidade_atual} razão={razao}")

    return {
        "fonte": "YOLO",
        "quantidade_atual": quantidade_atual,
        "media_pessoas_5min": 0.0,
        "media_pessoas_1h": 0.0,
        "pico_pessoas_1h": 0,
        "razao_pessoa_cadeira": razao,
        "historico_pessoas_2min": [],
        "historico_cadeiras_2min": [],
        "historico_mesas_2min": [],
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
        print("[DEBUG] ⚠️ LLaMA DF vazio após normalização de labels.")
        return gerar_metricas_vazias(fonte="LLaMA")

    pivot = df.pivot_table(index="timestamp", columns="label", values="contagem", fill_value=0)
    ultimo = pivot.tail(1).to_dict(orient="records")[0]
    print(f"[DEBUG] ✅ LLaMA último frame={ultimo}")

    return {
        "fonte": "LLaMA",
        "quantidade_atual": {k.replace(" ", "_"): int(v) for k, v in ultimo.items()},
        "media_5min": {},
        "media_1h": {},
        "razao_pessoa_cadeira": 0.0,
        "ultima_atualizacao": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
    }


# =====================================================
# 🔹 Métricas padrão vazias
# =====================================================
def gerar_metricas_vazias(fonte="YOLO"):
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
# 🔹 Pipeline principal
# =====================================================
async def gerar_analises_duplas(cnpj: str) -> Dict[str, Any]:
    df_yolo, df_llama = await buscar_dados_mongo_duplo(cnpj)
    print(f"[DEBUG] ✅ DataFrames recebidos: YOLO={len(df_yolo)} linhas, LLaMA={len(df_llama)} linhas")
    analise_yolo = calcular_metricas_yolo(df_yolo)
    analise_llama = calcular_metricas_llama(df_llama)
    return {"yolo_analysis": analise_yolo, "llama_analysis": analise_llama}
