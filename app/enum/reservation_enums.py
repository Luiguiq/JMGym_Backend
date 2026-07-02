from enum import Enum


class MetodoPago(str, Enum):
    YAPE = "YAPE"
    EFECTIVO = "EFECTIVO"


class EstadoPagoReserva(str, Enum):
    PENDIENTE = "PENDIENTE"
    PAGADO = "PAGADO"
    RECHAZADO = "RECHAZADO"
    VENCIDO = "VENCIDO"
    REEMBOLSO_PENDIENTE = "REEMBOLSO_PENDIENTE"
    REEMBOLSADO = "REEMBOLSADO"


class EstadoReserva(str, Enum):
    ACTIVA = "ACTIVA"
    CANCELADA = "CANCELADA"
    FINALIZADA = "FINALIZADA"
