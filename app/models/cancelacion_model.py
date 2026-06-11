from datetime import datetime
from typing import Optional

from sqlalchemy import (
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
from app.enum.cancelacion_enums import MotivoCancelacion, CanceladoPor


class Cancelacion(Base):
    __tablename__ = "cancelaciones"

    id_cancelacion: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    id_reserva: Mapped[int] = mapped_column(
        Integer, ForeignKey("reservas.id_reserva"), nullable=False
    )
    motivo: Mapped[MotivoCancelacion] = mapped_column(
        SAEnum(MotivoCancelacion), nullable=False
    )
    detalle: Mapped[Optional[str]] = mapped_column(Text)
    cancelado_por: Mapped[CanceladoPor] = mapped_column(
        SAEnum(CanceladoPor), default=CanceladoPor.USUARIO
    )
    id_admin: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("administradores.id_admin"), default=None
    )
    fecha_cancelacion: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )

    reserva: Mapped["Reserva"] = relationship(back_populates="cancelacion")
