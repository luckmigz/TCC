# detector.py
from ultralytics import YOLO
import supervision as sv
import cv2
import pandas as pd
import datetime
import os
import time

# Arquivos de saída
OUTPUT_CSV = "detecoes.csv"
STOP_FLAG = "stop.flag"
IMG_PATH = "frame_mais_recente.jpg"

# Colunas do CSV
COLUMNS = ['timestamp', 'track_id', 'label', 'confidence', 'x1', 'y1', 'x2', 'y2']


# 🔹 Limpa imagem antiga antes de começar
if os.path.exists(IMG_PATH):
    os.remove(IMG_PATH)
    print("🧹 frame_mais_recente.jpg removido para iniciar limpo.")

# Carrega modelo YOLO
model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture(0)

# Cria CSV vazio, se não existir
if not os.path.exists(OUTPUT_CSV):
    pd.DataFrame(columns=COLUMNS).to_csv(OUTPUT_CSV, index=False)

# Inicializa tracker
tracker = sv.ByteTrack()

# Para evitar registros duplicados
ultimo_registro = {}

print("🚀 Detector iniciado. Pressione Ctrl+C para sair.")

while True:
    # Checa sinal de parada
    if os.path.exists(STOP_FLAG):
        print("🛑 Detecção parada pelo usuário.")
        break

    ret, frame = cap.read()
    if not ret:
        print("⚠️ Falha ao capturar frame.")
        break

    # Roda YOLO
    results = model(frame)[0]
    detections = sv.Detections.from_ultralytics(results)

    # Atualiza tracker
    tracked = tracker.update_with_detections(detections)

    rows = []
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for xyxy, conf, cls, track_id in zip(
        tracked.xyxy, tracked.confidence, tracked.class_id, tracked.tracker_id
    ):
        x1, y1, x2, y2 = map(int, xyxy)
        label = model.names[int(cls)]
        conf = float(conf)

        # Checa duplicidade: mesmo objeto já registrado recentemente
        key = (track_id, label)
        if key in ultimo_registro:
            diff = datetime.datetime.now() - ultimo_registro[key]
            if diff.total_seconds() < 2:  # 2 segundos de tolerância
                continue

        # Registra o novo objeto
        ultimo_registro[key] = datetime.datetime.now()
        rows.append([now, track_id, label, conf, x1, y1, x2, y2])

        # Desenha caixa com ID
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f"{label} #{track_id}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Salva no CSV
    if rows:
        df = pd.DataFrame(rows, columns=COLUMNS)
        df.to_csv(OUTPUT_CSV, mode='a', header=False, index=False)
        cv2.imwrite(IMG_PATH, frame)

    time.sleep(0.5)  # diminui carga

cap.release()
print("✅ Detector finalizado.")
