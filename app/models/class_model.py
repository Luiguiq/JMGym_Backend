from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Clase(Base):
    __tablename__ = "clases"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    instructor = Column(String(100), nullable=False)
    horario = Column(String(100), nullable=False)
    cupos = Column(Integer, nullable=False)