from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.db.models import User, UserProfile, UserPlan
from app.schemas.plans import UserPlan as UserPlanSchema
from app.utils.plan_calculator import build_nutrition_plan
from app.utils.dependencies import get_current_user

router = APIRouter()


@router.get("/plans/me", response_model=UserPlanSchema)
def get_my_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить текущий план питания пользователя"""
    plan = db.query(UserPlan).filter(UserPlan.user_id == current_user.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="План питания не найден")
    return plan


@router.post("/plans/calculate", response_model=UserPlanSchema)
def calculate_and_save_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Рассчитать и сохранить план питания на основе профиля пользователя"""
    # Получаем профиль пользователя
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Профиль пользователя не найден")

    # Определяем delta_kg на основе goal_kg из профиля
    delta_kg = abs(profile.goal_kg - profile.weight) if profile.goal_kg else 0

    # Рассчитываем план
    plan_data = build_nutrition_plan(
        weight=profile.weight,
        height=profile.height,
        age=profile.age,
        gender=profile.gender,
        activity_multiplier=profile.activity_level / 10,  # Преобразуем 1-7 в 0.1-0.7
        delta_kg=delta_kg,
        goal_type=profile.goal_type
    )

    # Проверяем, существует ли уже план
    existing_plan = db.query(UserPlan).filter(UserPlan.user_id == current_user.id).first()
    
    if existing_plan:
        # Обновляем существующий план
        for key, value in plan_data.items():
            setattr(existing_plan, key, value)
        plan = existing_plan
    else:
        # Создаем новый план
        plan = UserPlan(user_id=current_user.id, **plan_data)
        db.add(plan)

    db.commit()
    db.refresh(plan)
    return plan


@router.delete("/plans/me", status_code=204)
def delete_my_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удалить текущий план питания"""
    plan = db.query(UserPlan).filter(UserPlan.user_id == current_user.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="План питания не найден")
    
    db.delete(plan)
    db.commit()
    return None 