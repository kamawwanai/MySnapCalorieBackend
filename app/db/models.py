# app/db/models.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

# базовый класс для всех моделей
Base = declarative_base()


class GoalType(str, enum.Enum):
    LOSS = "loss"
    MAINTAIN = "maintain"
    GAIN = "gain"


class Gender(enum.IntEnum):
    FEMALE = 0
    MALE = 1


class MealType(enum.IntEnum):
    BREAKFAST = 1
    MORNING_SNACK = 2
    LUNCH = 3
    AFTERNOON_SNACK = 4
    DINNER = 5
    EVENING_SNACK = 6
    WORKOUT = 7
    OTHER = 8


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow)
    onboarding_plan_completed = Column(Boolean, nullable=False, default=False)
    
    # Relationship with MealRecord
    meal_records = relationship("MealRecord", back_populates="user")
    # Relationship with UserProfile
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    # Relationship with UserPlan
    plan = relationship("UserPlan", back_populates="user", uselist=False)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    username = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(Integer, nullable=False)  # 0 - female, 1 - male
    height = Column(Integer, nullable=False)  # in centimeters
    weight = Column(Float, nullable=False)   # in kilograms
    activity_level = Column(Integer, nullable=False)  # 1-7
    goal_type = Column(Enum(GoalType), nullable=False)
    goal_kg = Column(Float, nullable=True)   # in kilograms

    # Relationship with User
    user = relationship("User", back_populates="profile")


class MealRecord(Base):
    __tablename__ = "meal_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    calories = Column(Float, nullable=False)  # в ккал
    proteins = Column(Float, nullable=False)  # в граммах
    fats = Column(Float, nullable=False)     # в граммах
    carbs = Column(Float, nullable=False)    # в граммах
    meal_type = Column(Integer, nullable=False, default=MealType.OTHER)  # тип приема пищи
    image_path = Column(String, nullable=True)  # путь к изображению
    
    # Relationship with User
    user = relationship("User", back_populates="meal_records")


class UserPlan(Base):
    __tablename__ = "user_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    calories_per_day = Column(Float, nullable=False)
    protein_g = Column(Float, nullable=False)
    fat_g = Column(Float, nullable=False)
    carb_g = Column(Float, nullable=False)
    duration_weeks = Column(Integer, nullable=False)
    smart_goal = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship with User
    user = relationship("User", back_populates="plan")
