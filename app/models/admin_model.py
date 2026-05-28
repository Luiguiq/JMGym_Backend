from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, TIMESTAMP, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class EstadoAdmin(str):
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"


class Administrador(Base):
    __tablename__ = "administradores"

    id_admin: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    correo_institucional: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    estado: Mapped[Optional[str]] = mapped_column(
        String(50), default=EstadoAdmin.ACTIVO
    )
    fecha_creacion: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
