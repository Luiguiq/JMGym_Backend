from sqlalchemy.orm import Session

from app.models.user_model import Usuario


def get_all_users(db: Session):
    return db.query(Usuario).all()


def get_user_by_id(db: Session, user_id: int):
    return db.query(Usuario).filter(
        Usuario.id == user_id
    ).first()


def get_user_by_email(db: Session, email: str):
    return db.query(Usuario).filter(
        Usuario.correo == email
    ).first()


def create_user(db: Session, user_data: dict):
    new_user = Usuario(**user_data)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user