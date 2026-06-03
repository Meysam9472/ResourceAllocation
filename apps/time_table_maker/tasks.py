from .services.time_table_service import time_table_maker
from celery_worker import celery_app
from celery.utils.log import get_task_logger

# Create a logger for this module
logger = get_task_logger(__name__)


@celery_app.task(bind=True, max_retries=5)
def time_table_maker_task(self, teachers_data, courses_data, num_rooms, cohorts, days, hours, 
                          user_id, schedule_name):
    result = time_table_maker(teachers_data, courses_data, num_rooms, cohorts, days, hours, 
                              False, self.request.id, user_id, logger, schedule_name)
    return result