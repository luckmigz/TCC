# service/detector_utils.py
from ultralytics import YOLO
import supervision as sv
import cv2
import numpy as np
import asyncio
import time
from datetime import datetime
from typing import AsyncGenerator, Tuple, Dict, List, Union

# --- Configurações principais ---
MODEL_PATH = "yolov8n.pt"
CLASSES_DE_INTERESSE: List[str] = ["person", "chair", "dining table"]
CONF_THRESH = 0.5  # confiança mínima para aceitar detecções
FRAME_WIDTH = None   # opcional (não altera se None)
FRAME_HEIGHT = None  # opcional (não altera se None)

# Variáveis globais
MODEL = None
TRACKER = None


# ------------------------------------------------------------------------------
# Inicializa YOLO + ByteTrack
# ------------------------------------------------------------------------------
def inicializar_detector_e_tracker():
    """Inicializa YOLO e ByteTrack uma única vez (modo leve e compatível)."""
    global MODEL, TRACKER
    if MODEL is None:
        print("🤖 Inicializando modelo YOLO (modo leve)...")
        MODEL = YOLO(MODEL_PATH)
    if TRACKER is None:
        TRACKER = sv.ByteTrack()
    return MODEL, TRACKER


# ------------------------------------------------------------------------------
# Abre câmera (RTSP ou webcam)
# ------------------------------------------------------------------------------
def abrir_camera(fonte_camera: Union[str, int]) -> cv2.VideoCapture:
    """
    Abre a câmera RTSP ou webcam.
    Se 'fonte_camera' for número, usa webcam local.
    Caso contrário, tenta abrir a URL RTSP.
    """
    try:
        camera_id = int(fonte_camera)
        print(f"🎥 Usando webcam local (ID: {camera_id})")
        cap = cv2.VideoCapture(camera_id)
    except ValueError:
        print(f"🌐 Conectando à câmera RTSP: {fonte_camera}")
        cap = cv2.VideoCapture(fonte_camera)

    if FRAME_WIDTH is not None:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    if FRAME_HEIGHT is not None:
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not cap.isOpened():
        raise ConnectionRefusedError(f"❌ Falha ao abrir câmera: {fonte_camera}")

    return cap


# ------------------------------------------------------------------------------
# Captura de frame único (sem alterar resolução)
# ------------------------------------------------------------------------------
def obter_frame_unico(fonte_camera: Union[str, int]) -> np.ndarray:
    """
    Captura um único frame e fecha a conexão (mantém resolução original).
    """
    cap = abrir_camera(fonte_camera)

    ret, frame = False, None
    for _ in range(10):  # tenta algumas vezes caso os primeiros frames venham vazios
        ret, frame = cap.read()
        if ret and frame is not None:
            break
        time.sleep(0.1)

    cap.release()

    if not ret or frame is None:
        raise ConnectionRefusedError(f"Falha ao capturar frame da câmera {fonte_camera}")

    return frame


# ------------------------------------------------------------------------------
# Detecção contínua e leve (modo periódico)
# ------------------------------------------------------------------------------
async def gerar_deteccoes_continuas(
    rtsp_url: str,
    intervalo_segundos: float = 60.0
) -> AsyncGenerator[Tuple[sv.Detections, Dict[int, str]], None]:
    """
    Gera detecções contínuas em intervalos fixos (modo leve e periódico).
    Compatível com webcam ou RTSP.
    """
    model, tracker = inicializar_detector_e_tracker()
    nomes = model.names

    # Identifica tipo de câmera
    fonte_camera = rtsp_url
    try:
        camera_id = int(rtsp_url)
        fonte_camera = camera_id
        print(f"🎥 Usando webcam local (ID: {camera_id})")
    except ValueError:
        print(f"🌐 Conectando à câmera RTSP: {rtsp_url}")

    print(f"🕐 Detecção periódica iniciada — intervalo: {intervalo_segundos:.1f}s")

    while True:
        start_time = time.time()
        try:
            frame = obter_frame_unico(fonte_camera)

            # Executa YOLO
            results = model(frame, verbose=False)[0]
            detections = sv.Detections.from_ultralytics(results)

            # Filtro de confiança
            if hasattr(detections, "confidence"):
                detections = detections[detections.confidence > CONF_THRESH]

            # Filtro de classes de interesse
            name_to_id = {v: k for k, v in nomes.items()}
            target_ids = [name_to_id[c] for c in CLASSES_DE_INTERESSE if c in name_to_id]

            if target_ids and hasattr(detections, "class_id"):
                mask = np.isin(detections.class_id, target_ids)
                detections = detections[mask]

            # Atualiza rastreador
            tracked = tracker.update_with_detections(detections)

            # Exibe contagem no log
            contagem = {}
            for class_id in getattr(detections, "class_id", []):
                label = nomes.get(class_id, "desconhecido")
                contagem[label] = contagem.get(label, 0) + 1

            if contagem:
                resumo = ", ".join([f"{obj}: {qtd}" for obj, qtd in contagem.items()])
                print(f"[{datetime.now():%H:%M:%S}] 🎯 Objetos detectados → {resumo}")
            else:
                print(f"[{datetime.now():%H:%M:%S}] 🚫 Nenhum objeto de interesse detectado.")

            yield tracked, nomes

        except Exception as e:
            print(f"⚠️ Erro durante a detecção: {e}")

        # Mantém a periodicidade precisa
        elapsed = time.time() - start_time
        restante = max(0.0, intervalo_segundos - elapsed)
        await asyncio.sleep(restante)
