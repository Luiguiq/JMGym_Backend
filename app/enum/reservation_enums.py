from enum import Enum


class MetodoPago(str, Enum):
    YAPE = "YAPE"
    EFECTIVO = "EFECTIVO"


class EstadoPagoReserva(str, Enum):
    PENDIENTE = "PENDIENTE"
    PAGADO = "PAGADO"
    VENCIDO = "VENCIDO"
    REEMBOLSADO = "REEMBOLSADO"


class EstadoReserva(str, Enum):
    ACTIVA = "ACTIVA"
    CANCELADA = "CANCELADA"
    FINALIZADA = "FINALIZADA"
