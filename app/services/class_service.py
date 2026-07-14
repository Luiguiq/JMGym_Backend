from datetime import date
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.enum.class_enums import EstadoClase
from app.enum.cancelacion_enums import MotivoCancelacion, CanceladoPor
from app.enum.payment_enums import EstadoPago
from app.enum.reservation_enums import EstadoPagoReserva, EstadoReserva, MetodoPago
from app.models.class_model import Clase
from app.models.cancelacion_model import Cancelacion
from app.models.payment_model import Pago
from app.models.reservation_model import Reserva
from app.models.seat_model import Espacio
from app.models.yape_model import YapePago
from app.repositories.class_repository import (
    get_active_classes,
    get_all_classes,
    get_today_classes,
    get_class_by_id,
    get_classes_by_instructor,
    create_class,
    update_class,
    delete_class,
    get_class_seats,
)
from app.schemas.class_schemas import (
    ClassCreateSchema,
    ClassUpdateSchema,
    ClassResponseSchema,
    SeatResponseSchema,
)
from app.services.notification_service import (
    notify_class_schedule_change,
    notify_class_instructor_change,
    notify_class_cancelled,
    notify_class_completed,
    notify_refund_processed,
)
from app.services.reservation_history_service import registrar_evento_reserva


def _populate_instructor_name(cls_obj, schema: ClassResponseSchema) -> None:
    if cls_obj.instructor:
        schema.instructor_nombre = cls_obj.instructor.nombre_completo


def _cancel_active_reservations_for_cancelled_class(db: Session, cls_obj) -> None:
    reservations = (
        db.query(Reserva)
        .filter(
            Reserva.id_clase == cls_obj.id_clase,
            Reserva.estado_reserva == EstadoReserva.ACTIVA,
        )
        .all()
    )
    if not reservations:
        return

    refunds_to_notify = []

    try:
        for reservation in reservations:
            old_estado_reserva = reservation.estado_reserva
            old_estado_pago = reservation.estado_pago

            seat = db.query(Espacio).filter(Espacio.id_espacio == reservation.id_espacio).first()
            if seat:
                seat.estado = "DISPONIBLE"

            reservation.estado_reserva = EstadoReserva.CANCELADA

            if cls_obj.cupos_disponibles is not None:
                cls_obj.cupos_disponibles = min(
                    cls_obj.cupos_totales or cls_obj.cupos_disponibles + 1,
                    cls_obj.cupos_disponibles + 1,
                )

            cancelacion = Cancelacion(
                id_reserva=reservation.id_reserva,
                motivo=MotivoCancelacion.CLASE_CANCELADA,
                detalle="Reserva cancelada automáticamente porque la clase fue anulada por administración",
                cancelado_por=CanceladoPor.ADMIN,
            )
            db.add(cancelacion)

            registrar_evento_reserva(
                db,
                reservation,
                "RESERVA_CANCELADA",
                estado_reserva_anterior=old_estado_reserva,
                estado_reserva_nuevo=reservation.estado_reserva,
                descripcion="La reserva fue cancelada porque la clase fue anulada por administración.",
                actor_tipo="ADMIN",
            )

            if (
                reservation.metodo_pago == MetodoPago.YAPE
                and reservation.estado_pago == EstadoPagoReserva.PAGADO
            ):
                reservation.estado_pago = EstadoPagoReserva.REEMBOLSADO

                pagos = db.query(Pago).filter(Pago.id_reserva == reservation.id_reserva).all()
                for pago in pagos:
                    pago.estado = EstadoPago.REEMBOLSADO

                yape_pagos = db.query(YapePago).filter(YapePago.id_reserva == reservation.id_reserva).all()
                for yape_pago in yape_pagos:
                    yape_pago.estado = "REEMBOLSADO"

                registrar_evento_reserva(
                    db,
                    reservation,
                    "PAGO_REEMBOLSADO",
                    estado_pago_anterior=old_estado_pago,
                    estado_pago_nuevo=reservation.estado_pago,
                    descripcion="El pago Yape fue reembolsado automáticamente porque la clase fue anulada.",
                    actor_tipo="ADMIN",
                )

                refunds_to_notify.append(
                    (reservation.id_usuario, float(reservation.monto), cls_obj.nombre_clase, reservation.id_reserva)
                )

        db.commit()
    except Exception:
        db.rollback()
        raise

    for user_id, amount, class_name, reservation_id in refunds_to_notify:
        try:
            notify_refund_processed(db, user_id, amount, class_name, reservation_id)
        except Exception:
            pass


def get_classes_service(db: Session) -> list[ClassResponseSchema]:
    auto_complete_past_classes(db)
    classes = get_all_classes(db)
    result = []
    for c in classes:
        schema = ClassResponseSchema.model_validate(c)
        _populate_instructor_name(c, schema)
        result.append(schema)
    return result


def get_all_classes_admin_service(db: Session) -> list[ClassResponseSchema]:
    auto_complete_past_classes(db)
    classes = get_all_classes(db)
    result = []
    for c in classes:
        schema = ClassResponseSchema.model_validate(c)
        _populate_instructor_name(c, schema)
        result.append(schema)
    return result


def get_today_classes_service(db: Session) -> list[ClassResponseSchema]:
    classes = get_today_classes(db)
    result = []
    for c in classes:
        schema = ClassResponseSchema.model_validate(c)
        _populate_instructor_name(c, schema)
        result.append(schema)
    return result


def get_class_detail_service(db: Session, class_id: int) -> ClassResponseSchema:
    cls = get_class_by_id(db, class_id)
    if not cls:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clase no encontrada",
        )
    schema = ClassResponseSchema.model_validate(cls)
    _populate_instructor_name(cls, schema)
    return schema


def create_class_service(db: Session, data: ClassCreateSchema) -> ClassResponseSchema:
    cls = create_class(db, data.model_dump())
    schema = ClassResponseSchema.model_validate(cls)
    _populate_instructor_name(cls, schema)
    return schema


def update_class_service(
    db: Session, class_id: int, data: ClassUpdateSchema
) -> ClassResponseSchema:
    cls = get_class_by_id(db, class_id)
    if not cls:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clase no encontrada",
        )

    old_horario = f"{cls.hora_inicio.strftime('%H:%M')} - {cls.hora_fin.strftime('%H:%M')}" if cls.hora_inicio else ""
    old_instructor = cls.instructor.nombre_completo if cls.instructor else ""
    old_estado = cls.estado

    cls = update_class(db, class_id, data.model_dump(exclude_unset=True))

    new_horario = f"{cls.hora_inicio.strftime('%H:%M')} - {cls.hora_fin.strftime('%H:%M')}" if cls.hora_inicio else ""
    new_instructor = cls.instructor.nombre_completo if cls.instructor else ""

    if old_horario and old_horario != new_horario:
        notify_class_schedule_change(db, cls, old_horario, new_horario)

    if old_instructor and old_instructor != new_instructor:
        notify_class_instructor_change(db, cls, old_instructor, new_instructor)

    if old_estado != EstadoClase.CANCELADA and cls.estado == EstadoClase.CANCELADA:
        motivo = data.motivo_cancelacion or ""
        notify_class_cancelled(db, cls, motivo)
        _cancel_active_reservations_for_cancelled_class(db, cls)

    schema = ClassResponseSchema.model_validate(cls)
    _populate_instructor_name(cls, schema)
    return schema


def delete_class_service(db: Session, class_id: int) -> dict:
    cls = get_class_by_id(db, class_id)
    if cls:
        try:
            notify_class_cancelled(db, cls, "La clase ha sido eliminada. Puedes solicitar un reembolso.")
        except Exception:
            pass

    deleted = delete_class(db, class_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clase no encontrada",
        )
    return {"message": "Clase eliminada correctamente", "notified": True}


def get_classes_by_instructor_service(db: Session, instructor_id: int) -> list[ClassResponseSchema]:
    classes = get_classes_by_instructor(db, instructor_id)
    result = []
    for c in classes:
        schema = ClassResponseSchema.model_validate(c)
        _populate_instructor_name(c, schema)
        result.append(schema)
    return result


def auto_complete_past_classes(db: Session) -> None:
    today = date.today()
    past_active = (
        db.query(Clase)
        .filter(
            Clase.fecha < today,
            Clase.estado == EstadoClase.ACTIVA,
        )
        .all()
    )
    for cls in past_active:
        cls.estado = EstadoClase.COMPLETA
    if past_active:
        db.commit()
        for cls in past_active:
            try:
                notify_class_completed(db, cls)
            except Exception:
                pass


def get_class_seats_service(db: Session, class_id: int) -> list[SeatResponseSchema]:
    from app.models.reservation_model import Reserva
    seats = get_class_seats(db, class_id)
    active_seat_ids = set(
        r.id_espacio for r in db.query(Reserva.id_espacio).filter(
            Reserva.id_clase == class_id,
            Reserva.estado_reserva == "ACTIVA",
        ).all()
    )
    result = []
    for s in seats:
        if s.estado in ("RESERVADO", "OCUPADO") and s.id_espacio not in active_seat_ids:
            s.estado = "DISPONIBLE"
            db.commit()
        result.append(SeatResponseSchema.model_validate(s))
    return result
