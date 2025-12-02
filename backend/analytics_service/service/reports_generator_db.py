# service/reports_generator_db.py

from datetime import datetime
from typing import Dict, Any, List

import pandas as pd

from .data_processor_db import (
    buscar_dados_mongo_duplo,
    normalizar_cnpj,
    OBJETOS_INTERESSE,
)


def _relatorio_vazio(fonte: str) -> Dict[str, Any]:
    return {
        "fonte": fonte,
        "daily": [],
        "total": {"person": 0, "chair": 0, "dining_table": 0},
    }


# =====================================================
# 🔹 Helpers internos
# =====================================================
def _normalizar_df_base(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df["label"] = df["label"].astype(str).str.replace("_", " ").str.lower()
    df = df[df["label"].isin(OBJETOS_INTERESSE)]
    return df


def _agrupar_por_dia(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa por dia (YYYY-MM-DD) somando contagens por label.
    Para YOLO, cada linha é 1 objeto detectado; então basta contar.
    Para LLaMA, já teremos uma coluna de contagem agregada.
    """
    if df.empty:
        return df

    df = df.copy()
    df["data"] = df["timestamp"].dt.date
    return df.groupby(["data", "label"])["contagem"].sum().reset_index()


# =====================================================
# 🔹 Relatório YOLO (histórico)
# =====================================================
def calcular_relatorio_diario_total_yolo(df: pd.DataFrame) -> Dict[str, Any]:
    if df.empty:
        return _relatorio_vazio("YOLO")

    # Base comum
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df["label"] = df["label"].astype(str).str.replace("_", " ").str.lower()
    df = df[df["label"].isin(OBJETOS_INTERESSE)]

    if df.empty:
        return _relatorio_vazio("YOLO")

    # Cada linha de YOLO vale 1 objeto
    df["contagem"] = 1

    # Daily
    df_daily = _agrupar_por_dia(df)

    daily_records: List[Dict[str, Any]] = []
    for data, grupo in df_daily.groupby("data"):
        registro = {"date": data.strftime("%Y-%m-%d")}
        for obj in OBJETOS_INTERESSE:
            chave = obj.replace(" ", "_")
            valor = int(grupo[grupo["label"] == obj]["contagem"].sum())
            registro[chave] = valor
        daily_records.append(registro)

    # Total
    total_por_label = df.groupby("label")["contagem"].sum().to_dict()
    total_dict = {
        obj.replace(" ", "_"): int(total_por_label.get(obj, 0))
        for obj in OBJETOS_INTERESSE
    }

    return {
        "fonte": "YOLO",
        "daily": daily_records,
        "total": total_dict,
    }


# =====================================================
# 🔹 Relatório LLaMA (histórico)
# =====================================================
def calcular_relatorio_diario_total_llama(df: pd.DataFrame) -> Dict[str, Any]:
    if df.empty:
        return _relatorio_vazio("LLaMA")

    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df["label"] = df["label"].astype(str).str.replace("_", " ").str.lower()
    df = df[df["label"].isin(OBJETOS_INTERESSE)]

    if df.empty:
        return _relatorio_vazio("LLaMA")

    # Garante coluna contagem
    if "contagem" not in df.columns:
        # fallback: se não tiver contagem, assume 1 por linha
        df["contagem"] = 1

    # Daily
    df_daily = _agrupar_por_dia(df)

    daily_records: List[Dict[str, Any]] = []
    for data, grupo in df_daily.groupby("data"):
        registro = {"date": data.strftime("%Y-%m-%d")}
        for obj in OBJETOS_INTERESSE:
            chave = obj.replace(" ", "_")
            valor = int(grupo[grupo["label"] == obj]["contagem"].sum())
            registro[chave] = valor
        daily_records.append(registro)

    # Total
    total_por_label = df.groupby("label")["contagem"].sum().to_dict()
    total_dict = {
        obj.replace(" ", "_"): int(total_por_label.get(obj, 0))
        for obj in OBJETOS_INTERESSE
    }

    return {
        "fonte": "LLaMA",
        "daily": daily_records,
        "total": total_dict,
    }


# =====================================================
# 🔹 Função principal chamada pela rota
# =====================================================
async def gerar_relatorio_diario_total(cnpj: str) -> Dict[str, Any]:
    """
    Gera o relatório diário + total para um CNPJ.
    - Usa TODO o histórico disponível no Mongo (somente_hoje=False)
    - Calcula relatório diário e total por objeto
    - NÃO salva no banco (isso é responsabilidade da rota)
    """
    df_yolo, df_llama = await buscar_dados_mongo_duplo(cnpj, somente_hoje=False)

    relatorio_yolo = calcular_relatorio_diario_total_yolo(df_yolo)
    relatorio_llama = calcular_relatorio_diario_total_llama(df_llama)

    return {
        "cnpj_normalizado": normalizar_cnpj(cnpj),
        "gerado_em": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "yolo_report": relatorio_yolo,
        "llama_report": relatorio_llama,
    }
