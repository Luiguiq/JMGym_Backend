from datetime import date, datetime
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


class PaymentHistoryResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_pago: int
    id_reserva: int
    metodo_pago: MetodoPago
    estado: EstadoPago
    monto: float
    codigo_operacion: Optional[str] = None
    fecha_pago: Optional[datetime] = None
    nombre_clase: Optional[str] = None
    fecha_clase: Optional[date] = None
    hora_inicio: Optional[str] = None
    hora_fin: Optional[str] = None
    codigo_reserva: Optional[str] = None


class PaymentConfirmSchema(BaseModel):
    estado: EstadoPago
    confirmado_por_admin: int
