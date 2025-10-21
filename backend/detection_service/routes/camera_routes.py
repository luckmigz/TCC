from fastapi import APIRouter
from pydantic import BaseModel
from service.monitor_manager import manager

router = APIRouter()

class StartPayload(BaseModel):
    cnpj: str
    rtsp: str  # pode ser ID (ex: "0") ou URL RTSP
    interval_seconds: float = 60.0

@router.post("/start")
async def start_camera(payload: StartPayload):
    session = await manager.start(
        cnpj=payload.cnpj, rtsp=payload.rtsp, interval_seconds=payload.interval_seconds
    )
    return {"message": "started", "status": session.status()}

@router.post("/stop")
async def stop_camera(payload: StartPayload):
    stopped = await manager.stop(payload.cnpj)
    return {"message": "stopped" if stopped else "not_running"}

@router.get("/status/{cnpj}")
async def status_camera(cnpj: str):
    st = manager.status(cnpj)
    if not st:
        return {"message": "no session found"}
    return {"status": st}
