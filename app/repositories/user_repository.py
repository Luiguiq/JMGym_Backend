from typing import Optional

from sqlalchemy.orm import Session

from app.models.user_model import Usuario


def get_user_by_email(db: Session, email: str) -> Optional[Usuario]:
    return (
        db.query(Usuario)
        .filter(Usuario.correo == email)
        .first()
    )


def get_user_by_dni(db: Session, dni: str) -> Optional[Usuario]:
    return (
        db.query(Usuario)
        .filter(Usuario.dni == dni)
        .first()
    )


def get_user_by_id(db: Session, user_id: int) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.id_usuario == user_id).first()


def create_user(db: Session, user_data: dict) -> Usuario:
    user = Usuario(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
