# CÓDIGO: data_processor_utils.py (versão corrigida)

import pandas as pd
from datetime import datetime
from typing import Dict, List, Any

# --- Configurações ---
OBJETOS_INTERESSE = ['chair', 'dining table', 'person']
INTERVALO_GRAFICO_MIN = 2 
JANELA_CURTO_PRAZO_MIN = 5 
JANELA_LONGO_PRAZO_MIN = 60 
# ---

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
    
    historico_json = [
        {"timestamp": row['periodo'].strftime('%Y-%m-%d %H:%M:%S'), label.replace(' ', '_'): int(row['contagem'])}
        for index, row in historico.iterrows()
    ]
    return historico_json


def calcular_metricas(df):
    """
    Calcula todas as métricas em tempo real usando o DataFrame passado em memória.
    Inclui tratamento para ausência de detecções.
    """
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.dropna(subset=['timestamp']).copy()

    # 🔹 Mantém apenas as classes relevantes
    df = df[df['label'].isin(['person', 'chair', 'dining table'])].copy()

    if df.empty:
        return {
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

    ultimo_timestamp = df['timestamp'].max()
    df_atual = df[df['timestamp'] == ultimo_timestamp]

    # 🔹 Se não há detecções no frame mais recente, zera as contagens
    if df_atual.empty:
        quantidade_atual = {"person": 0, "chair": 0, "dining_table": 0}
    else:
        contagem_atual = df_atual.groupby("label").size().to_dict()
        quantidade_atual = {obj.replace(' ', '_'): contagem_atual.get(obj, 0) for obj in OBJETOS_INTERESSE}

    # 🔹 Garante que pessoa = 0 se não houver detecção recente
    if quantidade_atual.get('person', 0) == 0:
        quantidade_atual['person'] = 0

    # --- Cálculos adicionais ---
    limite_1h = pd.Timestamp.now() - pd.Timedelta(minutes=JANELA_LONGO_PRAZO_MIN)
    df_recente_1h = df[df['timestamp'] > limite_1h].copy()
    
    df_pessoas_1h = df_recente_1h[df_recente_1h['label'] == 'person'].copy()
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
