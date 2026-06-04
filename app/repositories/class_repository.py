from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.models.class_model import Clase
from app.models.seat_model import Espacio
from app.enum.class_enums import EstadoClase


def get_class_by_id(db: Session, class_id: int) -> Optional[Clase]:
    return db.query(Clase).filter(Clase.id_clase == class_id).first()


def get_active_classes(db: Session) -> list[Clase]:
    return (
        db.query(Clase)
        .filter(
            (Clase.estado == EstadoClase.ACTIVA) | (Clase.estado.is_(None))
        )
        .all()
    )


def get_today_classes(db: Session) -> list[Clase]:
    today = date.today()
    return (
        db.query(Clase)
        .filter(Clase.fecha == today)
        .filter(
            (Clase.estado == EstadoClase.ACTIVA) | (Clase.estado.is_(None))
        )
        .all()
    )


def _generate_seat_codes(total: int) -> list[str]:
    cols = 5
    codes = []
    for i in range(total):
        row = i // cols
        col = i % cols
        letter = chr(65 + row)
        codes.append(f"{letter}{col + 1}")
    return codes


def create_class(db: Session, class_data: dict) -> Clase:
    cls = Clase(**class_data)
    db.add(cls)
    db.commit()
    db.refresh(cls)

    total = cls.cupos_totales or 0
    if total > 0:
        codes = _generate_seat_codes(total)
        seats = [Espacio(id_clase=cls.id_clase, codigo_espacio=c) for c in codes]
        db.add_all(seats)
        db.commit()

    return cls


def update_class(db: Session, class_id: int, class_data: dict) -> Optional[Clase]:
    cls = get_class_by_id(db, class_id)
    if not cls:
        return None
    for key, value in class_data.items():
        setattr(cls, key, value)
    db.commit()
    db.refresh(cls)
    return cls


def delete_class(db: Session, class_id: int) -> bool:
    cls = get_class_by_id(db, class_id)
    if not cls:
        return False
    db.delete(cls)
    db.commit()
    return True


def get_classes_by_instructor(db: Session, instructor_id: int) -> list[Clase]:
    return (
        db.query(Clase)
        .filter(Clase.id_instructor == instructor_id)
        .filter(
            (Clase.estado == EstadoClase.ACTIVA) | (Clase.estado.is_(None))
        )
        .order_by(Clase.fecha.desc(), Clase.hora_inicio)
        .all()
    )


def get_class_seats(db: Session, class_id: int) -> list[Espacio]:
    return db.query(Espacio).filter(Espacio.id_clase == class_id).all()
