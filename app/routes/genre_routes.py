from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from app.models.genre_model import GeneroClase
from app.enum.genre_enums import EstadoGenero
from app.security import get_db, get_current_admin

router = APIRouter(prefix="/genres", tags=["Genres"])


class GenreResponseSchema(BaseModel):
    model_config = {"from_attributes": True}

    id_genero: int
    nombre_genero: str
    descripcion: Optional[str] = None
    imagen: Optional[str] = None
    estado: str


class GenreCreateSchema(BaseModel):
    nombre_genero: str
    descripcion: Optional[str] = None
    imagen: Optional[str] = None
    estado: Optional[str] = "ACTIVO"


class GenreUpdateSchema(BaseModel):
    nombre_genero: Optional[str] = None
    descripcion: Optional[str] = None
    imagen: Optional[str] = None
    estado: Optional[str] = None


@router.get("", response_model=list[GenreResponseSchema])
def list_genres(db: Session = Depends(get_db)):
    return db.query(GeneroClase).all()


@router.get("/{genre_id}", response_model=GenreResponseSchema)
def get_genre(genre_id: int, db: Session = Depends(get_db)):
    genre = db.query(GeneroClase).filter(GeneroClase.id_genero == genre_id).first()
    if not genre:
        raise HTTPException(status_code=404, detail="Género no encontrado")
    return genre


@router.post("", response_model=GenreResponseSchema, status_code=201)
def create_genre(
    data: GenreCreateSchema,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    existing = db.query(GeneroClase).filter(GeneroClase.nombre_genero == data.nombre_genero).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un género con ese nombre")
    genre = GeneroClase(**data.model_dump())
    db.add(genre)
    db.commit()
    db.refresh(genre)
    return genre


@router.put("/{genre_id}", response_model=GenreResponseSchema)
def update_genre(
    genre_id: int,
    data: GenreUpdateSchema,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    genre = db.query(GeneroClase).filter(GeneroClase.id_genero == genre_id).first()
    if not genre:
        raise HTTPException(status_code=404, detail="Género no encontrado")

    if data.nombre_genero is not None:
        existing = db.query(GeneroClase).filter(
            GeneroClase.nombre_genero == data.nombre_genero,
            GeneroClase.id_genero != genre_id,
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Ya existe otro género con ese nombre")
        genre.nombre_genero = data.nombre_genero
    if data.descripcion is not None:
        genre.descripcion = data.descripcion
    if data.imagen is not None:
        genre.imagen = data.imagen
    if data.estado is not None:
        genre.estado = data.estado

    db.commit()
    db.refresh(genre)
    return genre


@router.delete("/{genre_id}")
def delete_genre(
    genre_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    genre = db.query(GeneroClase).filter(GeneroClase.id_genero == genre_id).first()
    if not genre:
        raise HTTPException(status_code=404, detail="Género no encontrado")

    if genre.clases:
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar el género porque tiene clases asociadas. Cambia su estado a INACTIVO en su lugar.",
        )

    db.delete(genre)
    db.commit()
    return {"message": "Género eliminado correctamente"}
