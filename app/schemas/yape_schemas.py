from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class YapeInitiateRequest(BaseModel):
    celular: str
    monto: float
    id_clase: int
    id_espacio: int


class YapeInitiateResponse(BaseModel):
    id_yape_pago: int
    estado: str


class YapeConfirmRequest(BaseModel):
    id_yape_pago: int
    codigo: str


class YapeConfirmResponse(BaseModel):
    estado: str
    mensaje: str
    id_reserva: Optional[int] = None


class YapePagoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_yape_pago: int
    id_usuario: int
    id_reserva: Optional[int] = None
    celular: str
    estado: str
    monto: float
    fecha_creacion: Optional[datetime] = None
    fecha_confirmacion: Optional[datetime] = None
    usuario_nombre: Optional[str] = None
    usuario_correo: Optional[str] = None
