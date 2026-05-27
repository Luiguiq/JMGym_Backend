from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)

    nombre = Column(String(100), nullable=False)

    correo = Column(
        String(100),
        unique=True,
        nullable=False
    )

    password = Column(
        String(255),
        nullable=False
    )

    rol = Column(
        String(50),
        default="cliente"
    )

    # RELACIÓN CON RESERVAS
    reservas = relationship(
        "Reserva",
        back_populates="usuario"
    )