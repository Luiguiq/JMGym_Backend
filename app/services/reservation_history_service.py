from enum import Enum
from typing import Optional

from sqlalchemy.orm import Session

from app.models.reservation_history_model import ReservaHistorialEstado


EVENT_TITLES = {
    "RESERVA_CREADA": "Reserva creada",
    "PAGO_PENDIENTE": "Pago pendiente",
    "PAGO_CONFIRMADO": "Pago confirmado",
    "PAGO_VENCIDO": "Pago vencido",
    "PAGO_RECHAZADO": "Pago rechazado",
    "PAGO_REEMBOLSADO": "Pago reembolsado",
    "RESERVA_CANCELADA": "Reserva cancelada",
    "REEMBOLSO_SOLICITADO": "Reembolso solicitado",
    "REEMBOLSO_APROBADO": "Reembolso aprobado",
    "REEMBOLSO_RECHAZADO": "Reembolso rechazado",
    "RESERVA_COMPLETADA": "Reserva completada",
    "RESERVA_FINALIZADA": "Reserva finalizada",
    "ASIENTO_CAMBIADO": "Espacio cambiado",
}

EVENT_DESCRIPTIONS = {
    "RESERVA_CREADA": "La reserva fue registrada correctamente.",
    "PAGO_PENDIENTE": "La reserva quedo pendiente de pago.",
    "PAGO_CONFIRMADO": "El pago de la reserva fue confirmado.",
    "PAGO_VENCIDO": "El pago de la reserva vencio.",
    "PAGO_RECHAZADO": "El pago fue rechazado y la reserva quedo pendiente.",
    "PAGO_REEMBOLSADO": "El pago de la reserva fue reembolsado.",
    "RESERVA_CANCELADA": "La reserva fue cancelada.",
    "REEMBOLSO_SOLICITADO": "La solicitud de reembolso fue enviada para revision.",
    "REEMBOLSO_APROBADO": "El reembolso fue aprobado por un administrador.",
    "REEMBOLSO_RECHAZADO": "El reembolso fue rechazado.",
    "RESERVA_COMPLETADA": "La reserva fue completada.",
    "RESERVA_FINALIZADA": "La reserva fue finalizada.",
    "ASIENTO_CAMBIADO": "El espacio de la reserva fue actualizado.",
}


def normalizar_estado(value) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, Enum):
        return value.value
    return str(value)


def registrar_evento_reserva(
    db: Session,
    reserva,
    tipo_evento: str,
    estado_reserva_anterior=None,
    estado_reserva_nuevo=None,
    estado_pago_anterior=None,
    estado_pago_nuevo=None,
    descripcion: Optional[str] = None,
    actor_tipo: Optional[str] = None,
    actor_id: Optional[int] = None,
) -> Optional[ReservaHistorialEstado]:
    reserva_anterior = normalizar_estado(estado_reserva_anterior)
    reserva_nuevo = normalizar_estado(estado_reserva_nuevo)
    pago_anterior = normalizar_estado(estado_pago_anterior)
    pago_nuevo = normalizar_estado(estado_pago_nuevo)

    states_unchanged = (
        reserva_anterior == reserva_nuevo
        and pago_anterior == pago_nuevo
        and tipo_evento not in {"RESERVA_CREADA", "PAGO_PENDIENTE", "ASIENTO_CAMBIADO"}
    )
    if states_unchanged:
        return None

    historial = ReservaHistorialEstado(
        id_reserva=reserva.id_reserva,
        tipo_evento=tipo_evento,
        estado_reserva_anterior=reserva_anterior,
        estado_reserva_nuevo=reserva_nuevo,
        estado_pago_anterior=pago_anterior,
        estado_pago_nuevo=pago_nuevo,
        descripcion=descripcion or EVENT_DESCRIPTIONS.get(tipo_evento),
        actor_tipo=actor_tipo,
        actor_id=actor_id,
    )
    db.add(historial)
    return historial
