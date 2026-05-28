from enum import Enum


class IntensidadClase(str, Enum):
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"


class EstadoClase(str, Enum):
    ACTIVA = "ACTIVA"
    CANCELADA = "CANCELADA"
    COMPLETA = "COMPLETA"
    FINALIZADA = "FINALIZADA"
