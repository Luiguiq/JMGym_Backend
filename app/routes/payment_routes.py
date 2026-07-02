from datetime import datetime

from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.models.user_model import Usuario
from app.schemas.payment_schemas import PaymentCreateSchema, PaymentResponseSchema, PaymentConfirmSchema, PaymentHistoryResponseSchema
from app.security import get_db, get_current_user
from app.services.payment_service import (
    create_payment_service,
    get_pending_payments_service,
    confirm_payment_service,
    get_my_payments_service,
)
from app.services.flow_service import get_flow_payment_status
from app.models.reservation_model import Reserva
from app.models.payment_model import Pago
from app.enum.payment_enums import EstadoPago, MetodoPago
from app.enum.reservation_enums import EstadoPagoReserva
from app.services.notification_service import notify_payment_confirmed

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("", response_model=PaymentResponseSchema, status_code=201)
def create_payment(data: PaymentCreateSchema, db: Session = Depends(get_db)):
    return create_payment_service(db, data)


@router.get("/me", response_model=list[PaymentHistoryResponseSchema])
def my_payments(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return get_my_payments_service(db, current_user.id_usuario)


@router.get("/pending", response_model=list[PaymentResponseSchema])
def list_pending_payments(db: Session = Depends(get_db)):
    return get_pending_payments_service(db)


@router.patch("/{payment_id}/confirm", response_model=PaymentResponseSchema)
def confirm_payment(
    payment_id: int,
    data: PaymentConfirmSchema,
    db: Session = Depends(get_db),
):
    return confirm_payment_service(db, payment_id, data)


@router.post("/flow/confirmation")
def flow_confirmation(
    token: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        status_data = get_flow_payment_status(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error al verificar pago en Flow: {str(e)}",
        )

    flow_status = status_data.get("status")
    commerce_order = status_data.get("commerceOrder", "")
    amount = status_data.get("amount", 0)
    flow_order = status_data.get("flowOrder", "")

    reservation = (
        db.query(Reserva)
        .filter(Reserva.codigo_reserva == commerce_order)
        .first()
    )
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada",
        )

    if flow_status == 1:
        if reservation.estado_pago == EstadoPagoReserva.PAGADO:
            return {"status": "success", "message": "Pago ya confirmado anteriormente"}

        reservation.estado_pago = EstadoPagoReserva.PAGADO

        payment = Pago(
            id_reserva=reservation.id_reserva,
            metodo_pago=MetodoPago.YAPE,
            estado=EstadoPago.CONFIRMADO,
            monto=float(amount),
            codigo_operacion=f"FLOW-{flow_order}",
            fecha_pago=datetime.now(),
        )
        db.add(payment)
        db.commit()

        try:
            notify_payment_confirmed(db, reservation.id_usuario, reservation)
        except Exception:
            pass

        return {"status": "success", "message": "Pago confirmado"}

    elif flow_status == 2:
        if reservation.estado_pago != EstadoPagoReserva.PENDIENTE:
            return {"status": "rejected", "message": "Estado actual no permite cambio a rechazado"}
        reservation.estado_pago = EstadoPagoReserva.RECHAZADO
        db.commit()
        return {"status": "rejected", "message": "Pago rechazado"}

    elif flow_status in (3, 4):
        return {"status": "cancelled", "message": "Pago cancelado o reembolsado"}

    return {"status": "pending", "message": "Pago pendiente"}
