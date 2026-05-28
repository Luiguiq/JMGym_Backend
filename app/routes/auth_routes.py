from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.user_schemas import UserRegisterSchema, UserLoginSchema, AuthResponse
from app.security import get_db
from app.services.auth_service import register_user, login_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=AuthResponse)
def register(data: UserRegisterSchema, db: Session = Depends(get_db)):
    return register_user(db, data)


@router.post("/login", response_model=AuthResponse)
def login(data: UserLoginSchema, db: Session = Depends(get_db)):
    return login_user(db, data)
