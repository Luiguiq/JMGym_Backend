from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base

class Clase(Base):
    __tablename__ = "clases"

    id = Column(Integer, primary_key=True, index=True)

    nombre = Column(
        String(100),
        nullable=False
    )

    instructor = Column(
        String(100),
        nullable=False
    )

    horario = Column(
        String(100),
        nullable=False
    )

    cupos = Column(
        Integer,
        nullable=False
    )

    # RELACIÓN CON RESERVAS
    reservas = relationship(
        "Reserva",
        back_populates="clase"
    )