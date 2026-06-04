from datetime import date, datetime, time
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ReservationCreateSchema(BaseModel):
    class_id: int = Field(validation_alias="classId")
    seat_id: int = Field(validation_alias="seatId")


class ClaseReservaSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, json_encoders={time: lambda t: t.strftime("%H:%M")})

    nombre_clase: str
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    duracion_minutos: Optional[int] = None
    fecha: Optional[date] = None
    precio: Optional[float] = None
    instructor_nombre: Optional[str] = None
    imagen_clase: Optional[str] = None


class EspacioReservaSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    codigo_espacio: str


class ReservationResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_reserva: int
    codigo_reserva: str
    id_usuario: int
    id_clase: int
    id_espacio: int
    metodo_pago: str
    estado_pago: str
    estado_reserva: str
    monto: float
    fecha_reserva: datetime
    fecha_limite_pago: Optional[datetime] = None
    fecha_clase: date
    qr_checkin: Optional[str] = None

    clase: Optional[ClaseReservaSchema] = None
    espacio: Optional[EspacioReservaSchema] = None
