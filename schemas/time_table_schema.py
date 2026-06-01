from pydantic import BaseModel
from typing import List

class ScheduleRequest(BaseModel):
    teachers: dict
    courses: dict
    num_rooms: int
    cohorts: list
    days: list
    hours: list


class TeacherRequest(BaseModel):
    first_name: str
    last_name: str
    available_times: List


class CourseRequest(BaseModel):
    name: str
    credits: int
    cohort: str