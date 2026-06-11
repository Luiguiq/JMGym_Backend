from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    TIMESTAMP,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.enum.notification_enums import TipoNotificacion, RespuestaNotificacion


class Notificacion(Base):
    __tablename__ = "notificaciones"

    id_notificacion: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    id_usuario: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id_usuario"), nullable=False
    )
    titulo: Mapped[Optional[str]] = mapped_column(String(150))
    mensaje: Mapped[Optional[str]] = mapped_column(Text)
    tipo: Mapped[TipoNotificacion] = mapped_column(
        SAEnum(TipoNotificacion), nullable=False
    )
    requiere_respuesta: Mapped[bool] = mapped_column(Boolean, default=False)
    respuesta_usuario: Mapped[Optional[RespuestaNotificacion]] = mapped_column(
        SAEnum(RespuestaNotificacion), default=None
    )
    fecha_respuesta: Mapped[Optional[datetime]] = mapped_column(DateTime, default=None)
    leido: Mapped[bool] = mapped_column(Boolean, default=False)
    fecha_envio: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    id_reserva: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("reservas.id_reserva"), default=None
    )
    id_clase: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("clases.id_clase"), default=None
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="notificaciones")
    reserva: Mapped[Optional["Reserva"]] = relationship()
    clase: Mapped[Optional["Clase"]] = relationship()
