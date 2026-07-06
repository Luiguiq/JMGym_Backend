from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, TIMESTAMP, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RestablecerContrasena(Base):
    __tablename__ = "restablecer_contrasena"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    correo: Mapped[str] = mapped_column(String(120), nullable=False)
    token: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    usado: Mapped[bool] = mapped_column(Boolean, default=False)
    expira_en: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.current_timestamp())
