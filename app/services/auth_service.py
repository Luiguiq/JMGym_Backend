from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.user_repository import get_user_by_email, get_user_by_dni, create_user
from app.schemas.user_schemas import (
    UserRegisterSchema,
    UserLoginSchema,
    UserOut,
    AuthResponse,
)
from app.security import hash_password, verify_password, create_access_token


def _build_user_out(user) -> UserOut:
    return UserOut(
        id=user.id_usuario,
        name=user.nombre_completo,
        email=user.correo,
        dni=user.dni,
        estado=user.estado.value if user.estado else "ACTIVO",
    )


def register_user(db: Session, data: UserRegisterSchema) -> AuthResponse:
    existing = get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado",
        )

    if data.dni:
        existing_dni = get_user_by_dni(db, data.dni)
        if existing_dni:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El DNI ya está registrado",
            )

    user = create_user(
        db,
        {
            "nombre_completo": data.name,
            "correo": data.email,
            "password_hash": hash_password(data.password),
            "dni": data.dni,
        },
    )

    token = create_access_token(data={"sub": user.correo})
    return AuthResponse(user=_build_user_out(user), token=token)


def login_user(db: Session, data: UserLoginSchema) -> AuthResponse:
    user = get_user_by_email(db, data.email)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    token = create_access_token(data={"sub": user.correo})
    return AuthResponse(user=_build_user_out(user), token=token)
