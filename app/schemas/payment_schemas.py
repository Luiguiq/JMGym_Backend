from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.enum.payment_enums import MetodoPago, EstadoPago


class PaymentCreateSchema(BaseModel):
    id_reserva: int
    metodo_pago: MetodoPago
    monto: float
    codigo_operacion: Optional[str] = None
    qr_yape: Optional[str] = None


class PaymentResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_pago: int
    id_reserva: int
    metodo_pago: MetodoPago
    estado: EstadoPago
    monto: float
    codigo_operacion: Optional[str] = None
    fecha_pago: Optional[datetime] = None
    qr_yape: Optional[str] = None
    confirmado_por_admin: Optional[int] = None


class PaymentConfirmSchema(BaseModel):
    estado: EstadoPago
    confirmado_por_admin: int
