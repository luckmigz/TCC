# CÓDIGO: detector_utils_light.py (modo leve + integração com LLaMA)

import asyncio
from ultralytics import YOLO
import supervision as sv
import cv2
import time
import numpy as np
from typing import Tuple, Dict, Any, Generator, List
from datetime import datetime
from .llama_vision_utils import analisar_frame_com_llama
from typing import Any, Dict, Tuple, AsyncGenerator


# --- Configurações ---
RTSP_URL = "rtsp://CameraSalao:camerasalao@192.168.137.212:554/stream1"
MODEL_PATH = "yolov8n.pt"  # leve e rápido
CLASSES_DE_INTERESSE: List[str] = ["person", "chair", "dining table"]
CONF_THRESH = 0.5
FRAME_WIDTH = None
FRAME_HEIGHT = None
RESIZE_TO = None

# Globais
MODEL = None
TRACKER = None


def inicializar_detector_e_tracker():
    """Inicializa YOLO e ByteTrack (compatível com todas as versões do supervision)."""
    global MODEL, TRACKER
    if MODEL is None:
        print("🤖 Inicializando modelo YOLO (modo leve)...")
        MODEL = YOLO(MODEL_PATH)
    if TRACKER is None:
        TRACKER = sv.ByteTrack()
    return MODEL, TRACKER


def _abrir_camera() -> cv2.VideoCapture:
    """Abre a câmera RTSP e ajusta resolução opcionalmente."""
    cap = cv2.VideoCapture(RTSP_URL)
    if FRAME_WIDTH:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    if FRAME_HEIGHT:
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    return cap


def obter_frame_unico() -> np.ndarray:
    """Captura um único frame e fecha a conexão — evita congelamento."""
    cap = _abrir_camera()
    ret, frame = False, None
    for _ in range(10):
        ret, frame = cap.read()
        if ret and frame is not None:
            break
        time.sleep(0.1)
    cap.release()

    if not ret or frame is None:
        raise ConnectionRefusedError("Falha ao capturar frame RTSP.")
    if RESIZE_TO:
        frame = cv2.resize(frame, RESIZE_TO)
    return frame


async def gerar_deteccoes_periodicas(
    intervalo_segundos: float = 5.0,
    salvar_frame_debug: bool = False
) -> AsyncGenerator[Tuple[Dict[str, Any], Dict[int, str], Dict[str, Any]], None]:
    """
    🔹 Gera detecções em intervalos fixos (sem vídeo ao vivo)
    🔹 Agora retorna DUAS VISÕES:
        1️⃣ YOLO (detections, model_names)
        2️⃣ LLaMA (dict com contagens)
    """
    model, tracker = inicializar_detector_e_tracker()
    print(f"🕐 Detecção integrada (YOLO + LLaMA) a cada {intervalo_segundos:.1f}s")

    while True:
        inicio = time.time()
        try:
            # --- YOLO ---
            frame = obter_frame_unico()
            results = model(frame)[0]
            detections = sv.Detections.from_ultralytics(results)

            # Filtro de confiança e classes
            if hasattr(detections, "confidence"):
                detections = detections[detections.confidence > CONF_THRESH]
            nomes = model.names
            name_to_id = {v: k for k, v in nomes.items()}
            target_ids = [name_to_id[c] for c in CLASSES_DE_INTERESSE if c in name_to_id]
            if target_ids and hasattr(detections, "class_id"):
                mask = np.isin(detections.class_id, target_ids)
                detections = detections[mask]

            tracked = tracker.update_with_detections(detections)

            # --- LLaMA ---
            visao_llama = await asyncio.to_thread(analisar_frame_com_llama, frame)
            # 👆 roda análise do LLaMA em thread separada (não trava o loop)

            # (Opcional) salvar frame anotado
            if salvar_frame_debug:
                try:
                    annotated = results.plot()
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    cv2.imwrite(f"frame_debug_{ts}.jpg", annotated)
                except Exception:
                    pass

            yield tracked, nomes, visao_llama

        except Exception as e:
            print(f"⚠️ Erro na detecção: {e}")

        # Espera até o próximo ciclo sem travar o event loop
        elapsed = time.time() - inicio
        await asyncio.sleep(max(0.0, intervalo_segundos - elapsed))
