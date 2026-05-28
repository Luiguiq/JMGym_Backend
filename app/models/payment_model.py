from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DECIMAL, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.enum.payment_enums import MetodoPago, EstadoPago


class Pago(Base):
    __tablename__ = "pagos"

    id_pago: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    id_reserva: Mapped[int] = mapped_column(
        Integer, ForeignKey("reservas.id_reserva"), nullable=False
    )
    metodo_pago: Mapped[MetodoPago] = mapped_column(
        SAEnum(MetodoPago), nullable=False
    )
    estado: Mapped[EstadoPago] = mapped_column(
        SAEnum(EstadoPago), default=EstadoPago.PENDIENTE
    )
    monto: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    codigo_operacion: Mapped[Optional[str]] = mapped_column(String(100))
    fecha_pago: Mapped[Optional[datetime]] = mapped_column(DateTime)
    qr_yape: Mapped[Optional[str]] = mapped_column(String(255))
    confirmado_por_admin: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("usuarios.id_usuario")
    )

    reserva: Mapped["Reserva"] = relationship(back_populates="pagos")
