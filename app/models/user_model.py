from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, TIMESTAMP, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.enum.user_enums import EstadoUsuario


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    nombre_completo: Mapped[str] = mapped_column(String(150), nullable=False)
    dni: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    correo: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    telefono: Mapped[Optional[str]] = mapped_column(String(20))
    foto_perfil: Mapped[Optional[str]] = mapped_column(String(255))
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    estado: Mapped[EstadoUsuario] = mapped_column(
        SAEnum(EstadoUsuario), default=EstadoUsuario.ACTIVO
    )
    fecha_registro: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )

    reservas: Mapped[list["Reserva"]] = relationship(back_populates="usuario")
