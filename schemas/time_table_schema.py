from pydantic import BaseModel
from typing import Optional, List, Dict


class ScheduleRequest(BaseModel):
    teachers: Dict
    courses: Dict
    num_rooms: int
    cohorts: List
    days: List
    hours: List


class TeacherRequest(BaseModel):
    first_name: str
    last_name: str
    available_times: List


class CourseRequest(BaseModel):
    name: str
    credits: int
    cohort: str


class TeacherUpdateSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    available_times: Optional[List[int]] = None


class CourseUpdateSchema(BaseModel):
    name: Optional[str] = None
    credits: Optional[int] = None
    cohort: Optional[str] = None