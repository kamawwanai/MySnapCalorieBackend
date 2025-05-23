from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.auth import UserRead
from app.db.models import User
from app.utils.dependencies import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)):
    """
    Возвращает данные текущего пользователя,
    извлечённого из JWT-токена.
    """
    return current_user
