# service/monitor_manager.py
import asyncio
from typing import Dict, Optional, Any, List
from datetime import datetime

from service.detector_utils import gerar_deteccoes_periodicas
from service.mongo_sender import enviar_dados_crus


class MonitorSession:
    def __init__(self, cnpj: str, rtsp: str, interval_seconds: float = 60.0):
        self.cnpj = cnpj
        self.rtsp = rtsp
        self.interval_seconds = interval_seconds
        self.task: Optional[asyncio.Task] = None
        self.started_at: Optional[datetime] = None
        self.last_save_at: Optional[datetime] = None
        self.frames_ok: int = 0
        self.running: bool = False

    def status(self) -> Dict[str, Any]:
        return {
            "cnpj": self.cnpj,
            "rtsp": self.rtsp,
            "running": self.running,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "last_save_at": self.last_save_at.isoformat() if self.last_save_at else None,
            "frames_processed": self.frames_ok,
            "interval_seconds": self.interval_seconds,
        }


class MonitorManager:
    def __init__(self):
        self._sessions: Dict[str, MonitorSession] = {}

    def get(self, cnpj: str) -> Optional[MonitorSession]:
        return self._sessions.get(cnpj)

    async def start(self, cnpj: str, rtsp: str, interval_seconds: float = 60.0) -> MonitorSession:
        session = self._sessions.get(cnpj)
        if session and session.running:
            if session.rtsp != rtsp:
                session.rtsp = rtsp
            return session

        session = MonitorSession(cnpj, rtsp, interval_seconds)
        self._sessions[cnpj] = session
        session.running = True
        session.started_at = datetime.utcnow()

        async def _worker():
            try:
                # Gerador leve: YOLO + LLaMA
                async for detections, nomes, visao_llama in gerar_deteccoes_periodicas(
                    intervalo_segundos=session.interval_seconds
                ):
                    # YOLO → monta lista de detecções
                    raw_list: List[Dict[str, Any]] = []
                    for xyxy, conf, cls, tid in zip(
                        getattr(detections, "xyxy", []),
                        getattr(detections, "confidence", []),
                        getattr(detections, "class_id", []),
                        getattr(detections, "tracker_id", []),
                    ):
                        x1, y1, x2, y2 = [int(v) for v in xyxy]
                        label = nomes.get(int(cls), "desconhecido")
                        raw_list.append({
                            "label": label,
                            "confidence": float(conf),
                            "bbox": [x1, y1, x2, y2],
                            "track_id": int(tid) if tid is not None else None,
                        })

                    # Envia ambas as visões para o banco
                    await enviar_dados_crus(session.cnpj, session.rtsp, raw_list, visao_llama)

                    session.frames_ok += 1
                    session.last_save_at = datetime.utcnow()

            except asyncio.CancelledError:
                pass
            except Exception as e:
                print(f"❌ Worker {session.cnpj} encerrou por erro: {e}")
            finally:
                session.running = False

        session.task = asyncio.create_task(_worker(), name=f"worker-{cnpj}")
        return session

    async def stop(self, cnpj: str) -> bool:
        session = self._sessions.get(cnpj)
        if not session or not session.task:
            return False
        if not session.task.done():
            session.task.cancel()
            try:
                await session.task
            except asyncio.CancelledError:
                pass
        session.running = False
        return True

    def status(self, cnpj: str) -> Optional[Dict[str, Any]]:
        session = self._sessions.get(cnpj)
        return session.status() if session else None


# Instância global para uso no sistema
manager = MonitorManager()
