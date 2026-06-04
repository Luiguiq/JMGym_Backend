from datetime import date, datetime, time
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.enum.class_enums import IntensidadClase, EstadoClase
from app.enum.espacio_enums import EstadoEspacio


class ClassCreateSchema(BaseModel):
    nombre_clase: str
    id_genero: int
    id_instructor: int
    descripcion: Optional[str] = None
    intensidad: IntensidadClase = IntensidadClase.MEDIA
    reglas_vestimenta: Optional[str] = None
    duracion_minutos: int
    fecha: date
    hora_inicio: time
    hora_fin: time
    precio: float = 0.00
    cupos_totales: int = 40
    cupos_disponibles: int = 40
    alumnos_minimos: int = 5
    fecha_limite_cancelacion: Optional[datetime] = None
    imagen_clase: Optional[str] = None
    motivo_cancelacion: Optional[str] = None


class ClassUpdateSchema(BaseModel):
    nombre_clase: Optional[str] = None
    id_genero: Optional[int] = None
    id_instructor: Optional[int] = None
    descripcion: Optional[str] = None
    intensidad: Optional[IntensidadClase] = None
    reglas_vestimenta: Optional[str] = None
    duracion_minutos: Optional[int] = None
    fecha: Optional[date] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    precio: Optional[float] = None
    cupos_totales: Optional[int] = None
    cupos_disponibles: Optional[int] = None
    alumnos_minimos: Optional[int] = None
    fecha_limite_cancelacion: Optional[datetime] = None
    imagen_clase: Optional[str] = None
    estado: Optional[EstadoClase] = None
    motivo_cancelacion: Optional[str] = None


class ClassResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_clase: int
    nombre_clase: str
    id_genero: int
    id_instructor: int
    instructor_nombre: Optional[str] = None
    descripcion: Optional[str] = None
    intensidad: IntensidadClase
    reglas_vestimenta: Optional[str] = None
    duracion_minutos: int
    fecha: date
    hora_inicio: time
    hora_fin: time
    precio: float
    cupos_totales: Optional[int] = None
    cupos_disponibles: Optional[int] = None
    alumnos_minimos: Optional[int] = None
    fecha_limite_cancelacion: Optional[datetime] = None
    imagen_clase: Optional[str] = None
    estado: Optional[EstadoClase] = None
    motivo_cancelacion: Optional[str] = None
    fecha_creacion: datetime


class SeatResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_espacio: int
    id_clase: int
    codigo_espacio: str
    estado: EstadoEspacio
