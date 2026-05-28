from enum import Enum


class EstadoEspacio(str, Enum):
    DISPONIBLE = "DISPONIBLE"
    OCUPADO = "OCUPADO"
    RESERVADO = "RESERVADO"
    EN_ESPERA = "EN_ESPERA"
