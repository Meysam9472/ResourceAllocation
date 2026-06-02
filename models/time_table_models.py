import enum
from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from database import Base


class Teacher(Base):
    __tablename__ = "teachers" # name of the table in the real database

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    available_times = Column(JSON, nullable=True)

    # relationship is a pythonic solution for moving between objects of connected tables
    user = relationship("User", back_populates="teachers")
    user_teacher_course_relations = relationship("UserTeacherCourseRelation", back_populates="teachers")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    cohort = Column(String, nullable=False)
    credits = Column(Integer, nullable=False)

    user = relationship("User", back_populates="courses")
    user_teacher_course_relations = relationship("UserTeacherCourseRelation", back_populates="courses")


class UserTeacherCourseRelation(Base):
    __tablename__ = "user_teacher_course_relations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    
    user = relationship("User", back_populates="user_teacher_course_relations")
    teacher = relationship("Teacher", back_populates="user_teacher_course_relations")
    course = relationship("Course", back_populates="user_teacher_course_relations")