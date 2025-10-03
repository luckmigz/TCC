import pandas as pd
import json
import os
import time
from datetime import datetime

# --- Configurações ---
CSV_PATH = "detecoes.csv"
JSON_OUTPUT_PATH = "indicadores.json" # Onde o JSON será salvo
OBJETOS_INTERESSE = ['chair', 'dining table', 'person']
INTERVALO_PROCESSAMENTO_SEC = 60 # 1 minuto (para o loop de processamento)
INTERVALO_GRAFICO_MIN = 2 # 2 minutos (para o agrupamento da série histórica)
JANELA_CURTO_PRAZO_MIN = 5 # Janela de tempo para a métrica de 5 minutos
JANELA_LONGO_PRAZO_MIN = 60 # Janela de tempo para as métricas de 1 hora
STOP_FLAG = "stop.flag"
# ---

def carregar_dados_e_limpar():
    """Carrega o CSV e prepara o DataFrame."""
    if not os.path.exists(CSV_PATH) or os.stat(CSV_PATH).st_size == 0:
        # Retorna um DataFrame vazio com as colunas esperadas para evitar erros
        return pd.DataFrame(columns=['timestamp', 'track_id', 'label', 'confidence', 'x1', 'y1', 'x2', 'y2'])

    try:
        df = pd.read_csv(CSV_PATH)
        
        # Conversões
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df = df.dropna(subset=['timestamp'])

        df['label'] = df['label'].astype(str).str.strip().str.lower()
        df = df[df['label'].isin(OBJETOS_INTERESSE)]
        
        return df
    except pd.errors.EmptyDataError:
        print("AVISO: O arquivo CSV está vazio ou ilegível.")
        return pd.DataFrame(columns=['timestamp', 'track_id', 'label', 'confidence', 'x1', 'y1', 'x2', 'y2'])
    except Exception as e:
        print(f"ERRO ao carregar dados: {e}")
        return pd.DataFrame(columns=['timestamp', 'track_id', 'label', 'confidence', 'x1', 'y1', 'x2', 'y2'])

def calcular_serie_temporal(df, label, intervalo_min):
    """Calcula a série temporal de contagem para um objeto específico."""
    df_obj = df[df['label'] == label].copy()
    
    if df_obj.empty:
        return []

    # Agrupamento (binning) no intervalo definido
    df_obj['periodo'] = df_obj['timestamp'].dt.floor(f'{intervalo_min}min')
    
    # Dentro de cada período, queremos o MÁXIMO de detecções
    historico = (
        df_obj
        .groupby(['periodo', 'timestamp'])
        .size().reset_index(name='contagem_frame')
        .groupby('periodo')
        .agg(contagem=('contagem_frame', 'max'))
        .reset_index()
        .sort_values('periodo')
    )
    
    # Formata para JSON
    historico_json = [
        {"timestamp": row['periodo'].strftime('%Y-%m-%d %H:%M:%S'), label.replace(' ', '_'): int(row['contagem'])}
        for index, row in historico.iterrows()
    ]
    return historico_json


def calcular_metricas(df):
    """Calcula a média, contagens atuais e todas as séries temporais."""
    
    # 1. Valores padrão para quando o DataFrame está vazio
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

    # --- Pré-processamento e Agrupamento ---

    # Encontra o último timestamp registrado
    ultimo_timestamp = df['timestamp'].max()

    # 2. Filtragem de dados para análise de 1 hora
    limite_1h = pd.Timestamp.now() - pd.Timedelta(minutes=JANELA_LONGO_PRAZO_MIN)
    df_recente_1h = df[df['timestamp'] > limite_1h].copy()
    
    # DataFrame de pessoas para cálculo de média e pico
    df_pessoas_1h = df_recente_1h[df_recente_1h['label'] == 'person'].copy()
    contagem_por_frame_1h = df_pessoas_1h.groupby('timestamp').size().reset_index(name='contagem')

    # --- Indicadores Chave ---

    # Métrica: Quantidade Atual (do último frame)
    df_atual = df[df['timestamp'] == ultimo_timestamp]
    contagem_atual = df_atual.groupby("label").size().to_dict()
    quantidade_atual = {obj.replace(' ', '_'): contagem_atual.get(obj, 0) for obj in OBJETOS_INTERESSE}
    
    # Métrica: Média de Pessoas (5 minutos)
    limite_5min = pd.Timestamp.now() - pd.Timedelta(minutes=JANELA_CURTO_PRAZO_MIN)
    df_pessoas_5min = df[(df['timestamp'] > limite_5min) & (df['label'] == 'person')]
    contagem_por_frame_5min = df_pessoas_5min.groupby('timestamp').size().reset_index(name='contagem')
    media_pessoas_5min = round(contagem_por_frame_5min['contagem'].mean(), 2) if not contagem_por_frame_5min.empty else 0.0

    # Métrica: Média de Pessoas (1 Hora)
    media_pessoas_1h = round(contagem_por_frame_1h['contagem'].mean(), 2) if not contagem_por_frame_1h.empty else 0.0

    # Métrica: Pico de Pessoas (1 Hora)
    pico_pessoas_1h = int(contagem_por_frame_1h['contagem'].max()) if not contagem_por_frame_1h.empty else 0

    # Métrica: Razão Pessoa/Cadeira
    cadeiras = quantidade_atual.get('chair', 0)
    pessoas = quantidade_atual.get('person', 0)
    razao_pessoa_cadeira = round(pessoas / cadeiras, 2) if cadeiras > 0 else (float('inf') if pessoas > 0 else 0.0)

    # --- Séries Históricas (Gráficos) ---
    
    historico_pessoas = calcular_serie_temporal(df, 'person', INTERVALO_GRAFICO_MIN)
    historico_cadeiras = calcular_serie_temporal(df, 'chair', INTERVALO_GRAFICO_MIN)
    historico_mesas = calcular_serie_temporal(df, 'dining table', INTERVALO_GRAFICO_MIN)

    # --- Resultado Final ---
    
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

def main():
    """Função principal que executa o processamento em loop e salva o JSON a cada 1 minuto."""
    
    print("🚀 Processador de dados iniciado. Atualizando indicadores.json a cada 60 segundos.")
    
    while True:
        try:
            # 1. Checa sinal de parada
            if os.path.exists(STOP_FLAG):
                print("🛑 Processamento parado pelo usuário.")
                break
            
            # 2. Carrega os dados mais recentes do histórico
            df_dados = carregar_dados_e_limpar()
            
            # 3. Calcula todas as métricas
            if df_dados.empty:
                output_data = calcular_metricas(pd.DataFrame())
            else:
                output_data = calcular_metricas(df_dados)

            # 4. Salva o JSON
            with open(JSON_OUTPUT_PATH, 'w') as f:
                json.dump(output_data, f, indent=4)
            
            print(f"✅ JSON atualizado: {output_data['ultima_atualizacao']} | Pessoas: {output_data['quantidade_atual']['person']}")

        except Exception as e:
            print(f"ERRO CRÍTICO no processador: {e}")
            
        # 5. Espera 60 segundos antes da próxima execução
        time.sleep(INTERVALO_PROCESSAMENTO_SEC)

if __name__ == "__main__":
    main()
