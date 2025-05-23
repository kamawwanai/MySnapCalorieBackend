from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import User, UserProfile, UserPlan
from app.schemas.profiles import UserProfile as UserProfileSchema
from app.schemas.profiles import UserProfileUpdate
from app.utils.dependencies import get_current_user
from app.utils.plan_calculator import build_nutrition_plan

router = APIRouter(
    prefix="/profiles",
    tags=["Profiles"]
)


@router.get("/me", response_model=UserProfileSchema)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить профиль текущего пользователя"""
    if not current_user.profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return current_user.profile


@router.put("/me", response_model=UserProfileSchema)
def update_my_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Обновить профиль текущего пользователя.
    Автоматически пересчитывает и обновляет план питания.
    """
    if not current_user.profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Получаем профиль из базы данных для обновления
    profile = db.query(UserProfile).filter(UserProfile.id == current_user.profile.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Обновляем профиль
    for key, value in profile_data.model_dump(exclude_unset=True).items():
        setattr(profile, key, value)

    # Пересчитываем и обновляем план питания
    delta_kg = abs(profile.goal_kg - profile.weight) if profile.goal_kg else 0
    plan_data = build_nutrition_plan(
        weight=profile.weight,
        height=profile.height,
        age=profile.age,
        gender=profile.gender,
        activity_multiplier=profile.activity_level,
        delta_kg=delta_kg,
        goal_type=profile.goal_type
    )

    # Обновляем или создаем план
    if current_user.plan:
        plan = db.query(UserPlan).filter(UserPlan.id == current_user.plan.id).first()
        if plan:
            for key, value in plan_data.items():
                setattr(plan, key, value)
    else:
        plan = UserPlan(user_id=current_user.id, **plan_data)
        db.add(plan)

    db.commit()
    return profile 