
# CÓDIGO: detector_utils_light.py (modo leve: sem vídeo ao vivo, apenas frames periódicos)

from ultralytics import YOLO
import supervision as sv
import cv2
import time
import numpy as np
from typing import Tuple, Dict, Any, Generator, List
from datetime import datetime

# --- Configurações ---
RTSP_URL = "rtsp://CameraSalao:camerasalao@192.168.137.212:554/stream1"
MODEL_PATH = "yolov8n.pt"  # você pode trocar para 'yolov8m.pt' ou 'yolov8l.pt' para mais precisão
CLASSES_DE_INTERESSE: List[str] = ["person", "chair", "dining table"]
CONF_THRESH = 0.5  # confiança mínima para aceitar detecções
FRAME_WIDTH = None   # ex.: 1280  (defina para None para não forçar)
FRAME_HEIGHT = None  # ex.: 720   (defina para None para não forçar)
RESIZE_TO = None     # ex.: (800, 450)  # redimensiona o frame antes do YOLO; deixe None para não redimensionar

# Variáveis globais
MODEL = None
TRACKER = None


def inicializar_detector_e_tracker():
    """Inicializa o YOLO e o ByteTrack apenas uma vez (modo compatível entre versões do supervision)."""
    global MODEL, TRACKER
    if MODEL is None:
        print("🤖 Inicializando modelo YOLO (modo leve)...")
        MODEL = YOLO(MODEL_PATH)
    if TRACKER is None:
        # Inicialização sem parâmetros para evitar incompatibilidades entre versões do supervision
        TRACKER = sv.ByteTrack()
    return MODEL, TRACKER


def _abrir_camera() -> cv2.VideoCapture:
    """Abre a câmera RTSP e aplica resoluções desejadas (se definidas)."""
    cap = cv2.VideoCapture(RTSP_URL)
    if FRAME_WIDTH is not None:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    if FRAME_HEIGHT is not None:
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    return cap


def obter_frame_unico() -> np.ndarray:
    """Captura um único frame e fecha a conexão (evita congelamento por stream contínuo)."""
    cap = _abrir_camera()

    # Em algumas câmeras, os primeiros frames podem vir vazios; tentamos algumas vezes
    ret, frame = False, None
    for _ in range(10):
        ret, frame = cap.read()
        if ret and frame is not None:
            break
        time.sleep(0.1)

    cap.release()

    if not ret or frame is None:
        raise ConnectionRefusedError("Falha ao capturar frame RTSP. Verifique a URL ou a rede.")

    if RESIZE_TO is not None:
        frame = cv2.resize(frame, RESIZE_TO)

    return frame


def gerar_deteccoes_periodicas(intervalo_segundos: float = 5.0, salvar_frame_debug: bool = False 
                               ) -> Generator[Tuple[sv.Detections, Dict[int, str]], None, None]:
    """
    Gera detecções em intervalos, sem janela de vídeo.
    Captura um único frame a cada ciclo, processa no YOLO e retorna as detecções rastreadas.
    """
    model, tracker = inicializar_detector_e_tracker()

    print(f"🕐 Detecção periódica iniciada (a cada {intervalo_segundos:.1f}s). Vídeo ao vivo desativado.")

    while True:
        start = time.time()
        try:
            frame = obter_frame_unico()

            # Inferência YOLO
            results = model(frame)[0]
            detections = sv.Detections.from_ultralytics(results)

            # Filtro por confiança
            if hasattr(detections, "confidence"):
                detections = detections[detections.confidence > CONF_THRESH]

            # Filtro por classes de interesse
            nomes = model.names
            name_to_id = {v: k for k, v in nomes.items()}
            target_ids = [name_to_id[c] for c in CLASSES_DE_INTERESSE if c in name_to_id]

            if target_ids and hasattr(detections, "class_id"):
                mask = np.isin(detections.class_id, target_ids)
                detections = detections[mask]

            # Atualiza rastreador
            tracked = tracker.update_with_detections(detections)

            # Opcional: salva o frame anotado para depuração
            if salvar_frame_debug:
                try:
                    annotated = results.plot()
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    cv2.imwrite(f"frame_debug_{ts}.jpg", annotated)
                except Exception:
                    pass

            yield tracked, nomes

        except Exception as e:
            print(f"⚠️ Erro durante a detecção: {e}")

        # Aguarda até completar o intervalo desejado
        elapsed = time.time() - start
        sleep_for = max(0.0, intervalo_segundos - elapsed)
        time.sleep(sleep_for)
