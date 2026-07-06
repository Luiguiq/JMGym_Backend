from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DECIMAL, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class YapePago(Base):
    __tablename__ = "yape_pagos"

    id_yape_pago: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    id_usuario: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id_usuario"), nullable=False
    )
    id_reserva: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("reservas.id_reserva")
    )
    id_clase: Mapped[int] = mapped_column(
        Integer, ForeignKey("clases.id_clase"), nullable=False
    )
    id_espacio: Mapped[int] = mapped_column(
        Integer, ForeignKey("espacios.id_espacio"), nullable=False
    )
    celular: Mapped[str] = mapped_column(String(15), nullable=False)
    codigo_confirmacion: Mapped[Optional[str]] = mapped_column(String(6))
    estado: Mapped[str] = mapped_column(String(20), default="PENDIENTE")
    monto: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )
    fecha_confirmacion: Mapped[Optional[datetime]] = mapped_column(DateTime)

    usuario: Mapped["Usuario"] = relationship()
    reserva: Mapped[Optional["Reserva"]] = relationship()
