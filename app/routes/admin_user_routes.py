from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from app.models.admin_model import Administrador
from app.security import get_db, get_current_admin, hash_password

router = APIRouter(prefix="/admin/users", tags=["Admin Management"])


class AdminCreateSchema(BaseModel):
    nombre: str
    correo_institucional: str
    password: str


class AdminResponseSchema(BaseModel):
    model_config = {"from_attributes": True}

    id_admin: int
    nombre: str
    correo_institucional: str
    estado: str
    fecha_creacion: Optional[datetime] = None


class AdminListSchema(BaseModel):
    model_config = {"from_attributes": True}

    id_admin: int
    nombre: str
    correo_institucional: str
    estado: str


@router.get("", response_model=list[AdminListSchema])
def list_admins(db: Session = Depends(get_db), admin: Session = Depends(get_current_admin)):
    return db.query(Administrador).all()


@router.post("", response_model=AdminResponseSchema, status_code=201)
def create_admin(data: AdminCreateSchema, db: Session = Depends(get_db), current_admin: Session = Depends(get_current_admin)):
    existing = db.query(Administrador).filter(Administrador.correo_institucional == data.correo_institucional).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El correo ya está registrado")
    admin = Administrador(
        nombre=data.nombre,
        correo_institucional=data.correo_institucional,
        password_hash=hash_password(data.password),
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@router.put("/{admin_id}/toggle-status")
def toggle_admin_status(admin_id: int, db: Session = Depends(get_db), current_admin: Session = Depends(get_current_admin)):
    if current_admin.id_admin == admin_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No puedes desactivar tu propia cuenta")
    admin = db.query(Administrador).filter(Administrador.id_admin == admin_id).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin no encontrado")
    admin.estado = "INACTIVO" if admin.estado == "ACTIVO" else "ACTIVO"
    db.commit()
    return {"message": f"Admin {'desactivado' if admin.estado == 'INACTIVO' else 'activado'} correctamente"}
