from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.security import get_db, get_current_user
from app.models.user_model import Usuario
from app.services.fidelizacion_service import obtener_info_fidelizacion

router = APIRouter(prefix="/fidelizacion", tags=["Fidelización"])


class FidelizacionResponse(BaseModel):
    horas_mes: float
    horas_base: float
    horas_bono: float
    nivel: str
    descuento_porcentaje: int
    acompanante_gratis: bool
    clases_gratis_restantes: int = 0
    siguiente_nivel: str | None = None
    horas_restantes: float = 0


@router.get("/me", response_model=FidelizacionResponse)
def get_mi_fidelizacion(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return obtener_info_fidelizacion(db, current_user.id_usuario)