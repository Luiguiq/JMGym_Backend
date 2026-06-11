from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.notification_model import Notificacion


def create_notification(db: Session, data: dict) -> Notificacion:
    notif = Notificacion(**data)
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


def get_user_notifications(
    db: Session, user_id: int, skip: int = 0, limit: int = 50
) -> list[Notificacion]:
    return (
        db.query(Notificacion)
        .filter(Notificacion.id_usuario == user_id)
        .order_by(Notificacion.fecha_envio.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_user_unread_count(db: Session, user_id: int) -> int:
    return (
        db.query(Notificacion)
        .filter(Notificacion.id_usuario == user_id, Notificacion.leido == False)
        .count()
    )


def get_notification_by_id(
    db: Session, notification_id: int
) -> Optional[Notificacion]:
    return (
        db.query(Notificacion)
        .filter(Notificacion.id_notificacion == notification_id)
        .first()
    )


def mark_notification_read(
    db: Session, notification_id: int, leido: bool = True
) -> Optional[Notificacion]:
    notif = get_notification_by_id(db, notification_id)
    if not notif:
        return None
    notif.leido = leido
    db.commit()
    db.refresh(notif)
    return notif


def mark_all_user_notifications_read(db: Session, user_id: int) -> int:
    result = (
        db.query(Notificacion)
        .filter(
            Notificacion.id_usuario == user_id, Notificacion.leido == False
        )
        .update({"leido": True})
    )
    db.commit()
    return result


def respond_to_notification(
    db: Session, notification_id: int, respuesta: str
) -> Optional[Notificacion]:
    notif = get_notification_by_id(db, notification_id)
    if not notif:
        return None
    notif.respuesta_usuario = respuesta
    notif.fecha_respuesta = datetime.now()
    db.commit()
    db.refresh(notif)
    return notif


def get_all_user_notifications_paginated(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    tipo: Optional[str] = None,
    leido: Optional[bool] = None,
) -> list[Notificacion]:
    query = db.query(Notificacion).filter(Notificacion.id_usuario == user_id)

    if tipo:
        query = query.filter(Notificacion.tipo == tipo)
    if leido is not None:
        query = query.filter(Notificacion.leido == leido)

    return (
        query.order_by(Notificacion.fecha_envio.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_all_notifications_admin(
    db: Session, skip: int = 0, limit: int = 100
) -> list[Notificacion]:
    return (
        db.query(Notificacion)
        .order_by(Notificacion.fecha_envio.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
