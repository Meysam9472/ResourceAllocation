from fastapi import APIRouter
from pydantic import BaseModel
from .tasks import time_table_maker_task
from celery.result import AsyncResult
from celery_worker import celery_app


router = APIRouter()


class ScheduleRequest(BaseModel):
    teachers: dict
    courses: dict
    num_rooms: int
    cohorts: list
    days: list
    hours: list


@router.post("/schedule/start")
def start_scheduling(req: ScheduleRequest):
    task = time_table_maker_task.delay(req.teachers, req.courses, req.num_rooms,
                                       req.cohorts, req.days, req.hours)
    return {"task_id": task.id, "message": "Task started in background."}


@router.get("/schedule/status/{task_id}")
def get_schedule_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    
    if task_result.state == 'PENDING':
        return {"status": "Task is pending in a queue"}
    elif task_result.state == 'STARTED' or task_result.state == 'PROGRESS':
        return {"status": "Task started..."}
    elif task_result.state == 'SUCCESS':
        return {"status": "Task finished successfully", "result": task_result.result}
    elif task_result.state == 'FAILURE':
        return {"status": "Task faild!", "error": str(task_result.info)}
    else:
        return {"status": task_result.state}
    