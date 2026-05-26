# We have to add all models here because when we want to define relationships between 
# models(This cause models in different files detect each other)
from database import Base
from .time_table_models import Teacher, Course
from .users_models import User