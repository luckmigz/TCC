from ultralytics import YOLO
import supervision as sv
import cv2
import time
import numpy as np
import asyncio # Necessário para o async generator
from typing import List, Tuple, Dict, AsyncGenerator

MODEL = None
TRACKER = None

# Classes de interesse conforme solicitado
CLASSES_DE_INTERESSE: List[str] = ['person', 'chair', 'dining table']

def inicializar_detector_e_tracker(model_path: str = "yolov8n.pt"):
    """Inicializa o modelo YOLO e o tracker apenas uma vez."""
    global MODEL, TRACKER
    if MODEL is None:
        print("🤖 Inicializando modelo YOLO...")
        MODEL = YOLO(model_path)
        TRACKER = sv.ByteTrack()
    return MODEL, TRACKER

async def gerar_deteccoes_continuas(rtsp_url: str, intervalo_segundos: float = 60.0) -> AsyncGenerator[Tuple[sv.Detections, Dict], None]:
    """
    Generator assíncrono contínuo que captura frames da câmera 
    e retorna detecções filtradas a cada 'intervalo_segundos'.
    """
    model, tracker = inicializar_detector_e_tracker()
    try:
        camera_source = int(rtsp_url)
        print(f"🔌 Usando câmera local (Webcam) com ID: {camera_source}")
    except ValueError:
        camera_source = rtsp_url
        print(f"🌐 Conectando à câmera de rede (RTSP): {camera_source}")

    # Usa a variável 'camera_source' que pode ser um int ou str
    cap = cv2.VideoCapture(camera_source) 
    # --- FIM DA MODIFICAÇÃO ---

    if not cap.isOpened():
        # A mensagem de erro agora funciona para ambos os casos
        raise ConnectionRefusedError(f"Falha ao conectar à fonte da câmera: {rtsp_url}") 

    if not cap.isOpened():
        raise ConnectionRefusedError(f"Falha ao conectar à câmera RTSP: {rtsp_url}")

    # Pré-calcula os IDs das classes de interesse
    nomes = model.names
    name_to_id = {v: k for k, v in nomes.items()}
    target_ids = [name_to_id[c] for c in CLASSES_DE_INTERESSE if c in name_to_id]

    print(f"Classes de interesse IDs: {target_ids}")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Falha ao capturar frame, tentando reconectar...")
            cap.release()
            await asyncio.sleep(5) # Espera 5s antes de tentar reconectar
            cap = cv2.VideoCapture(rtsp_url)
            if not cap.isOpened():
                print("❌ Reconexão falhou.")
                await asyncio.sleep(intervalo_segundos) # Espera o ciclo
                continue
            ret, frame = cap.read()
            if not ret:
                continue # Pula este ciclo se a leitura falhar novamente

        # 1. Detecção
        results = model(frame, verbose=False)[0] # verbose=False para menos logs
        detections = sv.Detections.from_ultralytics(results)

        # 2. Filtragem de classes
        if target_ids:
            mask = np.isin(detections.class_id, target_ids)
            detections = detections[mask]

        # 3. Rastreamento (Tracking)
        tracked_detections = tracker.update_with_detections(detections)
        
        # Retorna as detecções rastreadas e os nomes
        yield tracked_detections, nomes

        # Espera o intervalo definido (ex: 60 segundos)
        await asyncio.sleep(intervalo_segundos)

    cap.release()