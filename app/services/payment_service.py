from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.payment_model import Pago
from app.repositories.payment_repository import create_payment, get_payment_by_id, get_payments_pending
from app.repositories.reservation_repository import get_reservation_by_id
from app.schemas.payment_schemas import PaymentCreateSchema, PaymentResponseSchema, PaymentConfirmSchema
from app.enum.payment_enums import EstadoPago
from app.enum.reservation_enums import EstadoPagoReserva


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
        if data.estado == EstadoPago.CONFIRMADO:
            reservation.estado_pago = EstadoPagoReserva.PAGADO
        elif data.estado == EstadoPago.RECHAZADO:
            reservation.estado_pago = EstadoPagoReserva.PENDIENTE
        elif data.estado == EstadoPago.REEMBOLSADO:
            reservation.estado_pago = EstadoPagoReserva.PENDIENTE

        db.commit()
        db.refresh(payment)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al confirmar el pago",
        )

    return PaymentResponseSchema.model_validate(payment)


def get_pending_payments_service(
    db: Session,
) -> list[PaymentResponseSchema]:
    payments = get_payments_pending(db)
    return [PaymentResponseSchema.model_validate(p) for p in payments]
