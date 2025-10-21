import datetime
from collections import deque

class Restaurante:
    def __init__(self, cnpj: str, nome: str):
        self.cnpj = cnpj
        self.nome = nome
        self.quantidade_atual = {}
        self.historico_pessoas = deque(maxlen=60)
        self.ultima_atualizacao = None
        self.razao_pessoa_cadeira = 0.0
        self.media_pessoas_5min = 0.0
        self.pico_pessoas_1h = 0
        self.contador_total = 0

    def processar_deteccao_em_tempo_real(self, detections, model_names):
        contagem = {}
        for class_id in detections.class_id:
            nome = model_names.get(class_id, "desconhecido")
            contagem[nome] = contagem.get(nome, 0) + 1

        self.quantidade_atual = contagem
        self.historico_pessoas.append(contagem.get("person", 0))
        self.ultima_atualizacao = datetime.datetime.now()
        self._atualizar_metricas()

    def _atualizar_metricas(self):
        pessoas = self.quantidade_atual.get("person", 0)
        cadeiras = self.quantidade_atual.get("chair", 1)
        self.razao_pessoa_cadeira = round(pessoas / cadeiras, 2)
        self.media_pessoas_5min = round(sum(self.historico_pessoas) / len(self.historico_pessoas), 2)
        self.pico_pessoas_1h = max(self.pico_pessoas_1h, pessoas)
