from pydantic import BaseModel, Field, conint
from enum import IntEnum, Enum
from typing import Optional


class GoalType(str, Enum):
    LOSS = "loss"
    MAINTAIN = "maintain"
    GAIN = "gain"


class Gender(IntEnum):
    FEMALE = 0
    MALE = 1


class UserProfileBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    age: int = Field(..., ge=0, le=150)
    gender: Gender
    height: int = Field(..., ge=0, le=300)  # в сантиметрах
    weight: float = Field(..., ge=0, le=500)  # в килограммах
    activity_level: conint(ge=1, le=7)  # 1-7
    goal_type: GoalType
    goal_kg: Optional[float] = Field(None, ge=0, le=500)  # в килограммах


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(UserProfileBase):
    username: Optional[str] = Field(None, min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    age: Optional[int] = Field(None, ge=0, le=150)
    gender: Optional[Gender] = None
    height: Optional[int] = Field(None, ge=0, le=300)
    weight: Optional[float] = Field(None, ge=0, le=500)
    activity_level: Optional[conint(ge=1, le=7)] = None
    goal_type: Optional[GoalType] = None
    goal_kg: Optional[float] = Field(None, ge=0, le=500)


class UserProfile(UserProfileBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True 