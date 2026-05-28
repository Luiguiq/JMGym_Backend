from enum import Enum


class EstadoPago(str, Enum):
    PENDIENTE = "PENDIENTE"
    CONFIRMADO = "CONFIRMADO"
    RECHAZADO = "RECHAZADO"
    REEMBOLSADO = "REEMBOLSADO"


class MetodoPago(str, Enum):
    YAPE = "YAPE"
    EFECTIVO = "EFECTIVO"


class EstadoReembolso(str, Enum):
    PENDIENTE = "PENDIENTE"
    COMPLETADO = "COMPLETADO"
    RECHAZADO = "RECHAZADO"
