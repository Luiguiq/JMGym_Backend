import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASSWORD,
    SMTP_FROM,
)

logger = logging.getLogger(__name__)


def enviar_correo(destinatario: str, asunto: str, cuerpo_html: str) -> bool:
    if not SMTP_HOST:
        logger.warning(f"SMTP no configurado. Correo no enviado a {destinatario}")
        logger.info(f"Asunto: {asunto}")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = asunto
    msg["From"] = SMTP_FROM or SMTP_USER
    msg["To"] = destinatario

    msg.attach(MIMEText(cuerpo_html, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            if SMTP_PORT == 587:
                server.starttls()
            if SMTP_USER and SMTP_PASSWORD:
                server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(msg["From"], [destinatario], msg.as_string())
        logger.info(f"Correo enviado a {destinatario}")
        return True
    except Exception as e:
        logger.error(f"Error enviando correo a {destinatario}: {e}")
        return False
