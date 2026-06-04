from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from app.models.instructor_model import Instructor
from app.security import get_db, get_current_admin

router = APIRouter(prefix="/instructors", tags=["Instructors"])


class InstructorCreateSchema(BaseModel):
    nombre_completo: str
    telefono: Optional[str] = None
    especialidad: Optional[str] = None
    biografia: Optional[str] = None
    foto: Optional[str] = None
    video_presentacion: Optional[str] = None


class InstructorUpdateSchema(BaseModel):
    nombre_completo: Optional[str] = None
    telefono: Optional[str] = None
    especialidad: Optional[str] = None
    biografia: Optional[str] = None
    foto: Optional[str] = None
    video_presentacion: Optional[str] = None
    estado: Optional[str] = None


class InstructorResponseSchema(BaseModel):
    model_config = {"from_attributes": True}

    id_instructor: int
    nombre_completo: str
    telefono: Optional[str] = None
    especialidad: Optional[str] = None
    biografia: Optional[str] = None
    foto: Optional[str] = None
    video_presentacion: Optional[str] = None
    estado: str
    fecha_registro: Optional[datetime] = None


@router.get("", response_model=list[InstructorResponseSchema])
def list_instructors(db: Session = Depends(get_db)):
    return db.query(Instructor).all()


@router.get("/{instructor_id}", response_model=InstructorResponseSchema)
def get_instructor(instructor_id: int, db: Session = Depends(get_db)):
    instructor = db.query(Instructor).filter(Instructor.id_instructor == instructor_id).first()
    if not instructor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instructor no encontrado")
    return instructor


@router.post("", response_model=InstructorResponseSchema, status_code=201)
def create_instructor(data: InstructorCreateSchema, db: Session = Depends(get_db), admin: Session = Depends(get_current_admin)):
    instructor = Instructor(**data.model_dump())
    db.add(instructor)
    db.commit()
    db.refresh(instructor)
    return instructor


@router.put("/{instructor_id}", response_model=InstructorResponseSchema)
def update_instructor(instructor_id: int, data: InstructorUpdateSchema, db: Session = Depends(get_db), admin: Session = Depends(get_current_admin)):
    instructor = db.query(Instructor).filter(Instructor.id_instructor == instructor_id).first()
    if not instructor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instructor no encontrado")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(instructor, key, value)
    db.commit()
    db.refresh(instructor)
    return instructor


@router.delete("/{instructor_id}")
def delete_instructor(instructor_id: int, db: Session = Depends(get_db), admin: Session = Depends(get_current_admin)):
    instructor = db.query(Instructor).filter(Instructor.id_instructor == instructor_id).first()
    if not instructor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instructor no encontrado")
    db.delete(instructor)
    db.commit()
    return {"message": "Instructor eliminado correctamente"}
