from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.orm import Session

from app.models.user_model import Usuario
from app.models.seat_model import Espacio
from app.models.cancelacion_model import Cancelacion
from app.schemas.reservation_schemas import ReservationCreateSchema, ReservationResponseSchema
from app.schemas.cancelacion_schemas import CancelacionCreateSchema
from app.security import get_db, get_current_user, get_current_admin
from app.repositories.reservation_repository import get_reservation_by_id
from app.repositories.class_repository import get_class_by_id
from app.enum.reservation_enums import EstadoReserva
from app.enum.cancelacion_enums import CanceladoPor
from app.enum.notification_enums import TipoNotificacion
from app.repositories.notification_repository import create_notification as create_notification_repo
from app.services.reservation_service import (
    create_reservation_service,
    get_user_reservations_service,
    get_reservation_detail_service,
    get_all_reservations_service,
    cancel_reservation_service,
    change_seat_service,
    mark_reservation_as_paid_service,
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


@router.get("/{reservation_id}", response_model=ReservationResponseSchema)
def get_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return get_reservation_detail_service(db, current_user.id_usuario, reservation_id)


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
    
    print("CLASE:", reservation.clase)
    print("INSTRUCTOR:", reservation.clase.instructor)
    print(
        "NOMBRE:",
        reservation.clase.instructor.nombre_completo
        if reservation.clase.instructor
        else None
    )

    return ReservationResponseSchema.model_validate(reservation)

@router.patch("/{reservation_id}/seat", response_model=ReservationResponseSchema)
def change_seat(
    reservation_id: int,
    seat_id: int = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return change_seat_service(db, current_user.id_usuario, reservation_id, seat_id)


@router.patch("/{reservation_id}/mark-paid", response_model=ReservationResponseSchema)
def mark_reservation_as_paid(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    return mark_reservation_as_paid_service(db, reservation_id)


@router.patch("/{reservation_id}/cancel", response_model=ReservationResponseSchema)
def cancel_reservation(
    reservation_id: int,
    cancel_data: Optional[CancelacionCreateSchema] = Body(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return cancel_reservation_service(db, current_user.id_usuario, reservation_id, cancel_data)


@router.delete("/{reservation_id}")
def delete_reservation(
    reservation_id: int,
    cancel_data: Optional[CancelacionCreateSchema] = Body(None),
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

    motivo = cancel_data.motivo if cancel_data else "CLASE_CANCELADA"
    detalle = cancel_data.detalle if cancel_data else None

    try:
        old_seat = db.query(Espacio).filter(Espacio.id_espacio == reservation.id_espacio).first()
        if old_seat:
            old_seat.estado = "DISPONIBLE"

        reservation.estado_reserva = EstadoReserva.CANCELADA

        cancelacion = Cancelacion(
            id_reserva=reservation.id_reserva,
            motivo=motivo,
            detalle=detalle,
            cancelado_por=CanceladoPor.ADMIN,
        )
        db.add(cancelacion)

        cls = get_class_by_id(db, reservation.id_clase)
        if cls and cls.cupos_disponibles is not None:
            cls.cupos_disponibles += 1

        user_id = reservation.id_usuario
        clase_nombre = reservation.clase.nombre_clase if reservation.clase else "Clase"
        clase_fecha = reservation.fecha_clase
        id_reserva_val = reservation.id_reserva
        id_clase_val = reservation.id_clase

        db.commit()

        print(f"[DELETE_RESERVATION] Creating notification for user {user_id}, clase {clase_nombre}, fecha {clase_fecha}")
        try:
            notif = create_notification_repo(db, {
                "id_usuario": user_id,
                "titulo": "Reserva cancelada",
                "mensaje": f"Tu reserva para {clase_nombre} el {clase_fecha} ha sido cancelada por un administrador.",
                "tipo": TipoNotificacion.RESERVA_CANCELADA,
                "id_reserva": id_reserva_val,
                "id_clase": id_clase_val,
            })
            print(f"[DELETE_RESERVATION] Notification created: {notif.id_notificacion}")
        except Exception as exc:
            import logging
            logging.error(f"[DELETE_RESERVATION] NOTIF ERROR: {exc}")

        return {"message": "Reserva cancelada correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cancelar la reserva: {str(e)}",
        )
