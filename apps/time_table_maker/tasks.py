from .services.time_table_service import time_table_maker
from celery_worker import celery_app


@celery_app.task(bind=True, max_retries=5)
def time_table_maker_task(self, teachers_data, courses_data, num_rooms, cohorts, days, hours):
    result = time_table_maker(teachers_data, courses_data, num_rooms, cohorts, days, hours, 
                              False, self.request.id)
    return result