from enum import Enum


class MotivoCancelacion(str, Enum):
    CAMBIO_HORARIO = "CAMBIO_HORARIO"
    SALUD = "SALUD"
    ECONOMICO = "ECONOMICO"
    CAMBIO_SECTOR = "CAMBIO_SECTOR"
    CLASE_CANCELADA = "CLASE_CANCELADA"
    VENCIMIENTO_PAGO = "VENCIMIENTO_PAGO"
    OTRO = "OTRO"


class CanceladoPor(str, Enum):
    USUARIO = "USUARIO"
    ADMIN = "ADMIN"
    SISTEMA = "SISTEMA"
