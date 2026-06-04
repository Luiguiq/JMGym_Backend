from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.enum.reservation_enums import EstadoPagoReserva, EstadoReserva


class ReservationCreateSchema(BaseModel):
    class_id: int = Field(validation_alias="classId")


# NUEVO: Esquema para extraer el nombre de la clase automáticamente
class ClaseReservaSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    nombre_clase: str


class ReservationResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_reserva: int
    codigo_reserva: str
    id_usuario: int
    id_clase: int
    id_espacio: int
    metodo_pago: str
    estado_pago: EstadoPagoReserva
    estado_reserva: EstadoReserva
    monto: float
    fecha_reserva: datetime
    fecha_limite_pago: Optional[datetime] = None
    fecha_clase: date
    qr_checkin: Optional[str] = None

    # NUEVO: Le pedimos a FastAPI que incluya los datos de la clase
    clase: Optional[ClaseReservaSchema] = None
