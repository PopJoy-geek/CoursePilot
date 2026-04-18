from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from app.scheduler import generate_all_schedules

router = APIRouter()


class StudentProfileForSchedule(BaseModel):
    student_id: str
    max_credits_per_semester: int = Field(default=18, ge=12, le=24)


class ScheduleRequest(BaseModel):
    student_profile: StudentProfileForSchedule
    courses: List[Dict[str, Any]]


@router.post("")
def generate_schedules(request: ScheduleRequest):
    try:
        result = generate_all_schedules(
            request.courses,
            request.student_profile.max_credits_per_semester
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"课表生成失败: {str(e)}")