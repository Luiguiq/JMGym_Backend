from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.payment_model import Pago
from app.repositories.payment_repository import create_payment, get_payment_by_id, get_payments_pending
from app.repositories.reservation_repository import get_reservation_by_id
from app.schemas.payment_schemas import PaymentCreateSchema, PaymentResponseSchema, PaymentConfirmSchema, PaymentHistoryResponseSchema
from app.enum.payment_enums import EstadoPago
from app.enum.reservation_enums import EstadoPagoReserva
from app.services.notification_service import notify_payment_confirmed


def create_payment_service(
    db: Session, data: PaymentCreateSchema
) -> PaymentResponseSchema:
    reservation = get_reservation_by_id(db, data.id_reserva)
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada",
        )

    payment = create_payment(
        db,
        {
            "id_reserva": data.id_reserva,
            "metodo_pago": data.metodo_pago,
            "monto": data.monto,
            "codigo_operacion": data.codigo_operacion,
            "qr_yape": data.qr_yape,
        },
    )
    return PaymentResponseSchema.model_validate(payment)


def confirm_payment_service(
    db: Session, payment_id: int, data: PaymentConfirmSchema
) -> PaymentResponseSchema:
    payment = get_payment_by_id(db, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pago no encontrado",
        )

    if payment.estado != EstadoPago.PENDIENTE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El pago ya fue procesado",
        )

    try:
        payment.estado = data.estado
        payment.confirmado_por_admin = data.confirmado_por_admin
        payment.fecha_pago = datetime.now()

        reservation = payment.reserva
        was_confirmed = False
        if data.estado == EstadoPago.CONFIRMADO:
            reservation.estado_pago = EstadoPagoReserva.PAGADO
            was_confirmed = True
        elif data.estado == EstadoPago.RECHAZADO:
            reservation.estado_pago = EstadoPagoReserva.PENDIENTE
        elif data.estado == EstadoPago.REEMBOLSADO:
            reservation.estado_pago = EstadoPagoReserva.PENDIENTE

        db.commit()
        db.refresh(payment)

        if was_confirmed:
            notify_payment_confirmed(
                db, reservation.id_usuario, reservation
            )
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al confirmar el pago",
        )

    return PaymentResponseSchema.model_validate(payment)


def get_my_payments_service(db: Session, user_id: int) -> list[PaymentHistoryResponseSchema]:
    from app.repositories.payment_repository import get_payments_by_user
    payments = get_payments_by_user(db, user_id)
    result = []
    for p in payments:
        reserva = p.reserva
        clase = reserva.clase if reserva else None
        result.append(PaymentHistoryResponseSchema(
            id_pago=p.id_pago,
            id_reserva=p.id_reserva,
            metodo_pago=p.metodo_pago,
            estado=p.estado,
            monto=p.monto,
            codigo_operacion=p.codigo_operacion,
            fecha_pago=p.fecha_pago,
            nombre_clase=clase.nombre_clase if clase else None,
            fecha_clase=clase.fecha if clase else (reserva.fecha_clase if reserva else None),
            hora_inicio=str(clase.hora_inicio)[:5] if clase and clase.hora_inicio else None,
            hora_fin=str(clase.hora_fin)[:5] if clase and clase.hora_fin else None,
            codigo_reserva=reserva.codigo_reserva if reserva else None,
        ))
    return result


def get_pending_payments_service(
    db: Session,
) -> list[PaymentResponseSchema]:
    payments = get_payments_pending(db)
    return [PaymentResponseSchema.model_validate(p) for p in payments]