from pydantic import BaseModel
from datetime import datetime


class UserPlanBase(BaseModel):
    calories_per_day: float
    protein_g: float
    fat_g: float
    carb_g: float
    duration_weeks: int
    smart_goal: str


class UserPlanCreate(UserPlanBase):
    pass


class UserPlan(UserPlanBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True 