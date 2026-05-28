from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.models.admin_model import Administrador
from app.security import get_db, hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth/admin", tags=["Admin Auth"])


class AdminLoginSchema(BaseModel):
    email: EmailStr = Field(validation_alias="correo_institucional")
    password: str

    model_config = {"populate_by_name": True}


class AdminRegisterSchema(BaseModel):
    nombre: str
    email: EmailStr = Field(validation_alias="correo_institucional")
    password: str

    model_config = {"populate_by_name": True}


class AdminOut(BaseModel):
    id: int
    nombre: str
    email: str
    estado: str


class AdminAuthResponse(BaseModel):
    user: AdminOut
    token: str


@router.post("/register", response_model=AdminAuthResponse)
def admin_register(data: AdminRegisterSchema, db: Session = Depends(get_db)):
    existing = (
        db.query(Administrador)
        .filter(Administrador.correo_institucional == data.email)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado",
        )

    admin = Administrador(
        nombre=data.nombre,
        correo_institucional=data.email,
        password_hash=hash_password(data.password),
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)

    token = create_access_token(data={"sub": admin.correo_institucional})
    return AdminAuthResponse(
        user=AdminOut(
            id=admin.id_admin,
            nombre=admin.nombre,
            email=admin.correo_institucional,
            estado=admin.estado or "ACTIVO",
        ),
        token=token,
    )


@router.post("/login", response_model=AdminAuthResponse)
def admin_login(data: AdminLoginSchema, db: Session = Depends(get_db)):
    admin = (
        db.query(Administrador)
        .filter(Administrador.correo_institucional == data.email)
        .first()
    )
    if not admin or not verify_password(data.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    token = create_access_token(data={"sub": admin.correo_institucional})
    return AdminAuthResponse(
        user=AdminOut(
            id=admin.id_admin,
            nombre=admin.nombre,
            email=admin.correo_institucional,
            estado=admin.estado or "ACTIVO",
        ),
        token=token,
    )
