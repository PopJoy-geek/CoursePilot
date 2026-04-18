from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List
from app.seat_monitor import start_monitor, get_monitor_history, export_monitor_history_csv

router = APIRouter()


class MonitorStartRequest(BaseModel):
    student_id: str
    course_codes: List[str]
    interval_seconds: int = Field(default=60, ge=30, le=600)


@router.post("/start")
def start_monitoring(request: MonitorStartRequest):
    try:
        result = start_monitor(request.student_id, request.course_codes)
        return {
            "message": "monitor started",
            "monitor": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
def monitor_history():
    try:
        history = get_monitor_history()
        return {
            "history": history,
            "total_count": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export")
def export_history():
    try:
        filepath = export_monitor_history_csv()
        return {
            "message": "export successful",
            "file_path": filepath
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))