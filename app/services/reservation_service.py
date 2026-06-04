import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.reservation_model import Reserva
from app.models.seat_model import Espacio
from app.repositories.class_repository import get_class_by_id
from app.repositories.reservation_repository import (
    get_user_reservations,
    get_reservation_by_id,
    get_all_reservations,
)
from app.schemas.reservation_schemas import ReservationCreateSchema, ReservationResponseSchema
from app.enum.reservation_enums import MetodoPago, EstadoPagoReserva, EstadoReserva


def create_reservation_service(
    db: Session, user_id: int, data: ReservationCreateSchema
) -> ReservationResponseSchema:
    cls = get_class_by_id(db, data.class_id)
    if not cls:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clase no encontrada",
        )

    if cls.cupos_disponibles is not None and cls.cupos_disponibles <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay cupos disponibles",
        )

    existing = (
        db.query(Reserva)
        .filter(
            Reserva.id_usuario == user_id,
            Reserva.id_clase == data.class_id,
            Reserva.estado_reserva == EstadoReserva.ACTIVA,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya tienes una reserva activa para esta clase",
        )

    espacio = (
        db.query(Espacio)
        .filter(
            Espacio.id_espacio == data.seat_id,
            Espacio.id_clase == data.class_id,
        )
        .first()
    )
    if not espacio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Espacio no encontrado para esta clase",
        )

    if espacio.estado != "DISPONIBLE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El espacio seleccionado no esta disponible",
        )

    try:
        if cls.cupos_disponibles is not None:
            cls.cupos_disponibles -= 1

        espacio.estado = "RESERVADO"
        codigo = uuid.uuid4().hex[:10].upper()

        reservation = Reserva(
            codigo_reserva=codigo,
            id_usuario=user_id,
            id_clase=data.class_id,
            id_espacio=espacio.id_espacio,
            metodo_pago=MetodoPago.YAPE,
            monto=float(cls.precio) if cls.precio else 0.0,
            fecha_clase=cls.fecha,
            estado_pago=EstadoPagoReserva.PAGADO,
            estado_reserva=EstadoReserva.ACTIVA,
        )
        db.add(reservation)
        db.commit()
        db.refresh(reservation)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear la reserva",
        )

    return ReservationResponseSchema.model_validate(reservation)


def cancel_reservation_service(
    db: Session, user_id: int, reservation_id: int
) -> ReservationResponseSchema:
    reservation = get_reservation_by_id(db, reservation_id)
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada",
        )

    if reservation.id_usuario != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes cancelar una reserva que no te pertenece",
        )

    if reservation.estado_reserva != EstadoReserva.ACTIVA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo puedes cancelar reservas activas",
        )

    try:
        reservation.estado_reserva = EstadoReserva.CANCELADA

        cls = get_class_by_id(db, reservation.id_clase)
        if cls and cls.cupos_disponibles is not None:
            cls.cupos_disponibles += 1

        db.commit()
        db.refresh(reservation)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al cancelar la reserva",
        )

    return ReservationResponseSchema.model_validate(reservation)


def get_user_reservations_service(
    db: Session, user_id: int
) -> list[ReservationResponseSchema]:
    reservations = get_user_reservations(db, user_id)
    return [ReservationResponseSchema.model_validate(r) for r in reservations]


def get_all_reservations_service(
    db: Session,
) -> list[ReservationResponseSchema]:
    reservations = get_all_reservations(db)
    return [ReservationResponseSchema.model_validate(r) for r in reservations]
