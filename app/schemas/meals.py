from datetime import datetime, date
from pydantic import BaseModel, Field
from typing import List, Optional
from app.db.models import MealType


class MealRecordBase(BaseModel):
    datetime: datetime
    calories: float = Field(..., gt=0, description="Calories in kcal")
    proteins: float = Field(..., ge=0, description="Proteins in grams")
    fats: float = Field(..., ge=0, description="Fats in grams")
    carbs: float = Field(..., ge=0, description="Carbohydrates in grams")
    meal_type: MealType = Field(default=MealType.OTHER, description="Type of meal")
    image_path: Optional[str] = None


class MealRecordCreate(MealRecordBase):
    pass


class MealRecord(MealRecordBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class DayMealsSummary(BaseModel):
    date: date
    total_calories: float
    meals: List[MealRecord]

    class Config:
        from_attributes = True 