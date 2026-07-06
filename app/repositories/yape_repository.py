from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.yape_model import YapePago


def create_yape_pago(db: Session, data: dict) -> YapePago:
    pago = YapePago(**data)
    db.add(pago)
    db.commit()
    db.refresh(pago)
    return pago


def get_yape_pago_by_id(db: Session, id_yape_pago: int) -> Optional[YapePago]:
    return (
        db.query(YapePago)
        .filter(YapePago.id_yape_pago == id_yape_pago)
        .first()
    )


def update_yape_pago(
    db: Session, id_yape_pago: int, updates: dict
) -> Optional[YapePago]:
    pago = get_yape_pago_by_id(db, id_yape_pago)
    if not pago:
        return None
    for key, value in updates.items():
        setattr(pago, key, value)
    db.commit()
    db.refresh(pago)
    return pago


def get_all_yape_pagos(db: Session) -> list[YapePago]:
    return (
        db.query(YapePago)
        .order_by(YapePago.fecha_creacion.desc())
        .all()
    )
