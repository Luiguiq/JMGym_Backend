from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.models.user_model import Usuario
from app.models.admin_model import Administrador
from app.schemas.notification_schemas import (
    NotificationResponseSchema,
    NotificationRespondSchema,
    NotificationMarkReadSchema,
    UnreadCountResponse,
)
from app.security import get_db, get_current_user, get_current_admin
from app.services import notification_service as svc

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/me", response_model=list[NotificationResponseSchema])
def my_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return svc.get_user_notifications_service(db, current_user.id_usuario, skip, limit)


@router.get("/me/unread-count", response_model=UnreadCountResponse)
def unread_count(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    count = svc.get_user_unread_count_service(db, current_user.id_usuario)
    return {"count": count}


@router.patch("/{notification_id}/read", response_model=NotificationResponseSchema)
def mark_read(
    notification_id: int,
    data: NotificationMarkReadSchema = NotificationMarkReadSchema(),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return svc.mark_as_read_service(db, current_user.id_usuario, notification_id)


@router.post("/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return svc.mark_all_as_read_service(db, current_user.id_usuario)


@router.post("/{notification_id}/respond", response_model=NotificationResponseSchema)
def respond_notification(
    notification_id: int,
    data: NotificationRespondSchema,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return svc.respond_to_notification_service(
        db, current_user.id_usuario, notification_id, data.respuesta
    )


# ---- Admin endpoints ----

@router.get("", response_model=list[NotificationResponseSchema])
def list_all_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    admin: Administrador = Depends(get_current_admin),
):
    return svc.get_all_notifications_admin_service(db, skip, limit)


class AdminNotificationRequest:
    pass


from pydantic import BaseModel


class AdminSendNotificationSchema(BaseModel):
    titulo: str
    mensaje: str
    tipo: str = "NOTIFICACION_GENERAL"
    user_ids: Optional[list[int]] = None
    all_users: bool = False
    class_id: Optional[int] = None


@router.post("/send")
def send_admin_notification(
    data: AdminSendNotificationSchema,
    db: Session = Depends(get_db),
    admin: Administrador = Depends(get_current_admin),
):
    return svc.send_admin_notification_service(
        db,
        titulo=data.titulo,
        mensaje=data.mensaje,
        tipo=data.tipo,
        user_ids=data.user_ids,
        all_users=data.all_users,
        class_id=data.class_id,
    )
