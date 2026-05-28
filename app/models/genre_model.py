from typing import Optional

from sqlalchemy import String, Integer, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.enum.genre_enums import EstadoGenero


class GeneroClase(Base):
    __tablename__ = "generos_clase"

    id_genero: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    nombre_genero: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text)
    imagen: Mapped[Optional[str]] = mapped_column(String(255))
    estado: Mapped[EstadoGenero] = mapped_column(
        SAEnum(EstadoGenero), default=EstadoGenero.ACTIVO
    )

    clases: Mapped[list["Clase"]] = relationship(back_populates="genero")
