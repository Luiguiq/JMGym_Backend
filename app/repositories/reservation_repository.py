from typing import Optional

from sqlalchemy.orm import Session

from app.models.reservation_model import Reserva


def create_reservation(db: Session, reservation_data: dict) -> Reserva:
    reservation = Reserva(**reservation_data)
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


def get_user_reservations(db: Session, user_id: int) -> list[Reserva]:
    return (
        db.query(Reserva)
        .filter(Reserva.id_usuario == user_id)
        .order_by(Reserva.fecha_reserva.desc())
        .all()
    )


def get_all_reservations(db: Session) -> list[Reserva]:
    return (
        db.query(Reserva)
        .order_by(Reserva.fecha_reserva.desc())
        .all()
    )


def get_reservation_by_id(db: Session, reservation_id: int) -> Optional[Reserva]:
    return (
        db.query(Reserva)
        .filter(Reserva.id_reserva == reservation_id)
        .first()
    )
