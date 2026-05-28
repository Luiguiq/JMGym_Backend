from __future__ import annotations

from datetime import date, datetime, time
from typing import Optional

from sqlalchemy import (
    String,
    Integer,
    Text,
    Date,
    Time,
    DateTime,
    DECIMAL,
    TIMESTAMP,
    ForeignKey,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.enum.class_enums import IntensidadClase, EstadoClase
from sqlalchemy import Enum


class Clase(Base):
    __tablename__ = "clases"

    id_clase: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    nombre_clase: Mapped[str] = mapped_column(
        String(120),
        nullable=False
    )

    id_genero: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("generos_clase.id_genero"),
        nullable=False
    )

    id_instructor: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("instructores.id_instructor"),
        nullable=False
    )

    descripcion: Mapped[Optional[str]] = mapped_column(Text)

    intensidad: Mapped[IntensidadClase] = mapped_column(
        Enum(IntensidadClase),
        default=IntensidadClase.MEDIA
    )

    reglas_vestimenta: Mapped[Optional[str]] = mapped_column(Text)

    duracion_minutos: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    fecha: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    hora_inicio: Mapped[time] = mapped_column(
        Time,
        nullable=False
    )

    hora_fin: Mapped[time] = mapped_column(
        Time,
        nullable=False
    )

    precio: Mapped[float] = mapped_column(
        DECIMAL(10, 2),
        nullable=False,
        default=0.00
    )

    cupos_totales: Mapped[int] = mapped_column(
        Integer,
        default=40
    )

    cupos_disponibles: Mapped[int] = mapped_column(
        Integer,
        default=40
    )

    alumnos_minimos: Mapped[int] = mapped_column(
        Integer,
        default=5
    )

    fecha_limite_cancelacion: Mapped[Optional[datetime]] = mapped_column(
        DateTime
    )

    imagen_clase: Mapped[Optional[str]] = mapped_column(
        String(255)
    )

    estado: Mapped[EstadoClase] = mapped_column(
        Enum(EstadoClase),
        default=EstadoClase.ACTIVA
    )

    motivo_cancelacion: Mapped[Optional[str]] = mapped_column(Text)

    fecha_creacion: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp()
    )

    genero: Mapped["GeneroClase"] = relationship(
        back_populates="clases"
    )

    instructor: Mapped["Instructor"] = relationship(
        back_populates="clases"
    )

    reservas: Mapped[list["Reserva"]] = relationship(
        back_populates="clase"
    )

    espacios: Mapped[list["Espacio"]] = relationship(
        back_populates="clase"
    )