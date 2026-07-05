import uuid
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.reservation_model import Reserva
from app.models.payment_model import Pago
from app.models.seat_model import Espacio
from app.repositories.class_repository import get_class_by_id
from app.repositories.reservation_repository import (
    get_user_reservations,
    get_reservation_by_id,
    get_all_reservations,
)
from app.schemas.reservation_schemas import ReservationCreateSchema, ReservationResponseSchema
from app.schemas.cancelacion_schemas import CancelacionCreateSchema
from app.enum.reservation_enums import MetodoPago, EstadoPagoReserva, EstadoReserva
from app.enum.payment_enums import MetodoPago as MetodoPagoPago, EstadoPago
from app.enum.cancelacion_enums import MotivoCancelacion, CanceladoPor
from app.models.cancelacion_model import Cancelacion
from app.services.notification_service import (
    notify_reservation_created,
    notify_reservation_cancelled,
    notify_seat_changed,
)
from app.services.notification_service import (
    notify_refund_processed,
    notify_refund_request_cancelled,
)
from app.services.reservation_history_service import registrar_evento_reserva


def _class_has_started(reservation: Reserva) -> bool:
    cls = reservation.clase
    if not cls or not cls.fecha or not cls.hora_inicio:
        return False
    return datetime.now() >= datetime.combine(cls.fecha, cls.hora_inicio)


def create_reservation_service(
    db: Session, user_id: int, data: ReservationCreateSchema
) -> ReservationResponseSchema:
    cls = get_class_by_id(db, data.class_id)
    if not cls:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clase no encontrada",
        )

    if cls.cupos_disponibles is not None and cls.cupos_disponibles <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay cupos disponibles",
        )

    existing = (
        db.query(Reserva)
        .filter(
            Reserva.id_usuario == user_id,
            Reserva.id_clase == data.class_id,
            Reserva.estado_reserva == EstadoReserva.ACTIVA,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya tienes una reserva activa para esta clase",
        )

    existing_same_date = (
        db.query(Reserva)
        .filter(
            Reserva.id_usuario == user_id,
            Reserva.fecha_clase == cls.fecha,
            Reserva.estado_reserva == EstadoReserva.ACTIVA,
        )
        .first()
    )

    if existing_same_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya tienes una reserva activa para esa fecha",
        )

    espacio = (
        db.query(Espacio)
        .filter(
            Espacio.id_espacio == data.seat_id,
            Espacio.id_clase == data.class_id,
        )
        .first()
    )
    if not espacio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Espacio no encontrado para esta clase",
        )

    # Auto-fix: liberar asiento si no hay reserva activa que lo ocupe
    reserva_activa = db.query(Reserva).filter(
        Reserva.id_espacio == espacio.id_espacio,
        Reserva.estado_reserva == "ACTIVA",
    ).first()
    if espacio.estado != "DISPONIBLE" and not reserva_activa:
        espacio.estado = "DISPONIBLE"
        db.commit()

    if espacio.estado != "DISPONIBLE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El espacio seleccionado no esta disponible",
        )

    try:
        if cls.cupos_disponibles is not None:
            cls.cupos_disponibles -= 1

        espacio.estado = "RESERVADO"
        codigo = uuid.uuid4().hex[:10].upper()
        qr_checkin = f"CHECKIN:{codigo}"

        payment = (
            MetodoPago.EFECTIVO
            if data.payment_method.upper() == "EFECTIVO"
            else MetodoPago.YAPE
        )

        estado_pago = (
            EstadoPagoReserva.PENDIENTE
            if payment == MetodoPago.EFECTIVO
            else EstadoPagoReserva.PAGADO
        )

        reservation = Reserva(
            codigo_reserva=codigo,
            qr_checkin=qr_checkin,
            id_usuario=user_id,
            id_clase=data.class_id,
            id_espacio=espacio.id_espacio,
            metodo_pago=payment,
            monto=float(cls.precio) if cls.precio else 0.0,
            fecha_clase=cls.fecha,
            estado_pago=estado_pago,
            estado_reserva=EstadoReserva.ACTIVA,
        )
        db.add(reservation)
        db.flush()
        registrar_evento_reserva(
            db,
            reservation,
            "RESERVA_CREADA",
            estado_reserva_nuevo=reservation.estado_reserva,
            estado_pago_nuevo=reservation.estado_pago,
            actor_tipo="CLIENTE",
            actor_id=user_id,
        )
        registrar_evento_reserva(
            db,
            reservation,
            "PAGO_PENDIENTE" if estado_pago == EstadoPagoReserva.PENDIENTE else "PAGO_CONFIRMADO",
            estado_pago_nuevo=reservation.estado_pago,
            actor_tipo="CLIENTE",
            actor_id=user_id,
        )
        db.commit()
        db.refresh(reservation)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear la reserva",
        )

    try:
        notify_reservation_created(db, user_id, reservation)
    except Exception:
        pass

    return ReservationResponseSchema.model_validate(reservation)


def cancel_reservation_service(
    db: Session,
    user_id: int,
    reservation_id: int,
    cancel_data: Optional[CancelacionCreateSchema] = None,
) -> ReservationResponseSchema:
    reservation = get_reservation_by_id(db, reservation_id)
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada",
        )

    if reservation.id_usuario != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes cancelar una reserva que no te pertenece",
        )

    if reservation.estado_reserva != EstadoReserva.ACTIVA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo puedes cancelar reservas activas",
        )

    if _class_has_started(reservation):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La clase ya inició o ya terminó",
        )

    if reservation.estado_pago == EstadoPagoReserva.REEMBOLSO_PENDIENTE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta reserva tiene una solicitud de reembolso pendiente.",
        )

    if reservation.estado_pago != EstadoPagoReserva.PENDIENTE:
        detail = (
            "Esta reserva ya fue pagada. Debes solicitar un reembolso."
            if reservation.metodo_pago == MetodoPago.YAPE
            else "Solo puedes cancelar reservas sin pago confirmado."
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )

    motivo = (
        cancel_data.motivo
        if cancel_data
        else MotivoCancelacion.OTRO
    )
    detalle = cancel_data.detalle if cancel_data else None

    try:
        old_estado_reserva = reservation.estado_reserva
        old_seat = db.query(Espacio).filter(Espacio.id_espacio == reservation.id_espacio).first()
        if old_seat:
            old_seat.estado = "DISPONIBLE"

        reservation.estado_reserva = EstadoReserva.CANCELADA

        cls = get_class_by_id(db, reservation.id_clase)
        if cls and cls.cupos_disponibles is not None:
            cls.cupos_disponibles += 1

        cancelacion = Cancelacion(
            id_reserva=reservation.id_reserva,
            motivo=motivo,
            detalle=detalle,
            cancelado_por=CanceladoPor.USUARIO,
        )
        db.add(cancelacion)
        registrar_evento_reserva(
            db,
            reservation,
            "RESERVA_CANCELADA",
            estado_reserva_anterior=old_estado_reserva,
            estado_reserva_nuevo=reservation.estado_reserva,
            descripcion="La reserva fue cancelada por el cliente.",
            actor_tipo="CLIENTE",
            actor_id=user_id,
        )
        db.commit()
        db.refresh(reservation)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al cancelar la reserva",
        )

    try:
        notify_reservation_cancelled(db, user_id, reservation)
    except Exception:
        pass

    return ReservationResponseSchema.model_validate(reservation)


def get_user_reservations_service(
    db: Session, user_id: int
) -> list[ReservationResponseSchema]:
    reservations = get_user_reservations(db, user_id)
    return [ReservationResponseSchema.model_validate(r) for r in reservations]


def get_reservation_detail_service(
    db: Session,
    user_id: int,
    reservation_id: int
) -> ReservationResponseSchema:

    from app.repositories.reservation_repository import (
        get_reservation_by_id as get_reservation_repo
    )

    reservation = get_reservation_repo(
        db,
        reservation_id
    )

    if not reservation:
        raise HTTPException(
            status_code=404,
            detail="Reserva no encontrada"
        )

    if reservation.id_usuario != user_id:
        raise HTTPException(
            status_code=403,
            detail="No puedes ver esta reserva"
        )

    response = ReservationResponseSchema.model_validate(
        reservation
    )

    if (
        response.clase
        and reservation.clase
        and reservation.clase.instructor
    ):
        response.clase.instructor_nombre = (
            reservation
            .clase
            .instructor
            .nombre_completo
        )

    return response


def change_seat_service(
    db: Session, user_id: int, reservation_id: int, new_seat_id: int
) -> ReservationResponseSchema:
    reservation = get_reservation_by_id(db, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    if reservation.id_usuario != user_id:
        raise HTTPException(status_code=403, detail="No puedes modificar esta reserva")
    if reservation.estado_reserva != EstadoReserva.ACTIVA:
        raise HTTPException(status_code=400, detail="Solo puedes cambiar asiento en reservas activas")

    old_seat = db.query(Espacio).filter(Espacio.id_espacio == reservation.id_espacio).first()
    new_seat = db.query(Espacio).filter(Espacio.id_espacio == new_seat_id).first()

    if not new_seat or new_seat.id_clase != reservation.id_clase:
        raise HTTPException(status_code=404, detail="El nuevo espacio no pertenece a esta clase")
    if new_seat.estado != "DISPONIBLE":
        raise HTTPException(status_code=400, detail="El nuevo espacio no está disponible")

    try:
        old_seat_code = old_seat.codigo_espacio if old_seat else None
        new_seat_code = new_seat.codigo_espacio
        if old_seat:
            old_seat.estado = "DISPONIBLE"
        new_seat.estado = "RESERVADO"
        reservation.id_espacio = new_seat.id_espacio
        db.execute(
            text("""
                INSERT INTO cambios_espacio (id_reserva, id_espacio_anterior, id_espacio_nuevo)
                VALUES (:id_reserva, :id_espacio_anterior, :id_espacio_nuevo)
            """),
            {
                "id_reserva": reservation.id_reserva,
                "id_espacio_anterior": old_seat.id_espacio if old_seat else None,
                "id_espacio_nuevo": new_seat.id_espacio,
            },
        )
        registrar_evento_reserva(
            db,
            reservation,
            "ASIENTO_CAMBIADO",
            descripcion=(
                f"El espacio cambio de {old_seat_code} a {new_seat_code}."
                if old_seat_code
                else f"El espacio cambio a {new_seat_code}."
            ),
            actor_tipo="CLIENTE",
            actor_id=user_id,
        )
        db.commit()
        db.refresh(reservation)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al cambiar el asiento")

    try:
        notify_seat_changed(
            db, user_id, reservation,
            old_seat.codigo_espacio if old_seat else "",
            new_seat.codigo_espacio,
        )
    except Exception:
        pass

    return ReservationResponseSchema.model_validate(reservation)


def get_all_reservations_service(
    db: Session,
) -> list[ReservationResponseSchema]:
    reservations = get_all_reservations(db)
    return [ReservationResponseSchema.model_validate(r) for r in reservations]


def mark_reservation_as_paid_service(
    db: Session, reservation_id: int
) -> ReservationResponseSchema:
    reservation = get_reservation_by_id(db, reservation_id)
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada",
        )

    if reservation.estado_reserva != EstadoReserva.ACTIVA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo puedes marcar como pagadas reservas activas",
        )

    if reservation.estado_pago != EstadoPagoReserva.PENDIENTE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La reserva no está pendiente de pago",
        )

    try:
        old_estado_pago = reservation.estado_pago
        reservation.estado_pago = EstadoPagoReserva.PAGADO
        payment = Pago(
            id_reserva=reservation.id_reserva,
            metodo_pago=MetodoPagoPago.EFECTIVO,
            estado=EstadoPago.CONFIRMADO,
            monto=reservation.monto,
            fecha_pago=datetime.now(),
            codigo_operacion=f"EFECTIVO-{reservation.codigo_reserva}",
        )
        db.add(payment)
        registrar_evento_reserva(
            db,
            reservation,
            "PAGO_CONFIRMADO",
            estado_pago_anterior=old_estado_pago,
            estado_pago_nuevo=reservation.estado_pago,
            actor_tipo="ADMIN",
        )
        db.commit()
        db.refresh(reservation)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al marcar la reserva como pagada",
        )

    return ReservationResponseSchema.model_validate(reservation)

def request_refund_service(
    db: Session,
    user_id: int,
    reservation_id: int,
):
    reservation = get_reservation_by_id(
        db,
        reservation_id
    )

    if not reservation:
        raise HTTPException(
            status_code=404,
            detail="Reserva no encontrada"
        )

    if reservation.id_usuario != user_id:
        raise HTTPException(
            status_code=403,
            detail="No autorizado"
        )

    if reservation.estado_pago != EstadoPagoReserva.PAGADO:
        raise HTTPException(
            status_code=400,
            detail="Solo reservas pagadas pueden solicitar reembolso"
        )

    if reservation.metodo_pago != MetodoPago.YAPE:
        raise HTTPException(
            status_code=400,
            detail="Solo reservas pagadas por Yape pueden solicitar reembolso"
        )

    if reservation.estado_reserva != EstadoReserva.ACTIVA:
        raise HTTPException(
            status_code=400,
            detail="La reserva no es elegible"
        )

    if _class_has_started(reservation):
        raise HTTPException(
            status_code=400,
            detail="La clase ya inició o ya terminó"
        )

    try:
        old_estado_pago = reservation.estado_pago
        reservation.estado_pago = (
            EstadoPagoReserva.REEMBOLSO_PENDIENTE
        )
        registrar_evento_reserva(
            db,
            reservation,
            "REEMBOLSO_SOLICITADO",
            estado_pago_anterior=old_estado_pago,
            estado_pago_nuevo=reservation.estado_pago,
            actor_tipo="CLIENTE",
            actor_id=user_id,
        )
        db.commit()
        db.refresh(reservation)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error al solicitar el reembolso"
        )

    return ReservationResponseSchema.model_validate(
        reservation
    )


def cancel_refund_request_service(
    db: Session,
    user_id: int,
    reservation_id: int,
) -> ReservationResponseSchema:
    reservation = get_reservation_by_id(db, reservation_id)

    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada",
        )

    if reservation.id_usuario != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado",
        )

    if reservation.metodo_pago != MetodoPago.YAPE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo reservas pagadas por Yape pueden cancelar una solicitud de reembolso",
        )

    if reservation.estado_pago != EstadoPagoReserva.REEMBOLSO_PENDIENTE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta solicitud de reembolso ya no está pendiente.",
        )

    if reservation.estado_reserva != EstadoReserva.ACTIVA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La reserva no es elegible",
        )

    if _class_has_started(reservation):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La clase ya inició o ya terminó",
        )

    try:
        old_estado_pago = reservation.estado_pago
        old_estado_reserva = reservation.estado_reserva
        reservation.estado_pago = EstadoPagoReserva.PAGADO
        registrar_evento_reserva(
            db,
            reservation,
            "REEMBOLSO_SOLICITUD_CANCELADA",
            estado_reserva_anterior=old_estado_reserva,
            estado_reserva_nuevo=reservation.estado_reserva,
            estado_pago_anterior=old_estado_pago,
            estado_pago_nuevo=reservation.estado_pago,
            descripcion="El cliente decidió mantener la reserva y canceló la solicitud de reembolso.",
            actor_tipo="CLIENTE",
            actor_id=user_id,
        )
        db.commit()
        db.refresh(reservation)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al cancelar la solicitud de reembolso",
        )

    try:
        notify_refund_request_cancelled(db, user_id, reservation)
    except Exception:
        pass

    return ReservationResponseSchema.model_validate(reservation)

def approve_refund_service(
    db: Session,
    admin_id: int,
    reservation_id: int
) -> ReservationResponseSchema:
    reservation = get_reservation_by_id(db, reservation_id)

    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada",
        )

    if reservation.estado_pago != EstadoPagoReserva.REEMBOLSO_PENDIENTE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La reserva no tiene un reembolso pendiente",
        )

    if reservation.estado_reserva != EstadoReserva.ACTIVA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La reserva no es elegible para reembolso",
        )

    cls = reservation.clase or get_class_by_id(db, reservation.id_clase)
    if cls and cls.fecha and cls.hora_inicio:
        class_start = datetime.combine(cls.fecha, cls.hora_inicio)
        if datetime.now() >= class_start:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La clase ya inició o ya terminó",
            )

    try:
        old_estado_pago = reservation.estado_pago
        old_estado_reserva = reservation.estado_reserva
        old_seat = db.query(Espacio).filter(
            Espacio.id_espacio == reservation.id_espacio
        ).first()
        if old_seat:
            old_seat.estado = "DISPONIBLE"

        if cls and cls.cupos_disponibles is not None:
            cls.cupos_disponibles += 1

        reservation.estado_pago = EstadoPagoReserva.REEMBOLSADO
        reservation.estado_reserva = EstadoReserva.CANCELADA

        cancelacion = Cancelacion(
            id_reserva=reservation.id_reserva,
            motivo=MotivoCancelacion.ECONOMICO,
            detalle="Reembolso aprobado por el administrador",
            cancelado_por=CanceladoPor.ADMIN,
            id_admin=admin_id,
        )
        db.add(cancelacion)
        registrar_evento_reserva(
            db,
            reservation,
            "REEMBOLSO_APROBADO",
            estado_pago_anterior=old_estado_pago,
            estado_pago_nuevo=reservation.estado_pago,
            actor_tipo="ADMIN",
            actor_id=admin_id,
        )
        registrar_evento_reserva(
            db,
            reservation,
            "RESERVA_CANCELADA",
            estado_reserva_anterior=old_estado_reserva,
            estado_reserva_nuevo=reservation.estado_reserva,
            descripcion="La reserva fue cancelada como consecuencia del reembolso aprobado.",
            actor_tipo="ADMIN",
            actor_id=admin_id,
        )

        db.commit()
        db.refresh(reservation)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al aprobar el reembolso",
        )

    try:
        notify_refund_processed(
            db,
            reservation.id_usuario,
            float(reservation.monto),
            cls.nombre_clase if cls else "Clase",
            reservation.id_reserva,
        )
    except Exception:
        pass

    return ReservationResponseSchema.model_validate(reservation)
