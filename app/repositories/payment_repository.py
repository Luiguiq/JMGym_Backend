from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.payment_model import Pago
from app.models.reservation_model import Reserva
from app.enum.payment_enums import EstadoPago


def create_payment(db: Session, payment_data: dict) -> Pago:
    payment = Pago(**payment_data)
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def get_payment_by_id(db: Session, payment_id: int) -> Optional[Pago]:
    return db.query(Pago).filter(Pago.id_pago == payment_id).first()


def get_payments_by_user(db: Session, user_id: int) -> list[Pago]:
    return (
        db.query(Pago)
        .join(Pago.reserva)
        .filter(Reserva.id_usuario == user_id)
        .order_by(Pago.fecha_pago.desc(), Pago.id_pago.desc())
        .all()
    )


def get_payments_pending(db: Session) -> list[Pago]:
    return (
        db.query(Pago)
        .filter(Pago.estado == EstadoPago.PENDIENTE)
        .all()
    )


def confirm_payment(
    db: Session,
    payment_id: int,
    estado: EstadoPago,
    admin_id: int,
) -> Optional[Pago]:
    payment = get_payment_by_id(db, payment_id)
    if not payment:
        return None

    payment.estado = estado
    payment.confirmado_por_admin = admin_id
    payment.fecha_pago = datetime.now()
    db.commit()
    db.refresh(payment)
    return payment
