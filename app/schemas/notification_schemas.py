from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.enum.notification_enums import TipoNotificacion, RespuestaNotificacion


class NotificationCreateSchema(BaseModel):
    id_usuario: int
    titulo: str
    mensaje: str
    tipo: TipoNotificacion
    requiere_respuesta: bool = False
    id_reserva: Optional[int] = None
    id_clase: Optional[int] = None


class NotificationResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_notificacion: int
    id_usuario: int
    titulo: Optional[str] = None
    mensaje: Optional[str] = None
    tipo: TipoNotificacion
    requiere_respuesta: bool
    respuesta_usuario: Optional[RespuestaNotificacion] = None
    fecha_respuesta: Optional[datetime] = None
    leido: bool
    fecha_envio: datetime
    id_reserva: Optional[int] = None
    id_clase: Optional[int] = None


class NotificationRespondSchema(BaseModel):
    respuesta: RespuestaNotificacion


class NotificationMarkReadSchema(BaseModel):
    leido: bool = True


class UnreadCountResponse(BaseModel):
    count: int
