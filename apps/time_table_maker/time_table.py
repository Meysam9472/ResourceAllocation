from fastapi import APIRouter, Depends, HTTPException, status
from .tasks import time_table_maker_task
from celery.result import AsyncResult
from celery_worker import celery_app

from sqlalchemy.ext.asyncio import AsyncSession
from models.users_models import User
from models.time_table_models import Teacher, Course
from dependencies import get_postgres_db_connection as get_db
from sqlalchemy.future import select
from sqlalchemy import delete, and_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from dependencies import get_current_user_token_data, require_admin_role

from schemas.time_table_schema import ScheduleRequest, TeacherRequest, CourseRequest


router = APIRouter(prefix="/schedule", tags=["Schedule"])


@router.post("/start")
async def start_scheduling(req: ScheduleRequest, current_user: int=Depends(get_current_user_token_data),
                           db: AsyncSession = Depends(get_db)):
    
    current_user_id = current_user.get("user_id")
    
    result = await db.execute(select(User.credit).where(User.id==current_user_id))
    user_credit = result.scalars().first()
    if user_credit is None or user_credit <= 0:
        raise HTTPException(status_code=400, detail="User's credit is not enough...")
    
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


@router.post("/add_teacher")
async def add_teacher(req: TeacherRequest, current_user: int=Depends(get_current_user_token_data),
                      db: AsyncSession = Depends(get_db)):
    try:
        user_id = current_user.get("user_id")
        
        # Create new teacher instance with correct fields
        new_teacher = Teacher(user_id=user_id, first_name=req.first_name, last_name=req.last_name,
                            available_times=req.available_times)
        db.add(new_teacher)
        
        # Save changes asynchronously
        await db.commit()
        # Refresh to get the generated ID
        await db.refresh(new_teacher)
        
        return {"result": f"Teacher: {new_teacher.first_name} {new_teacher.last_name} added successfully."}
    
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Teacher data violates database constraints."
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while adding the teacher."
        )
    

@router.get("/get_teachers")
async def get_teachers(current_user: int=Depends(get_current_user_token_data),
                       db: AsyncSession = Depends(get_db)):
    try:
        user_id = current_user.get("user_id")
        result = await db.execute(select(Teacher).where(Teacher.user_id==user_id))
        teachers = result.scalars().all()
        
        return {"teachers": teachers}
    
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while fetching teachers."
        )


@router.delete("/delete_teachers")
async def delete_teachers(id: int, current_user: int=Depends(get_current_user_token_data),
                          db: AsyncSession = Depends(get_db)):
    # 1. Extract user_id from token data
    user_id = current_user.get("user_id")
    try:
        # 2. Construct the delete query with ownership check
        query = (delete(Teacher).where(and_(Teacher.id == id, Teacher.user_id == user_id)))
        
        # 3. Execute the query
        result = await db.execute(query)
        
        # 4. Check if any row was actually deleted (rowcount)
        if result.rowcount == 0:
            # If no row was deleted, it means either the ID doesn't exist 
            # or it doesn't belong to the current user
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Teacher with id {id} not found or you don't have permission to delete it"
            )
            
        # 5. Commit the transaction
        await db.commit()
        
        return {"message": f"Teacher(id={id}) successfully deleted"}

    except HTTPException:
        # Re-raise FastAPI HTTP exceptions
        raise
    except Exception as e:
        # Rollback in case of unexpected database errors
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the teacher"
        )


@router.delete("/delete_courses")
async def delete_courses(id: int, current_user: int=Depends(get_current_user_token_data),
                         db: AsyncSession = Depends(get_db)):
    user_id = current_user.get("user_id")
    try:
        query = (delete(Course).where(and_(Course.id == id, Course.user_id == user_id)))
        
        result = await db.execute(query)
        
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course with id {id} not found or you don't have permission to delete it"
                )
            
        await db.commit()
        
        return {"message": f"Course(id={id}) successfully deleted"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the course"
        )
    

@router.get("/get_courses")
async def get_courses(current_user: int=Depends(get_current_user_token_data), 
                      db: AsyncSession = Depends(get_db)):
    try:
        user_id = current_user.get("user_id")
        result = await db.execute(select(Course).where(Course.user_id==user_id))
        courses = result.scalars().all()
        
        return {"courses": courses}
    
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while fetching courses."
        )


@router.post("/add_course")
async def add_course(req: CourseRequest, current_user: int=Depends(get_current_user_token_data),
                     db: AsyncSession = Depends(get_db)):
    try:
        user_id = current_user.get("user_id")
        name = req.name
        cohort = str(req.cohort)
        credits = req.credits
        
        new_course = Course(name=name, cohort=cohort, credits=credits, user_id=user_id)
        db.add(new_course)
        await db.commit()
        await db.refresh(new_course)
    
        return {"result": f"Course: {new_course.name} added successfully."}
    
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid data. Make sure referenced user exist."
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while adding the course.\n{e}"
        )
    


