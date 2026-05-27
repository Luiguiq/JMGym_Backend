from sqlalchemy.orm import Session

from app.models.class_model import Clase


def get_all_classes(db: Session):
    return db.query(Clase).all()


def get_class_by_id(db: Session, class_id: int):
    return db.query(Clase).filter(
        Clase.id == class_id
    ).first()


def create_class(db: Session, class_data: dict):
    new_class = Clase(**class_data)

    db.add(new_class)
    db.commit()
    db.refresh(new_class)

    return new_class