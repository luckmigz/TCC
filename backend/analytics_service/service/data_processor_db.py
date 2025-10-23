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
# 🔹 Funções auxiliares
# =====================================================
def normalizar_cnpj(valor: str) -> str:
    if valor is None:
        return ""
    return re.sub(r"\D", "", str(valor)).strip()

def converter_valor_bson(valor):
    """Converte tipos {'$numberInt': '3'}, {'$numberDouble': '0.5'}, {'$numberLong': '123'} -> int/float."""
    if isinstance(valor, dict):
        if "$numberInt" in valor:
            return int(valor["$numberInt"])
        if "$numberDouble" in valor:
            return float(valor["$numberDouble"])
        if "$numberLong" in valor:
            return int(valor["$numberLong"])
    return valor

def converter_timestamp_bson(ts_raw):
    """Converte {'$date': {'$numberLong': '1761190423439'}} -> datetime UTC; aceita ISODate e string também."""
    if isinstance(ts_raw, dict) and "$date" in ts_raw:
        inner = ts_raw["$date"]
        if isinstance(inner, dict) and "$numberLong" in inner:
            millis = int(inner["$numberLong"])
            return datetime.utcfromtimestamp(millis / 1000.0)
        # Atlas às vezes exporta "$date": "2025-10-22T00:39:17.546Z"
        if isinstance(inner, str):
            return pd.to_datetime(inner, utc=True, errors="coerce")
    return pd.to_datetime(ts_raw, utc=True, errors="coerce")


# =====================================================
# 🔹 Descoberta de CNPJs existentes (para fallback)
# =====================================================
async def _listar_cnpjs_existentes(colecao, limite: int = 500) -> List[str]:
    """
    Retorna até `limite` CNPJs como strings (como estão salvos),
    olhando nos campos 'cnpj' e 'CNPJ' (na raiz).
    """
    # Project só os campos de CNPJ para evitar tráfego desnecessário
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
    # De-duplicar preservando ordem
    seen = set()
    uniq = []
    for v in valores:
        if v not in seen:
            uniq.append(v)
            seen.add(v)
    return uniq


# =====================================================
# 🔹 Busca dados YOLO / LLaMA (apenas por CNPJ) com fallback
# =====================================================
async def buscar_dados_mongo_duplo(cnpj: str):
    """
    1) Normaliza o CNPJ recebido (só dígitos).
    2) Tenta buscar por 'cnpj'/'CNPJ' como string e int.
    3) Se não encontrar, lista CNPJs existentes, normaliza todos e re-busca
       usando os valores REAIS que têm dígitos iguais ao solicitado.
    """
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
    print(f"\n[DEBUG] 🔎 Buscando por CNPJ normalizado: {cnpj_limpo}")
    print(f"[DEBUG] Query inicial: {query}")

    cursor = colecao.find(query)
    docs = await cursor.to_list(length=None)
    print(f"[DEBUG] 📦 Encontrados (query inicial): {len(docs)}")

    # ---------- Fallback por descoberta de CNPJs ----------
    if not docs:
        existentes = await _listar_cnpjs_existentes(colecao, limite=500)
        existentes_norm = [(orig, normalizar_cnpj(orig)) for orig in existentes]
        candidatos_reais = [orig for (orig, norm) in existentes_norm if norm == cnpj_limpo]

        print(f"[DEBUG] 🔁 Fallback: distintos na coleção (até 500) = {len(existentes)}")
        # Mostra um pequeno resumo para debug
        demo = existentes[:10]
        if demo:
            print(f"[DEBUG] Exemplos de CNPJs salvos (amostra): {demo}")

        if candidatos_reais:
            print(f"[DEBUG] ✅ Candidatos reais que batem (normalizado): {candidatos_reais}")
            query2 = {"$or": [{"cnpj": {"$in": candidatos_reais}},
                              {"CNPJ": {"$in": candidatos_reais}}]}
            cursor2 = colecao.find(query2)
            docs = await cursor2.to_list(length=None)
            print(f"[DEBUG] 📦 Encontrados (fallback): {len(docs)}")
        else:
            print("[DEBUG] ❌ Nenhum CNPJ equivalente (por dígitos) encontrado no banco.")

    # ---------- Parsing dos documentos ----------
    if not docs:
        df_vazio = pd.DataFrame(columns=["timestamp", "label"])
        return df_vazio, df_vazio

    registros_yolo, registros_llama = [], []

    for i, doc in enumerate(docs):
        ts = converter_timestamp_bson(doc.get("timestamp"))
        if i == 0:
            cnpj_doc = doc.get("cnpj") if "cnpj" in doc else doc.get("CNPJ")
            print(f"[DEBUG] 🧾 Exemplo doc[0] CNPJ salvo: {cnpj_doc} (type={type(cnpj_doc)})")
            print(f"[DEBUG] 🕓 Exemplo timestamp convertido: {ts}")

        # YOLO
        for det in doc.get("detections_yolo", []):
            label = str(det.get("label", "")).replace("_", " ").lower()
            conf = converter_valor_bson(det.get("confidence", 0))
            registros_yolo.append({
                "timestamp": ts,
                "label": label,
                "confidence": conf
            })

        # LLaMA (dict label -> contagem)
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

    print(f"[DEBUG] 📊 YOLO linhas: {len(df_yolo)} | LLaMA linhas: {len(df_llama)}")
    if not df_yolo.empty:
        print(f"[DEBUG] 🔸 YOLO head:\n{df_yolo.head(3)}")
    if not df_llama.empty:
        print(f"[DEBUG] 🔸 LLaMA head:\n{df_llama.head(3)}")

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
