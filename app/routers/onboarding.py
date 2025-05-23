from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import User, UserProfile, UserPlan
from app.schemas.profiles import UserProfileCreate
from app.utils.dependencies import get_current_user
from app.utils.plan_calculator import build_nutrition_plan

router = APIRouter(
    prefix="/onboardingPlan",
    tags=["OnboardingPlan"]
)


@router.get("/status")
def get_onboarding_plan_status(current_user: User = Depends(get_current_user)):
    """
    Проверяет, завершил ли пользователь онбординг план.
    """
    return {"onboardingPlanCompleted": current_user.onboarding_plan_completed}


@router.post("/complete")
def complete_onboarding_plan(
    profile_data: UserProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Завершает онбординг план пользователя, создавая его профиль
    и устанавливая флаг onboarding_plan_completed.
    Также автоматически создает план питания.
    """
    # Проверяем, не создан ли уже профиль
    if current_user.profile is not None:
        raise HTTPException(
            status_code=400,
            detail="User profile already exists"
        )

    # Создаем профиль пользователя
    profile = UserProfile(**profile_data.model_dump(), user_id=current_user.id)
    db.add(profile)
    
    # Создаем план питания
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
    
    plan = UserPlan(user_id=current_user.id, **plan_data)
    db.add(plan)
    
    # Получаем свежий объект пользователя из текущей сессии
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Отмечаем онбординг как завершенный
    user.onboarding_plan_completed = True
    
    db.commit()
    db.refresh(profile)
    db.refresh(plan)
    db.refresh(user)
    
    return {
        "status": "success",
        "message": "Onboarding plan completed successfully",
        "profile": profile,
        "nutrition_plan": plan,
        "onboarding_completed": user.onboarding_plan_completed
    } 