from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PriorityLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ScheduleType(str, Enum):
    SAFE = "safe"
    INTEREST = "interest"
    BALANCED = "balanced"


class MonitorStatus(str, Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    COMPLETED = "completed"


class TimeSlot(BaseModel):
    day: str
    start_time: str = Field(..., pattern=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    end_time: str = Field(..., pattern=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")


class StudentProfile(BaseModel):
    student_id: str
    major: str
    current_credits: int
    completed_courses: List[str]
    gpa: float = Field(ge=0.0, le=4.0)
    graduation_year: int
    preferences: Dict[str, Any] = {}


class CourseInput(BaseModel):
    code: str
    name: str
    credits: int
    capacity: int
    current_enrollment: int
    prerequisites: List[str] = []
    corequisites: List[str] = []
    core_requirement: bool = False
    major_requirement: bool = False
    difficulty: float = Field(ge=1.0, le=5.0)
    time_slots: List[TimeSlot]


class GraduationRequirement(BaseModel):
    total_credits: int
    major_credits: int
    core_credits: int
    elective_credits: int
    required_courses: List[str]


class RecommendationRequest(BaseModel):
    student_profile: StudentProfile
    courses: List[CourseInput]
    graduation_requirements: GraduationRequirement


class CourseRecommendation(BaseModel):
    course_code: str
    course_name: str
    priority_score: float = Field(ge=0.0, le=1.0)
    fit_score: float = Field(ge=0.0, le=1.0)
    risk_score: float = Field(ge=0.0, le=1.0)
    priority_level: PriorityLevel
    recommendation_reason: str
    risk_warning: Optional[str] = None
    prerequisites_met: bool
    helps_graduation: bool
    enrollment_suggestion: str


class RecommendationResponse(BaseModel):
    recommendations: List[CourseRecommendation]
    generated_at: datetime


class StudentProfileForSchedule(BaseModel):
    student_id: str
    max_credits_per_semester: int = Field(default=18, ge=12, le=24)
    preferred_days: List[str] = []
    avoid_morning: bool = False
    avoid_evening: bool = False
    max_consecutive_classes: int = Field(default=3, ge=1, le=6)


class ScheduleRequest(BaseModel):
    student_profile: StudentProfileForSchedule
    courses: List[CourseInput]


class ScheduleAnalysis(BaseModel):
    has_conflicts: bool
    conflict_details: List[str] = []
    consecutive_classes: int
    max_gap_hours: float
    schedule_health_score: float = Field(ge=0.0, le=100.0)
    advantages: List[str] = []
    disadvantages: List[str] = []


class GeneratedSchedule(BaseModel):
    schedule_type: ScheduleType
    selected_courses: List[CourseInput]
    total_credits: int
    analysis: ScheduleAnalysis
    time_table: Dict[str, List[Dict[str, Any]]]


class ScheduleResponse(BaseModel):
    schedules: List[GeneratedSchedule]
    generated_at: datetime


class MonitorStartRequest(BaseModel):
    student_id: str
    course_codes: List[str]
    interval_seconds: int = Field(default=60, ge=30, le=600)


class CourseStatus(BaseModel):
    course_code: str
    capacity: int
    current_enrollment: int
    enrollment_ratio: float
    last_updated: datetime
    status_change: Optional[str] = None


class MonitorHistoryItem(BaseModel):
    monitor_id: str
    student_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: int
    courses_monitored: List[str]
    total_checks: int


class MonitorHistoryResponse(BaseModel):
    history: List[MonitorHistoryItem]
    total_count: int