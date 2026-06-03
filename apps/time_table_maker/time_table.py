from fastapi import APIRouter, Depends, HTTPException, status
from .tasks import time_table_maker_task
from celery.result import AsyncResult
from celery_worker import celery_app

from sqlalchemy.ext.asyncio import AsyncSession
from models.users_models import User
from models.time_table_models import Teacher, Course, UserTeacherCourseRelation
from dependencies import get_postgres_db_connection as get_db
from sqlalchemy.future import select
from sqlalchemy import delete, and_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from dependencies import get_current_user_token_data, require_admin_role

from schemas.time_table_schema import ScheduleRequest, TeacherRequest, CourseRequest
from schemas.time_table_schema import CourseUpdateSchema, TeacherUpdateSchema, RelationSchema


router = APIRouter(prefix="/schedule", tags=["Schedule"])


@router.post("/start")
async def start_scheduling(req: ScheduleRequest, current_user: dict=Depends(get_current_user_token_data),
                           db: AsyncSession = Depends(get_db)):
    
    current_user_id = current_user.get("user_id")
    
    result = await db.execute(select(User.credit).where(User.id==current_user_id))
    user_credit = result.scalars().first()
    if user_credit is None or user_credit <= 0:
        raise HTTPException(status_code=400, detail="User's credit is not enough...")
    
    task = time_table_maker_task.delay(req.teachers, req.courses, req.num_rooms,
                                       req.cohorts, req.days, req.hours, current_user_id, req.schedule_name)
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
async def add_teacher(req: TeacherRequest, current_user: dict=Depends(get_current_user_token_data),
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
async def get_teachers(current_user: dict=Depends(get_current_user_token_data),
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


@router.delete("/delete_teacher/{id}")
async def delete_teacher(id: int, current_user: dict=Depends(get_current_user_token_data),
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


@router.patch("/update_teacher/{id}") # Put ID in the URL path
async def update_teacher(
    id: int, 
    teacher_data: TeacherUpdateSchema, # Use Pydantic schema for request body
    current_user: dict = Depends(get_current_user_token_data),
    db: AsyncSession = Depends(get_db)
):
    user_id = current_user.get("user_id")
    
    try:
        teacher = await db.get(Teacher, id)
        
        # 1. Check if teacher exists FIRST to prevent AttributeError
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Teacher with id {id} not found"
            )
            
        # 2. Check ownership (403 Forbidden is more semantically correct here)
        if teacher.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this teacher"
            )
            
        # 3. Update fields if they are provided (not None)
        if teacher_data.first_name is not None:
            teacher.first_name = teacher_data.first_name
        if teacher_data.last_name is not None:
            teacher.last_name = teacher_data.last_name
        if teacher_data.available_times is not None:
            teacher.available_times = teacher_data.available_times
        
        await db.commit()
        await db.refresh(teacher) # Refresh to get updated data
        
        return teacher
        
    except HTTPException:
        # Re-raise HTTP exceptions so they don't get caught by the general Exception block
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the teacher"
        )


@router.patch("/update_course/{id}") # Put ID in the URL path
async def update_course(
    id: int, 
    course_data: CourseUpdateSchema, # Use Pydantic schema for request body
    current_user: dict = Depends(get_current_user_token_data),
    db: AsyncSession = Depends(get_db)
):
    
    user_id = current_user.get("user_id")
    
    try:
        course = await db.get(Course, id)
        
        # 1. Check if course exists FIRST to prevent AttributeError
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course with id {id} not found"
            )
            
        # 2. Check ownership (403 Forbidden is more semantically correct here)
        if course.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this course"
            )
            
        # 3. Update fields if they are provided (not None)
        if course_data.name is not None:
            course.name = course_data.name
        if course_data.credits is not None:
            course.credits = course_data.credits
        if course_data.cohort is not None:
            course.cohort = course_data.cohort
        
        await db.commit()
        await db.refresh(course) # Refresh to get updated data
        
        return course
        
    except HTTPException:
        # Re-raise HTTP exceptions so they don't get caught by the general Exception block
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while updating the course.{e}"
        )


@router.delete("/delete_course/{id}")
async def delete_course(id: int, current_user: dict=Depends(get_current_user_token_data),
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
async def get_courses(current_user: dict=Depends(get_current_user_token_data), 
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
async def add_course(req: CourseRequest, current_user: dict=Depends(get_current_user_token_data),
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
            detail=f"An unexpected error occurred while adding the course."
        )


@router.get("/get_relations")
async def get_relations(current_user: dict=Depends(get_current_user_token_data),
                        db: AsyncSession = Depends(get_db)):
    try:
        user_id = current_user.get("user_id")
        query = select(UserTeacherCourseRelation).where(UserTeacherCourseRelation.user_id==user_id)
        result = await db.execute(query)
        relations = result.scalars().all()
        
        return {"relations": relations}
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while fetching relations."
        )


@router.post("/add_relation")
async def add_relation(req: RelationSchema, current_user: dict=Depends(get_current_user_token_data),
                       db: AsyncSession = Depends(get_db)):
    try:
        user_id = current_user.get("user_id")
        teacher_id = req.teacher_id
        course_id = req.course_id
        new_relation = UserTeacherCourseRelation(user_id=user_id, teacher_id=teacher_id, 
                                                 course_id=course_id)
        db.add(new_relation)
        await db.commit()
        await db.refresh(new_relation)
        
        return {"result": f"Relation: {new_relation.id} added successfully."}
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while adding the relation."
        )


@router.delete("/delete_relation/{id}")
async def delete_relation(id: int, current_user: dict=Depends(get_current_user_token_data),
                          db: AsyncSession = Depends(get_db)):
    
    user_id = current_user.get("user_id")
    try:
        query = (delete(UserTeacherCourseRelation).where(and_(UserTeacherCourseRelation.id == id,
                                                              UserTeacherCourseRelation.user_id == user_id)))
        
        result = await db.execute(query)
        
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Relation with id {id} not found or you don't have permission to delete it"
                )
            
        await db.commit()
        
        return {"message": f"Relation(id={id}) successfully deleted"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the relation"
        )

