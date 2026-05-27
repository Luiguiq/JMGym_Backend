from sqlalchemy.orm import Session

from app.models.reservation_model import Reserva


def get_all_reservations(db: Session):
    return db.query(Reserva).all()


def get_reservation_by_id(
    db: Session,
    reservation_id: int
):
    return db.query(Reserva).filter(
        Reserva.id == reservation_id
    ).first()


def get_reservations_by_user(
    db: Session,
    user_id: int
):
    return db.query(Reserva).filter(
        Reserva.usuario_id == user_id
    ).all()


def create_reservation(
    db: Session,
    reservation_data: dict
):
    new_reservation = Reserva(**reservation_data)

    db.add(new_reservation)
    db.commit()
    db.refresh(new_reservation)

    return new_reservation