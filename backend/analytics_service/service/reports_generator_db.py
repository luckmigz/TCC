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
        "total": {obj.replace(" ", "_"): 0 for obj in OBJETOS_INTERESSE},
    }


# =====================================================
# 🔹 Relatório diário e total - YOLO
# =====================================================
def calcular_relatorio_diario_total_yolo(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Gera contagem diária e total de cada objeto para YOLO.
    - total: número total de detecções (linhas) por label
    - daily: número de detecções por dia e label
    """
    if df.empty:
        return _relatorio_vazio("YOLO")

    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df = df.dropna(subset=["timestamp"])

    # normalização do label
    df["label"] = df["label"].str.replace("_", " ").str.lower()
    df = df[df["label"].isin(OBJETOS_INTERESSE)]

    if df.empty:
        return _relatorio_vazio("YOLO")

    # só a parte de data
    df["date"] = df["timestamp"].dt.date

    # 🔹 Total geral por label (qtd de detecções)
    total_por_label = df.groupby("label").size().to_dict()
    total = {
        label.replace(" ", "_"): int(total_por_label.get(label, 0))
        for label in OBJETOS_INTERESSE
    }

    # 🔹 Contagem diária por label
    daily_rows: List[Dict[str, Any]] = []
    group = (
        df.groupby(["date", "label"])
        .size()
        .reset_index(name="total_dia")
    )

    for _, row in group.iterrows():
        daily_rows.append(
            {
                "date": row["date"].isoformat(),
                "label": row["label"].replace(" ", "_"),
                "total_dia": int(row["total_dia"]),
            }
        )

    return {
        "fonte": "YOLO",
        "daily": daily_rows,
        "total": total,
    }


# =====================================================
# 🔹 Relatório diário e total - LLaMA
# =====================================================
def calcular_relatorio_diario_total_llama(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Gera contagem diária e total de cada objeto para LLaMA.
    Usa a coluna 'contagem' (quantidade por amostra).
    - total: soma de 'contagem' por label
    - daily: soma de 'contagem' por dia e label
    """
    if df.empty:
        return _relatorio_vazio("LLaMA")

    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df = df.dropna(subset=["timestamp"])

    df["label"] = df["label"].str.replace("_", " ").str.lower()
    df = df[df["label"].isin(OBJETOS_INTERESSE)]

    if df.empty:
        return _relatorio_vazio("LLaMA")

    df["date"] = df["timestamp"].dt.date

    # 🔹 Total geral por label (soma das contagens)
    total_series = df.groupby("label")["contagem"].sum()
    total = {
        label.replace(" ", "_"): int(total_series.get(label, 0))
        for label in OBJETOS_INTERESSE
    }

    # 🔹 Contagem diária por label (soma das contagens no dia)
    daily_rows: List[Dict[str, Any]] = []
    group = (
        df.groupby(["date", "label"])["contagem"]
        .sum()
        .reset_index(name="total_dia")
    )

    for _, row in group.iterrows():
        daily_rows.append(
            {
                "date": row["date"].isoformat(),
                "label": row["label"].replace(" ", "_"),
                "total_dia": int(row["total_dia"]),
            }
        )

    return {
        "fonte": "LLaMA",
        "daily": daily_rows,
        "total": total,
    }


# =====================================================
# 🔹 Função principal de relatório
# =====================================================
async def gerar_relatorio_diario_total(cnpj: str) -> Dict[str, Any]:
    """
    - Busca todos os documentos de detecção para o CNPJ (YOLO + LLaMA)
    - Calcula relatório diário e total por objeto
    - NÃO salva no banco (isso é responsabilidade da rota)
    """
    df_yolo, df_llama = await buscar_dados_mongo_duplo(cnpj)

    relatorio_yolo = calcular_relatorio_diario_total_yolo(df_yolo)
    relatorio_llama = calcular_relatorio_diario_total_llama(df_llama)

    return {
        "cnpj_normalizado": normalizar_cnpj(cnpj),
        "gerado_em": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "yolo_report": relatorio_yolo,
        "llama_report": relatorio_llama,
    }
