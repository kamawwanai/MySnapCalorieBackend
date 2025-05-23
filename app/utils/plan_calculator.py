from app.db.models import Gender, GoalType

def calculate_bmr(weight_kg: float, height_cm: float, age_years: int, gender: Gender) -> float:
    """
    Формула Миффлина–Сан Жеора:
    Мужчины: +5, женщины: –161
    """
    if gender == Gender.MALE:
        return 10 * weight_kg + 6.25 * height_cm - 5 * age_years + 5
    else:
        return 10 * weight_kg + 6.25 * height_cm - 5 * age_years - 161


def calculate_tdee(bmr: float, activity_multiplier: float) -> float:
    """
    TDEE = BMR × множитель активности
    """
    return bmr * activity_multiplier


def calculate_weeks(delta_kg: float, rate_kg_per_week: float = 0.5) -> float:
    """
    Определяем длительность в неделях, минимум 1 неделя
    """
    return max(delta_kg / rate_kg_per_week, 1.0)


def calculate_daily_adjustment(delta_kg: float, weeks: float) -> float:
    """
    Суточный дефицит/избыток калорий
    1 кг жира ≈ 7700 ккал
    """
    return (delta_kg * 7700) / (weeks * 7)


def calculate_target_calories(
    tdee: float,
    delta_kg: float,
    goal_type: GoalType
) -> tuple[float, int]:
    """
    Возвращает (целевая калорийность, длительность в неделях)
    """
    if goal_type == GoalType.LOSS:
        weeks = calculate_weeks(delta_kg)
        deficit = calculate_daily_adjustment(delta_kg, weeks)
        return tdee - deficit, int(weeks)
    elif goal_type == GoalType.GAIN:
        weeks = calculate_weeks(delta_kg)
        surplus = calculate_daily_adjustment(delta_kg, weeks)
        return tdee + surplus, int(weeks)
    else:  # maintain
        return tdee, 0


def calculate_macros(
    target_calories: float,
    protein_ratio: float = 0.25,
    fat_ratio: float = 0.30
) -> tuple[float, float, float]:
    """
    Распределение макросов:
    Белки и углеводы дают 4 ккал/г, жиры — 9 ккал/г.
    """
    protein_kcal = target_calories * protein_ratio
    fat_kcal = target_calories * fat_ratio
    carb_kcal = target_calories - protein_kcal - fat_kcal

    protein_g = protein_kcal / 4
    fat_g = fat_kcal / 9
    carbs_g = carb_kcal / 4

    return protein_g, fat_g, carbs_g


def calculate_smart_goal(delta_kg: float, goal_type: GoalType) -> tuple[str, int]:
    """
    Возвращает кортеж (SMART-цель, длительность в неделях).
    """
    if goal_type == GoalType.LOSS and delta_kg > 0:
        weeks = max(int(delta_kg / 0.5), 1)
        text = f"Похудеть на {delta_kg:.1f} кг за {weeks} недель"
    elif goal_type == GoalType.GAIN and delta_kg > 0:
        weeks = max(int(delta_kg / 0.5), 1)
        text = f"Набрать {delta_kg:.1f} кг за {weeks} недель"
    else:
        weeks = 0
        text = "Поддерживать вес"
    return text, weeks


def get_activity_multiplier(activity_level: int) -> float:
    """
    Преобразует уровень активности (1-7) в соответствующий множитель
    1 -> 1.2 (Сидячий образ жизни)
    2 -> 1.375 (Легкая активность)
    3 -> 1.4625 (Умеренная активность)
    4 -> 1.55 (Средняя активность)
    5 -> 1.6375 (Активный образ жизни)
    6 -> 1.725 (Очень активный образ жизни)
    7 -> 1.9 (Профессиональный спортсмен)
    """
    multipliers = {
        1: 1.2,
        2: 1.375,
        3: 1.4625,
        4: 1.55,
        5: 1.6375,
        6: 1.725,
        7: 1.9
    }
    return multipliers[activity_level]


def build_nutrition_plan(
    weight: float,
    height: float,
    age: int,
    gender: Gender,
    activity_multiplier: int,
    delta_kg: float,
    goal_type: GoalType,
    protein_ratio: float = 0.25,
    fat_ratio: float = 0.30
) -> dict:
    """
    Создает план питания на основе параметров пользователя
    """
    bmr = calculate_bmr(weight, height, age, gender)
    activity_multiplier = get_activity_multiplier(activity_multiplier)
    tdee = calculate_tdee(bmr, activity_multiplier)
    target_cals, duration_weeks = calculate_target_calories(tdee, delta_kg, goal_type)
    protein, fat, carbs = calculate_macros(target_cals, protein_ratio, fat_ratio)
    goal_text, duration_weeks = calculate_smart_goal(delta_kg, goal_type)

    return {
        "calories_per_day": round(target_cals),
        "protein_g": round(protein),
        "fat_g": round(fat),
        "carb_g": round(carbs),
        "duration_weeks": duration_weeks,
        "smart_goal": goal_text
    } 