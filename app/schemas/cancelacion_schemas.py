from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.enum.cancelacion_enums import MotivoCancelacion, CanceladoPor


class CancelacionCreateSchema(BaseModel):
    motivo: MotivoCancelacion = MotivoCancelacion.OTRO
    detalle: Optional[str] = None


class CancelacionResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_cancelacion: int
    id_reserva: int
    motivo: MotivoCancelacion
    detalle: Optional[str] = None
    cancelado_por: CanceladoPor
    id_admin: Optional[int] = None
    fecha_cancelacion: datetime


class CancelacionAdminResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_cancelacion: int
    id_reserva: int
    motivo: str
    detalle: Optional[str] = None
    cancelado_por: str
    fecha_cancelacion: datetime
    codigo_reserva: Optional[str] = None
    nombre_usuario: Optional[str] = None
    nombre_clase: Optional[str] = None
    fecha_clase: Optional[date] = None
