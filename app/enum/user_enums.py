from enum import Enum


class EstadoUsuario(str, Enum):
    ACTIVO = "ACTIVO"
    BLOQUEADO = "BLOQUEADO"
