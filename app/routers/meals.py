from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
import os
import shutil
from pathlib import Path

from app.db.session import get_db
from app.db.models import MealRecord
from app.schemas.meals import MealRecordCreate, MealRecord as MealRecordSchema, DayMealsSummary
from app.utils.dependencies import get_current_user
from app.db.models import User

router = APIRouter(prefix="/meals", tags=["meals"])

# Создаем директорию для изображений, если она не существует
MEAL_IMAGES_DIR = Path("app/static/meal_images")
MEAL_IMAGES_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/", response_model=MealRecordSchema)
def create_meal_record(
    meal: MealRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создание новой записи о приеме пищи (image_path — строка, загрузка файла отдельно)"""
    db_meal = MealRecord(
        **meal.model_dump(),
        user_id=current_user.id
    )
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    return db_meal


@router.get("/", response_model=List[MealRecordSchema])
def get_user_meals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение всех записей о приемах пищи текущего пользователя"""
    return db.query(MealRecord).filter(MealRecord.user_id == current_user.id).all()


@router.get("/grouped", response_model=List[DayMealsSummary])
def get_grouped_meals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение записей о приемах пищи, сгруппированных по дате.
    Для каждой даты возвращается список приемов пищи и общая сумма калорий.
    Даты отсортированы в порядке убывания (сначала последние).
    """
    # Получаем все приемы пищи пользователя
    meals = db.query(MealRecord).filter(
        MealRecord.user_id == current_user.id
    ).order_by(MealRecord.datetime.desc()).all()

    # Группируем приемы пищи по дате
    grouped_meals = {}
    for meal in meals:
        meal_date = meal.datetime.date()
        if meal_date not in grouped_meals:
            grouped_meals[meal_date] = {
                'date': meal_date,
                'total_calories': 0,
                'meals': []
            }
        grouped_meals[meal_date]['meals'].append(meal)
        grouped_meals[meal_date]['total_calories'] += meal.calories

    # Преобразуем в список и сортируем по дате (убывание)
    result = [DayMealsSummary(**day_data) for day_data in grouped_meals.values()]
    result.sort(key=lambda x: x.date, reverse=True)

    return result


@router.get("/{meal_id}", response_model=MealRecordSchema)
def get_meal_record(
    meal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение конкретной записи о приеме пищи"""
    meal = db.query(MealRecord).filter(
        MealRecord.id == meal_id,
        MealRecord.user_id == current_user.id
    ).first()
    
    if meal is None:
        raise HTTPException(status_code=404, detail="Meal record not found")
    
    return meal 