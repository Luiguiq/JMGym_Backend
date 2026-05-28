from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    String,
    Integer,
    Date,
    DateTime,
    DECIMAL,
    TIMESTAMP,
    ForeignKey,
    UniqueConstraint,
    Enum as SAEnum,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.enum.reservation_enums import MetodoPago, EstadoPagoReserva, EstadoReserva


class Reserva(Base):
    __tablename__ = "reservas"

    __table_args__ = (
        UniqueConstraint("id_usuario", "fecha_clase", "estado_reserva"),
    )

    id_reserva: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    codigo_reserva: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False
    )
    id_usuario: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id_usuario"), nullable=False
    )
    id_clase: Mapped[int] = mapped_column(
        Integer, ForeignKey("clases.id_clase"), nullable=False
    )
    id_espacio: Mapped[int] = mapped_column(
        Integer, ForeignKey("espacios.id_espacio"), nullable=False
    )
    metodo_pago: Mapped[MetodoPago] = mapped_column(
        SAEnum(MetodoPago), nullable=False
    )
    estado_pago: Mapped[EstadoPagoReserva] = mapped_column(
        SAEnum(EstadoPagoReserva), default=EstadoPagoReserva.PENDIENTE
    )
    estado_reserva: Mapped[EstadoReserva] = mapped_column(
        SAEnum(EstadoReserva), default=EstadoReserva.ACTIVA
    )
    monto: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    fecha_reserva: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    fecha_limite_pago: Mapped[Optional[datetime]] = mapped_column(DateTime)
    fecha_clase: Mapped[date] = mapped_column(Date, nullable=False)
    qr_checkin: Mapped[Optional[str]] = mapped_column(String(255))

    usuario: Mapped["Usuario"] = relationship(back_populates="reservas")
    clase: Mapped["Clase"] = relationship(back_populates="reservas")
    espacio: Mapped["Espacio"] = relationship(back_populates="reserva")
    pagos: Mapped[list["Pago"]] = relationship(back_populates="reserva")
