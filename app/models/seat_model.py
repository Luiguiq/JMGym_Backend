from typing import Optional

from sqlalchemy import String, Integer, ForeignKey, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.enum.espacio_enums import EstadoEspacio


class Espacio(Base):
    __tablename__ = "espacios"

    __table_args__ = (
        UniqueConstraint("id_clase", "codigo_espacio"),
    )

    id_espacio: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    id_clase: Mapped[int] = mapped_column(
        Integer, ForeignKey("clases.id_clase"), nullable=False
    )
    codigo_espacio: Mapped[str] = mapped_column(String(10), nullable=False)
    estado: Mapped[EstadoEspacio] = mapped_column(
        SAEnum(EstadoEspacio), default=EstadoEspacio.DISPONIBLE
    )

    clase: Mapped["Clase"] = relationship(back_populates="espacios")
    reserva: Mapped[Optional["Reserva"]] = relationship(back_populates="espacio")
