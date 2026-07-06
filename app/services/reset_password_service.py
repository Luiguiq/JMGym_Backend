import logging
from datetime import datetime, timedelta, timezone
import secrets

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import RESET_TOKEN_EXPIRE_MINUTES
from app.models.password_reset_model import RestablecerContrasena
from app.repositories.user_repository import get_user_by_email
from app.security import hash_password
from app.utils.email import enviar_correo


logger = logging.getLogger(__name__)
FRONTEND_URL = "https://jm-gyms.vercel.app"


def solicitar_restablecimiento(db: Session, correo: str) -> dict:
    user = get_user_by_email(db, correo)
    if not user:
        return {"mensaje": "Si el correo existe, recibirás un enlace para restablecer tu contraseña"}

    token = secrets.token_urlsafe(48)
    expira_en = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)

    reset = RestablecerContrasena(
        correo=correo,
        token=token,
        expira_en=expira_en,
    )
    db.add(reset)
    db.commit()

    enlace = f"{FRONTEND_URL}/cliente/restablecer-contrasena?token={token}"
    cuerpo_html = f"""
    <h2>Restablecer contraseña</h2>
    <p>Has solicitado restablecer tu contraseña. Haz clic en el siguiente enlace:</p>
    <p><a href="{enlace}">{enlace}</a></p>
    <p>Este enlace expira en {RESET_TOKEN_EXPIRE_MINUTES} minutos.</p>
    <p>Si no solicitaste esto, ignora este correo.</p>
    """

    enviado = enviar_correo(correo, "Restablece tu contraseña - JMGym", cuerpo_html)

    if not enviado:
        logger.warning(f"No se pudo enviar correo a {correo}, pero se guardó el token")

    return {"mensaje": "Si el correo existe, recibirás un enlace para restablecer tu contraseña"}


def restablecer_contrasena(db: Session, token: str, nueva_password: str) -> dict:
    registro = (
        db.query(RestablecerContrasena)
        .filter(
            RestablecerContrasena.token == token,
            RestablecerContrasena.usado == False,
            RestablecerContrasena.expira_en > datetime.now(timezone.utc),
        )
        .first()
    )

    if not registro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido o expirado",
        )

    user = get_user_by_email(db, registro.correo)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario no encontrado",
        )

    user.password_hash = hash_password(nueva_password)
    registro.usado = True
    db.commit()

    return {"mensaje": "Contraseña restablecida exitosamente"}
