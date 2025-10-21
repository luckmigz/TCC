# CÓDIGO: restaurante_data_model.py (versão corrigida)

import pandas as pd
from datetime import datetime
from typing import Dict, List, Union, Any
import supervision as sv

# IMPORTANTE: A função calcular_metricas será usada.
from data_processor_utils import calcular_metricas 

# Colunas do DataFrame de histórico em memória
COLUMNS = ['timestamp', 'track_id', 'label', 'confidence', 'x1', 'y1', 'x2', 'y2']


class Restaurante:
    """
    Classe que armazena o estado do dashboard, incluindo o histórico de detecções 
    em memória (DataFrame) para cálculos de média e pico.
    """
    
    def __init__(self, cnpj: str, nome: str = "Restaurante Monitorado"):
        # Atributos de Identificação
        self.cnpj: str = cnpj
        self.nome: str = nome
        
        # Histórico em memória
        self._historico_df = pd.DataFrame(columns=COLUMNS)
        
        # Indicadores atuais
        self._quantidade_atual: Dict[str, int] = {"person": 0, "chair": 0, "dining_table": 0}
        self._media_pessoas_5min: float = 0.0
        self._media_pessoas_1h: float = 0.0
        self._pico_pessoas_1h: int = 0
        self._razao_pessoa_cadeira: Union[float, str] = 0.0 
        
        # Séries históricas (para gráficos)
        self._historico_pessoas: List[Dict[str, Any]] = []
        self._historico_cadeiras: List[Dict[str, Any]] = []
        self._historico_mesas: List[Dict[str, Any]] = []
        
        # Metadados
        self._ultima_atualizacao: str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # --- Getters ---
    @property
    def quantidade_atual(self) -> Dict[str, int]:
        return self._quantidade_atual
    @property
    def media_pessoas_5min(self) -> float:
        return self._media_pessoas_5min
    @property
    def media_pessoas_1h(self) -> float:
        return self._media_pessoas_1h
    @property
    def pico_pessoas_1h(self) -> int:
        return self._pico_pessoas_1h
    @property
    def razao_pessoa_cadeira(self) -> Union[float, str]:
        return self._razao_pessoa_cadeira
    @property
    def historico_pessoas(self) -> List[Dict[str, Any]]:
        return self._historico_pessoas
    @property
    def historico_cadeiras(self) -> List[Dict[str, Any]]:
        return self._historico_cadeiras
    @property
    def historico_mesas(self) -> List[Dict[str, Any]]:
        return self._historico_mesas
    @property
    def ultima_atualizacao(self) -> str:
        return self._ultima_atualizacao

    # --- Atualização interna ---
    def atualizar_indicadores(self, data: Dict[str, Any]):
        """Atualiza os atributos internos com base nas métricas calculadas."""
        self._quantidade_atual = data.get("quantidade_atual", self._quantidade_atual)
        self._media_pessoas_5min = data.get("media_pessoas_5min", self._media_pessoas_5min)
        self._media_pessoas_1h = data.get("media_pessoas_1h", self._media_pessoas_1h)
        self._pico_pessoas_1h = data.get("pico_pessoas_1h", self._pico_pessoas_1h)
        self._razao_pessoa_cadeira = data.get("razao_pessoa_cadeira", self._razao_pessoa_cadeira)
        self._historico_pessoas = data.get("historico_pessoas_2min", self._historico_pessoas)
        self._historico_cadeiras = data.get("historico_cadeiras_2min", self._historico_cadeiras)
        self._historico_mesas = data.get("historico_mesas_2min", self._historico_mesas)
        self._ultima_atualizacao = data.get("ultima_atualizacao", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    # --- Processamento principal ---
    def processar_deteccao_em_tempo_real(self, detections: sv.Detections, model_names: Dict[int, str]):
        """
        Recebe detecções brutas, adiciona ao histórico em memória (self._historico_df),
        e recalcula todos os indicadores. Inclui tratamento para frames sem detecção.
        """
        rows = []
        now = datetime.now()
        now_str = now.strftime('%Y-%m-%d %H:%M:%S')

        # 🔹 Caso haja detecções, registra normalmente
        if len(detections) > 0:
            for xyxy, conf, cls, track_id in zip(
                detections.xyxy, detections.confidence, detections.class_id, detections.tracker_id
            ):
                x1, y1, x2, y2 = map(int, xyxy)
                label = model_names[int(cls)]
                conf = float(conf)
                rows.append([now_str, track_id, label, conf, x1, y1, x2, y2])
        else:
            # 🔹 Frame sem detecções — adiciona marcador "none"
            rows.append([now_str, None, "none", 0.0, 0, 0, 0, 0])

        df_novo_frame = pd.DataFrame(rows, columns=COLUMNS)

        # 🔹 Mantém apenas 2h de histórico recente
        self._historico_df['timestamp'] = pd.to_datetime(self._historico_df['timestamp'], errors='coerce')
        limite_memoria = now - pd.Timedelta(hours=2)
        df_recente = self._historico_df[self._historico_df['timestamp'] > limite_memoria]

        # 🔹 Atualiza histórico em memória
        self._historico_df = pd.concat([df_recente, df_novo_frame], ignore_index=True)

        # 🔹 Recalcula métricas
        metricas_calculadas = calcular_metricas(self._historico_df)
        self.atualizar_indicadores(metricas_calculadas)
