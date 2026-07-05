from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ReservaHistorialEstado(Base):
    __tablename__ = "reservas_historial_estados"

    id_historial: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    id_reserva: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("reservas.id_reserva", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tipo_evento: Mapped[str] = mapped_column(String(50), nullable=False)
    estado_reserva_anterior: Mapped[Optional[str]] = mapped_column(String(50))
    estado_reserva_nuevo: Mapped[Optional[str]] = mapped_column(String(50))
    estado_pago_anterior: Mapped[Optional[str]] = mapped_column(String(50))
    estado_pago_nuevo: Mapped[Optional[str]] = mapped_column(String(50))
    descripcion: Mapped[Optional[str]] = mapped_column(Text)
    fecha_hora: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False, index=True
    )
    actor_tipo: Mapped[Optional[str]] = mapped_column(String(30))
    actor_id: Mapped[Optional[int]] = mapped_column(Integer)

    reserva: Mapped["Reserva"] = relationship(back_populates="historial_estados")
