from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.user_schemas import ForgotPasswordRequest, ResetPasswordRequest
from app.security import get_db
from app.services.reset_password_service import solicitar_restablecimiento, restablecer_contrasena

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    return solicitar_restablecimiento(db, data.correo)


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    return restablecer_contrasena(db, data.token, data.password)
