from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Text, TIMESTAMP, ForeignKey, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.enum.instructor_enums import EstadoInstructor


class Instructor(Base):
    __tablename__ = "instructores"

    id_instructor: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    nombre_completo: Mapped[str] = mapped_column(String(150), nullable=False)
    telefono: Mapped[Optional[str]] = mapped_column(String(20))
    especialidad: Mapped[Optional[str]] = mapped_column(String(120))
    biografia: Mapped[Optional[str]] = mapped_column(Text)
    foto: Mapped[Optional[str]] = mapped_column(String(255))
    video_presentacion: Mapped[Optional[str]] = mapped_column(String(255))
    estado: Mapped[EstadoInstructor] = mapped_column(
        SAEnum(EstadoInstructor), default=EstadoInstructor.ACTIVO
    )
    fecha_registro: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )

    clases: Mapped[list["Clase"]] = relationship(back_populates="instructor")
    instructor_generos: Mapped[list["InstructorGenero"]] = relationship(
        back_populates="instructor"
    )


class InstructorGenero(Base):
    __tablename__ = "instructor_generos"

    id_instructor: Mapped[int] = mapped_column(
        Integer, ForeignKey("instructores.id_instructor"), primary_key=True
    )
    id_genero: Mapped[int] = mapped_column(
        Integer, ForeignKey("generos_clase.id_genero"), primary_key=True
    )

    instructor: Mapped["Instructor"] = relationship(back_populates="instructor_generos")
    genero: Mapped["GeneroClase"] = relationship()
