from fastapi import APIRouter
from .tasks import time_table_maker_task
from celery.result import AsyncResult
from celery_worker import celery_app

from dependencies import get_current_user_token_data, require_admin_role

from schemas.time_table_schema import ScheduleRequest


router = APIRouter(prefix="/schedule", tags=["Schedule"])


@router.post("/start")
def start_scheduling(req: ScheduleRequest, current_user: int=Depends(get_current_user_token_data)):
    
    current_user_id = current_user.get("user_id")
    
    # TODO: Check Credit of user here
    
    task = time_table_maker_task.delay(req.teachers, req.courses, req.num_rooms,
                                       req.cohorts, req.days, req.hours, current_user_id)
    return {"task_id": task.id, "message": "Task started in background."}


@router.get("/status/{task_id}")
def get_schedule_status(task_id: str, current_admin: dict = Depends(require_admin_role)):
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
    