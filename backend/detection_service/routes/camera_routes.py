from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from service.detector_utils import gerar_deteccoes_continuas
from service.mongo_sender import enviar_dados_crus
import asyncio

router = APIRouter()

# Modelo de dados para a requisição
class CameraRequest(BaseModel):
    cnpj: str
    rtsp_url: str

# Variável global para controlar o estado do loop
is_running = False

async def loop_captura(cnpj: str, rtsp_url: str):
    """
    Loop contínuo que roda enquanto o microserviço está ativo,
    capturando e enviando dados (de 1 em 1 minuto, conforme detector_utils).
    """
    global is_running
    is_running = True

    print(f"🎥 Iniciando captura para {cnpj} — {rtsp_url}")

    try:
        # Usa o gerador para obter detecções no intervalo definido
        # O intervalo de 60 segundos (1 min) é definido na chamada abaixo
        async for detections, model_names in gerar_deteccoes_continuas(rtsp_url, intervalo_segundos=60):
            if not is_running:
                print("🛑 Captura interrompida pela rota /stop.")
                break

            # Formata os dados crus para JSON
            detections_json = []
            if detections.tracker_id is not None: # Garante que há detecções
                for xyxy, conf, cls, track_id in zip(
                    detections.xyxy, detections.confidence, detections.class_id, detections.tracker_id
                ):
                    x1, y1, x2, y2 = map(int, xyxy)
                    detections_json.append({
                        "track_id": int(track_id),
                        "label": model_names[int(cls)],
                        "confidence": float(conf),
                        "x1": x1, "y1": y1, "x2": x2, "y2": y2
                    })

            # Envia os dados crus para o MongoDB
            if detections_json:
                await enviar_dados_crus(cnpj, rtsp_url, detections_json)
            else:
                print(f"📦 Nenhum objeto de interesse detectado para {cnpj}.")

    except ConnectionRefusedError as e:
        print(f"❌ Erro de conexão com a câmera {rtsp_url}: {e}")
        is_running = False
    except Exception as e:
        print(f"⚠️ Erro inesperado no loop de captura: {e}")
        is_running = False


@router.post("/start")
async def start_camera(data: CameraRequest, background_tasks: BackgroundTasks):
    """
    Inicia o monitoramento. Recebe CNPJ e RTSP_URL.
    """
    global is_running
    if is_running:
        return {"status": "already_running", "message": "O serviço já está em execução."}

    # Adiciona o loop_captura como uma tarefa de fundo
    background_tasks.add_task(loop_captura, data.cnpj, data.rtsp_url)
    return {"status": "started", "cnpj": data.cnpj, "camera": data.rtsp_url}

@router.post("/stop")
async def stop_camera():
    """
    Para o loop de captura.
    """
    global is_running
    if not is_running:
        return {"status": "already_stopped"}

    is_running = False
    return {"status": "stopped"}