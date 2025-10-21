# CÓDIGO: restaurante_monitor_light.py
import threading
import time
from restaurante_data_model import Restaurante
from detector_utils_light import gerar_deteccoes_periodicas, inicializar_detector_e_tracker

class RestauranteMonitorLight:
    """
    Versão leve do monitor de restaurante:
    - Usa frames únicos a cada ciclo (sem stream contínuo)
    - Ideal para hardware limitado
    """

    def __init__(self, cnpj: str, nome: str = "Restaurante Monitorado", intervalo: int = 5):
        self.restaurante = Restaurante(cnpj, nome)
        self.intervalo = intervalo  # segundos entre capturas
        self._rodando = False
        self._thread = None

    def _loop_deteccao(self):
        inicializar_detector_e_tracker()
        print(f"🚀 Loop leve iniciado (intervalo: {self.intervalo}s)")
        gerador = gerar_deteccoes_periodicas(intervalo_segundos=self.intervalo, salvar_frame_debug=False)

        while self._rodando:
            try:
                detections, model_names = next(gerador)
                self.restaurante.processar_deteccao_em_tempo_real(detections, model_names)

                print(f"📊 {self.restaurante.ultima_atualizacao} | "
                      f"Pessoas: {self.restaurante.quantidade_atual.get('person', 0)} | "
                      f"Cadeiras: {self.restaurante.quantidade_atual.get('chair', 0)} | "
                      f"Mesas: {self.restaurante.quantidade_atual.get('dining_table', 0)} | "
                      f"Razão P/C: {self.restaurante.razao_pessoa_cadeira}")
            except Exception as e:
                print(f"⚠️ Erro no loop de detecção: {e}")
                time.sleep(1)

    def iniciar(self):
        if not self._rodando:
            self._rodando = True
            self._thread = threading.Thread(target=self._loop_deteccao, daemon=True)
            self._thread.start()
            print("✅ Monitor leve iniciado.")

    def parar(self):
        self._rodando = False
        if self._thread:
            self._thread.join()
            print("🛑 Monitor leve parado.")
