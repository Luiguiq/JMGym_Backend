from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from app.models.user_model import Usuario
from app.models.reservation_model import Reserva
from app.security import get_db, get_current_admin, hash_password
from app.enum.user_enums import EstadoUsuario

router = APIRouter(prefix="/users", tags=["User Management"])


class UserUpdateSchema(BaseModel):
    nombre_completo: Optional[str] = None
    dni: Optional[str] = None
    correo: Optional[str] = None
    telefono: Optional[str] = None
    password: Optional[str] = None


class UserCreateFromAdminSchema(BaseModel):
    nombre_completo: str
    dni: str
    correo: str
    telefono: Optional[str] = None
    password: str = "cliente123"


class UserResponseSchema(BaseModel):
    model_config = {"from_attributes": True}

    id_usuario: int
    nombre_completo: str
    dni: str
    correo: str
    telefono: Optional[str] = None
    estado: str
    fecha_registro: Optional[datetime] = None


class UserReservationSchema(BaseModel):
    model_config = {"from_attributes": True}

    id_reserva: int
    id_clase: int
    estado_reserva: str
    fecha_reserva: Optional[datetime] = None
    fecha_clase: Optional[datetime] = None
    monto: float


@router.get("", response_model=list[UserResponseSchema])
def list_users(db: Session = Depends(get_db), admin: Session = Depends(get_current_admin)):
    return db.query(Usuario).all()


@router.get("/{user_id}", response_model=UserResponseSchema)
def get_user(user_id: int, db: Session = Depends(get_db), admin: Session = Depends(get_current_admin)):
    user = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return user


@router.put("/{user_id}", response_model=UserResponseSchema)
def update_user(user_id: int, data: UserUpdateSchema, db: Session = Depends(get_db), admin: Session = Depends(get_current_admin)):
    user = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    update_data = data.model_dump(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["password_hash"] = hash_password(update_data.pop("password"))

    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


@router.post("/register-by-admin", response_model=UserResponseSchema, status_code=201)
def register_user_by_admin(data: UserCreateFromAdminSchema, db: Session = Depends(get_db), admin: Session = Depends(get_current_admin)):
    existing = db.query(Usuario).filter(
        (Usuario.correo == data.correo) | (Usuario.dni == data.dni)
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El correo o DNI ya están registrados")

    user = Usuario(
        nombre_completo=data.nombre_completo,
        dni=data.dni,
        correo=data.correo,
        telefono=data.telefono,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{user_id}/toggle-block")
def toggle_user_block(user_id: int, db: Session = Depends(get_db), admin: Session = Depends(get_current_admin)):
    user = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    user.estado = EstadoUsuario.BLOQUEADO if user.estado == EstadoUsuario.ACTIVO else EstadoUsuario.ACTIVO
    db.commit()
    return {"message": f"Usuario {'bloqueado' if user.estado == EstadoUsuario.BLOQUEADO else 'desbloqueado'} correctamente"}


@router.get("/{user_id}/reservations", response_model=list[UserReservationSchema])
def get_user_reservations(user_id: int, db: Session = Depends(get_db), admin: Session = Depends(get_current_admin)):
    user = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return db.query(Reserva).filter(Reserva.id_usuario == user_id).all()


@router.get("/stats/totals")
def get_user_stats(db: Session = Depends(get_db), admin: Session = Depends(get_current_admin)):
    total = db.query(Usuario).count()
    activos = db.query(Usuario).filter(Usuario.estado == EstadoUsuario.ACTIVO).count()
    bloqueados = db.query(Usuario).filter(Usuario.estado == EstadoUsuario.BLOQUEADO).count()
    return {"total": total, "activos": activos, "bloqueados": bloqueados}
