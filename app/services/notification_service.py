from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.enum.notification_enums import TipoNotificacion, RespuestaNotificacion
from app.enum.cancelacion_enums import MotivoCancelacion, CanceladoPor
from app.models.notification_model import Notificacion
from app.models.reservation_model import Reserva
from app.models.class_model import Clase
from app.models.user_model import Usuario
from app.models.cancelacion_model import Cancelacion
from app.models.seat_model import Espacio
from app.repositories import notification_repository as repo
from app.schemas.notification_schemas import (
    NotificationResponseSchema,
    NotificationCreateSchema,
)


def _create_notification(
    db: Session,
    user_id: int,
    titulo: str,
    mensaje: str,
    tipo: TipoNotificacion,
    requiere_respuesta: bool = False,
    id_reserva: Optional[int] = None,
    id_clase: Optional[int] = None,
) -> NotificationResponseSchema:
    notif = repo.create_notification(
        db,
        {
            "id_usuario": user_id,
            "titulo": titulo,
            "mensaje": mensaje,
            "tipo": tipo,
            "requiere_respuesta": requiere_respuesta,
            "id_reserva": id_reserva,
            "id_clase": id_clase,
        },
    )
    return NotificationResponseSchema.model_validate(notif)


def _notify_all_reservation_users(
    db: Session,
    class_id: int,
    titulo: str,
    mensaje: str,
    tipo: TipoNotificacion,
    requiere_respuesta: bool = False,
):
    """Send notification to all users with active reservations for a class."""
    reservas = (
        db.query(Reserva)
        .filter(
            Reserva.id_clase == class_id,
            Reserva.estado_reserva == "ACTIVA",
        )
        .all()
    )
    for r in reservas:
        _create_notification(
            db,
            user_id=r.id_usuario,
            titulo=titulo,
            mensaje=mensaje,
            tipo=tipo,
            requiere_respuesta=requiere_respuesta,
            id_reserva=r.id_reserva,
            id_clase=class_id,
        )


def notify_reservation_created(
    db: Session, user_id: int, reservation: Reserva
) -> NotificationResponseSchema:
    return _create_notification(
        db,
        user_id=user_id,
        titulo="Reserva confirmada",
        mensaje=f"Tu reserva para {reservation.clase.nombre_clase} el {reservation.fecha_clase} ha sido creada exitosamente. Código: {reservation.codigo_reserva}",
        tipo=TipoNotificacion.RESERVA_CONFIRMADA,
        id_reserva=reservation.id_reserva,
        id_clase=reservation.id_clase,
    )


def notify_reservation_cancelled(
    db: Session, user_id: int, reservation: Reserva
) -> NotificationResponseSchema:
    return _create_notification(
        db,
        user_id=user_id,
        titulo="Reserva cancelada",
        mensaje=f"Tu reserva para {reservation.clase.nombre_clase} el {reservation.fecha_clase} ha sido cancelada.",
        tipo=TipoNotificacion.RESERVA_CANCELADA,
        id_reserva=reservation.id_reserva,
        id_clase=reservation.id_clase,
    )


def notify_payment_confirmed(
    db: Session, user_id: int, reservation: Reserva
) -> NotificationResponseSchema:
    return _create_notification(
        db,
        user_id=user_id,
        titulo="Pago confirmado",
        mensaje=f"Tu pago de S/ {reservation.monto:.2f} para {reservation.clase.nombre_clase} ha sido confirmado.",
        tipo=TipoNotificacion.PAGO_CONFIRMADO,
        id_reserva=reservation.id_reserva,
        id_clase=reservation.id_clase,
    )


def notify_seat_changed(
    db: Session, user_id: int, reservation: Reserva, old_seat_code: str, new_seat_code: str
) -> NotificationResponseSchema:
    return _create_notification(
        db,
        user_id=user_id,
        titulo="Asiento cambiado",
        mensaje=f"Tu asiento para {reservation.clase.nombre_clase} cambió de {old_seat_code} a {new_seat_code}.",
        tipo=TipoNotificacion.CAMBIO_ESPACIO,
        id_reserva=reservation.id_reserva,
        id_clase=reservation.id_clase,
    )


def notify_class_schedule_change(
    db: Session,
    class_obj: Clase,
    old_time: str,
    new_time: str,
    reason: str = "",
) -> list[NotificationResponseSchema]:
    titulo = "Cambio de horario"
    mensaje = (
        f"La clase {class_obj.nombre_clase} del {class_obj.fecha} "
        f"ha cambiado de {old_time} a {new_time}. "
        f"{'Motivo: ' + reason if reason else ''}"
    )
    reservas = (
        db.query(Reserva)
        .filter(
            Reserva.id_clase == class_obj.id_clase,
            Reserva.estado_reserva == "ACTIVA",
        )
        .all()
    )
    results = []
    for r in reservas:
        n = _create_notification(
            db,
            user_id=r.id_usuario,
            titulo=titulo,
            mensaje=mensaje,
            tipo=TipoNotificacion.CAMBIO_HORARIO,
            requiere_respuesta=True,
            id_reserva=r.id_reserva,
            id_clase=class_obj.id_clase,
        )
        results.append(n)
    return results


def notify_class_instructor_change(
    db: Session,
    class_obj: Clase,
    old_instructor: str,
    new_instructor: str,
) -> list[NotificationResponseSchema]:
    titulo = "Cambio de instructor"
    mensaje = (
        f"La clase {class_obj.nombre_clase} del {class_obj.fecha} "
        f"ha cambiado de instructor: {old_instructor} → {new_instructor}."
    )
    reservas = (
        db.query(Reserva)
        .filter(
            Reserva.id_clase == class_obj.id_clase,
            Reserva.estado_reserva == "ACTIVA",
        )
        .all()
    )
    results = []
    for r in reservas:
        n = _create_notification(
            db,
            user_id=r.id_usuario,
            titulo=titulo,
            mensaje=mensaje,
            tipo=TipoNotificacion.CAMBIO_INSTRUCTOR,
            id_reserva=r.id_reserva,
            id_clase=class_obj.id_clase,
        )
        results.append(n)
    return results


def notify_class_cancelled(
    db: Session,
    class_obj: Clase,
    reason: str = "",
) -> list[NotificationResponseSchema]:
    titulo = "Clase cancelada"
    mensaje = (
        f"La clase {class_obj.nombre_clase} del {class_obj.fecha} "
        f"ha sido cancelada. {'Motivo: ' + reason if reason else ''}"
    )
    reservas = (
        db.query(Reserva)
        .filter(
            Reserva.id_clase == class_obj.id_clase,
            Reserva.estado_reserva == "ACTIVA",
        )
        .all()
    )
    results = []
    for r in reservas:
        n = _create_notification(
            db,
            user_id=r.id_usuario,
            titulo=titulo,
            mensaje=mensaje,
            tipo=TipoNotificacion.CANCELACION,
            requiere_respuesta=False,
            id_reserva=r.id_reserva,
            id_clase=class_obj.id_clase,
        )
        results.append(n)
    return results


def notify_new_class(
    db: Session, user_ids: list[int], class_obj: Clase
) -> list[NotificationResponseSchema]:
    titulo = "Nueva clase disponible"
    mensaje = (
        f"Se ha agregado una nueva clase: {class_obj.nombre_clase} "
        f"el {class_obj.fecha} a las {class_obj.hora_inicio}."
    )
    results = []
    for uid in user_ids:
        n = _create_notification(
            db,
            user_id=uid,
            titulo=titulo,
            mensaje=mensaje,
            tipo=TipoNotificacion.NUEVA_CLASE,
            id_clase=class_obj.id_clase,
        )
        results.append(n)
    return results


def notify_refund_processed(
    db: Session, user_id: int, monto: float, class_name: str, reservation_id: int
) -> NotificationResponseSchema:
    return _create_notification(
        db,
        user_id=user_id,
        titulo="Reembolso procesado",
        mensaje=f"Se ha procesado tu reembolso de S/ {monto:.2f} por la clase {class_name}.",
        tipo=TipoNotificacion.REEMBOLSO,
        id_reserva=reservation_id,
    )


def notify_account_blocked(
    db: Session, user_id: int, estado: str
) -> NotificationResponseSchema:
    accion = "bloqueada" if estado == "BLOQUEADO" else "desbloqueada"
    return _create_notification(
        db,
        user_id=user_id,
        titulo="Cuenta " + accion,
        mensaje=f"Tu cuenta ha sido {accion}. Contacta al administrador si tienes dudas.",
        tipo=TipoNotificacion.BLOQUEO_CUENTA,
    )


def notify_class_reminder(
    db: Session, user_id: int, reservation: Reserva, hours_before: int
) -> NotificationResponseSchema:
    return _create_notification(
        db,
        user_id=user_id,
        titulo="Recordatorio de clase",
        mensaje=f"Tu clase {reservation.clase.nombre_clase} comienza en {hours_before} hora(s) a las {reservation.clase.hora_inicio}. ¡Te esperamos!",
        tipo=TipoNotificacion.RECORDATORIO,
        id_reserva=reservation.id_reserva,
        id_clase=reservation.id_clase,
    )


def get_user_notifications_service(
    db: Session, user_id: int, skip: int = 0, limit: int = 50
) -> list[NotificationResponseSchema]:
    notifs = repo.get_user_notifications(db, user_id, skip=skip, limit=limit)
    return [NotificationResponseSchema.model_validate(n) for n in notifs]


def get_user_unread_count_service(db: Session, user_id: int) -> int:
    return repo.get_user_unread_count(db, user_id)


def mark_as_read_service(
    db: Session, user_id: int, notification_id: int
) -> NotificationResponseSchema:
    notif = repo.get_notification_by_id(db, notification_id)
    if not notif:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada",
        )
    if notif.id_usuario != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes modificar esta notificación",
        )
    notif = repo.mark_notification_read(db, notification_id, True)
    return NotificationResponseSchema.model_validate(notif)


def mark_all_as_read_service(db: Session, user_id: int) -> dict:
    count = repo.mark_all_user_notifications_read(db, user_id)
    return {"message": f"{count} notificacion(es) marcada(s) como leídas", "count": count}


def respond_to_notification_service(
    db: Session, user_id: int, notification_id: int, respuesta: RespuestaNotificacion
) -> NotificationResponseSchema:
    notif = repo.get_notification_by_id(db, notification_id)
    if not notif:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada",
        )
    if notif.id_usuario != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes responder a esta notificación",
        )
    if not notif.requiere_respuesta:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta notificación no requiere respuesta",
        )

    if respuesta == RespuestaNotificacion.CANCELADO:
        if notif.id_reserva:
            reservation = (
                db.query(Reserva)
                .filter(Reserva.id_reserva == notif.id_reserva)
                .first()
            )
            if reservation and reservation.estado_reserva == "ACTIVA":
                old_seat = db.query(Espacio).filter(Espacio.id_espacio == reservation.id_espacio).first()
                if old_seat:
                    old_seat.estado = "DISPONIBLE"

                reservation.estado_reserva = "CANCELADA"
                cls = reservation.clase
                if cls and cls.cupos_disponibles is not None:
                    cls.cupos_disponibles += 1

                cancelacion = Cancelacion(
                    id_reserva=reservation.id_reserva,
                    motivo=MotivoCancelacion.CAMBIO_HORARIO,
                    detalle="Cancelación por respuesta a notificación de cambio de horario",
                    cancelado_por=CanceladoPor.USUARIO,
                )
                db.add(cancelacion)
                db.commit()

    notif = repo.respond_to_notification(db, notification_id, respuesta.value)
    return NotificationResponseSchema.model_validate(notif)


# Admin service to send bulk notifications
def send_admin_notification_service(
    db: Session,
    titulo: str,
    mensaje: str,
    tipo: str,
    user_ids: Optional[list[int]] = None,
    all_users: bool = False,
    class_id: Optional[int] = None,
) -> dict:
    if all_users:
        users = db.query(Usuario).filter(Usuario.estado == "ACTIVO").all()
        user_ids = [u.id_usuario for u in users]
    elif class_id and not user_ids:
        reservas = (
            db.query(Reserva)
            .filter(
                Reserva.id_clase == class_id,
                Reserva.estado_reserva == "ACTIVA",
            )
            .all()
        )
        user_ids = list(set(r.id_usuario for r in reservas))

    if not user_ids:
        return {"message": "No hay usuarios para notificar", "count": 0}

    count = 0
    for uid in user_ids:
        _create_notification(
            db,
            user_id=uid,
            titulo=titulo,
            mensaje=mensaje,
            tipo=TipoNotificacion(tipo) if isinstance(tipo, str) else tipo,
            id_clase=class_id,
        )
        count += 1

    return {"message": f"Notificación enviada a {count} usuario(s)", "count": count}


def get_all_notifications_admin_service(
    db: Session, skip: int = 0, limit: int = 100
) -> list[NotificationResponseSchema]:
    notifs = repo.get_all_notifications_admin(db, skip=skip, limit=limit)
    return [NotificationResponseSchema.model_validate(n) for n in notifs]
