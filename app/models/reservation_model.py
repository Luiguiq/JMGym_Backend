from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base

class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True)

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=False
    )

    clase_id = Column(
        Integer,
        ForeignKey("clases.id"),
        nullable=False
    )

    estado = Column(
        String(50),
        default="pendiente"
    )

    # RELACIÓN CON USUARIO
    usuario = relationship(
        "Usuario",
        back_populates="reservas"
    )

    # RELACIÓN CON CLASE
    clase = relationship(
        "Clase",
        back_populates="reservas"
    )