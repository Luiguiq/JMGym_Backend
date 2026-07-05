from datetime import date, datetime, time
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field


HISTORY_EVENT_TITLES = {
    "RESERVA_CREADA": "Reserva creada",
    "PAGO_PENDIENTE": "Pago pendiente",
    "PAGO_CONFIRMADO": "Pago confirmado",
    "PAGO_VENCIDO": "Pago vencido",
    "PAGO_RECHAZADO": "Pago rechazado",
    "PAGO_REEMBOLSADO": "Pago reembolsado",
    "RESERVA_CANCELADA": "Reserva cancelada",
    "REEMBOLSO_SOLICITADO": "Reembolso solicitado",
    "REEMBOLSO_APROBADO": "Reembolso aprobado",
    "REEMBOLSO_RECHAZADO": "Reembolso rechazado",
    "REEMBOLSO_SOLICITUD_CANCELADA": "Solicitud de reembolso cancelada",
    "RESERVA_COMPLETADA": "Reserva completada",
    "RESERVA_FINALIZADA": "Reserva finalizada",
    "ASIENTO_CAMBIADO": "Espacio cambiado",
}


class ReservationCreateSchema(BaseModel):
    class_id: int = Field(validation_alias="classId")
    seat_id: int = Field(validation_alias="seatId")
    payment_method: str = Field(validation_alias="paymentMethod")
    

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


class UsuarioReservaSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nombre_completo: str
    correo: Optional[str] = None
    foto_perfil: Optional[str] = None


class EspacioReservaSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    codigo_espacio: str


class ReservationHistoryResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(validation_alias="id_historial")
    tipo_evento: str
    descripcion: Optional[str] = None
    estado_reserva_anterior: Optional[str] = None
    estado_reserva_nuevo: Optional[str] = None
    estado_pago_anterior: Optional[str] = None
    estado_pago_nuevo: Optional[str] = None
    fecha_hora: datetime
    actor_tipo: Optional[str] = None

    @computed_field
    @property
    def titulo(self) -> str:
        return HISTORY_EVENT_TITLES.get(self.tipo_evento, "Cambio registrado")


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
    usuario: Optional[UsuarioReservaSchema] = None
    historial_estados: list[ReservationHistoryResponseSchema] = Field(default_factory=list)
