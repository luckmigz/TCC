from ultralytics import YOLO
import supervision as sv
import cv2
import datetime
import os
import time
import logging
from ..database import detections_collection, control_collection

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def run_detection_process():
    """
    Executa o loop principal de detecção e salvamento de dados.
    """
    IMG_PATH = "frame_mais_recente.jpg"
    if os.path.exists(IMG_PATH):
        os.remove(IMG_PATH)

    model = YOLO("yolov8n.pt")
    RTSP_URL = os.environ.get("RTSP_URL", "rtsp://CameraSalao:CameraSalao@192.168.15.20:554/stream1")
    cap = cv2.VideoCapture(RTSP_URL)
    tracker = sv.ByteTrack()
    ultimo_registro = {}

    logging.info("🚀 Worker de detecção iniciado.")

    while True:
        if control_collection.find_one({"signal": "stop"}):
            logging.info("🛑 Sinal de parada recebido. Encerrando o worker.")
            break

        ret, frame = cap.read()
        if not ret or frame is None:
            logging.warning("⚠️ Falha ao capturar frame. Tentando reconectar...")
            time.sleep(5)
            cap.open(RTSP_URL)
            continue

        results = model(frame)[0]
        detections = sv.Detections.from_ultralytics(results)
        tracked_detections = tracker.update_with_detections(detections)

        documentos_para_inserir = []
        timestamp_atual = datetime.datetime.utcnow()

        for xyxy, conf, cls, track_id in zip(
            tracked_detections.xyxy, tracked_detections.confidence, tracked_detections.class_id, tracked_detections.tracker_id
        ):
            key = (track_id, int(cls))
            if key in ultimo_registro and (timestamp_atual - ultimo_registro[key]).total_seconds() < 2.0:
                continue
            
            ultimo_registro[key] = timestamp_atual

            documento = {
                "timestamp": timestamp_atual,
                "track_id": int(track_id),
                "label": model.names[int(cls)],
                "confidence": float(conf),
                "bounding_box": { "x1": int(xyxy[0]), "y1": int(xyxy[1]), "x2": int(xyxy[2]), "y2": int(xyxy[3]) }
            }
            documentos_para_inserir.append(documento)

            # Desenha no frame para salvar a imagem
            cv2.rectangle(frame, (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3])), (0, 255, 0), 2)
            cv2.putText(frame, f"{model.names[int(cls)]} #{track_id}", (int(xyxy[0]), int(xyxy[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        if documentos_para_inserir:
            detections_collection.insert_many(documentos_para_inserir)
            cv2.imwrite(IMG_PATH, frame)
            logging.info(f"💾 {len(documentos_para_inserir)} novas detecções salvas.")

        time.sleep(0.1)

    cap.release()
    logging.info("✅ Worker de detecção finalizado.")