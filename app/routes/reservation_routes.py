from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.user_model import Usuario
from app.schemas.reservation_schemas import ReservationCreateSchema, ReservationResponseSchema
from app.security import get_db, get_current_user
from app.repositories.reservation_repository import get_reservation_by_id
from app.repositories.class_repository import get_class_by_id
from app.enum.reservation_enums import EstadoReserva
from app.services.reservation_service import (
    create_reservation_service,
    get_user_reservations_service,
    get_all_reservations_service,
    cancel_reservation_service,
)

router = APIRouter(prefix="/reservations", tags=["Reservations"])


@router.post("", response_model=ReservationResponseSchema, status_code=201)
def create_reservation(
    data: ReservationCreateSchema,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return create_reservation_service(db, current_user.id_usuario, data)


@router.get("/me", response_model=list[ReservationResponseSchema])
def my_reservations(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return get_user_reservations_service(db, current_user.id_usuario)


@router.get("", response_model=list[ReservationResponseSchema])
def list_all_reservations(
    db: Session = Depends(get_db),
):
    return get_all_reservations_service(db)

@router.get("/{reservation_id}", response_model=ReservationResponseSchema)
def get_reservation_detail(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    reservation = get_reservation_by_id(db, reservation_id)

    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada",
        )

    if reservation.id_usuario != current_user.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes acceder a esta reserva",
        )

    return ReservationResponseSchema.model_validate(reservation)

@router.patch("/{reservation_id}/cancel", response_model=ReservationResponseSchema)
def cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return cancel_reservation_service(db, current_user.id_usuario, reservation_id)


@router.delete("/{reservation_id}")
def delete_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
):
    reservation = get_reservation_by_id(db, reservation_id)
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada",
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
        return {"message": "Reserva cancelada correctamente"}
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al cancelar la reserva",
        )
