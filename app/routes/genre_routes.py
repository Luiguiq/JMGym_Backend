from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from app.models.genre_model import GeneroClase
from app.security import get_db

router = APIRouter(prefix="/genres", tags=["Genres"])


class GenreResponseSchema(BaseModel):
    model_config = {"from_attributes": True}

    id_genero: int
    nombre_genero: str
    descripcion: Optional[str] = None
    estado: str


@router.get("", response_model=list[GenreResponseSchema])
def list_genres(db: Session = Depends(get_db)):
    return db.query(GeneroClase).all()
