from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.db import engine, Base
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.meals import router as meals_router
from app.routers.onboarding import router as onboarding_plan_router
from app.routers.plans import router as plans_router
from app.routers.profiles import router as profiles_router
from app.routers.classification import router as classification_router

# для разработки: создаём таблицы по описанным моделям
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CalorieCounter API",
    version="0.1.0",
    # Отключаем повторную валидацию для ускорения
    validate_all=False,
    # Настраиваем OpenAPI для более быстрой загрузки документации
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url=None  # Отключаем ReDoc для ускорения
)

# Настраиваем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# подключаем роуты
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(users_router)
app.include_router(meals_router)
app.include_router(onboarding_plan_router)
app.include_router(plans_router, tags=["Plans"])
app.include_router(profiles_router)
app.include_router(classification_router, prefix="/classification", tags=["Classification"])