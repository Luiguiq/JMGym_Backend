from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.models.class_model import Clase
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


def create_class(db: Session, class_data: dict) -> Clase:
    cls = Clase(**class_data)
    db.add(cls)
    db.commit()
    db.refresh(cls)
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
