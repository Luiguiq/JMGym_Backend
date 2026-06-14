from fastapi import APIRouter, Depends
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
