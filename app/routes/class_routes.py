from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.class_schemas import ClassCreateSchema, ClassUpdateSchema, ClassResponseSchema, SeatResponseSchema
from app.security import get_db, get_current_admin
from app.models.admin_model import Administrador
from app.services.class_service import (
    get_classes_service,
    get_today_classes_service,
    get_class_detail_service,
    get_classes_by_instructor_service,
    create_class_service,
    update_class_service,
    delete_class_service,
    get_class_seats_service,
)

router = APIRouter(prefix="/classes", tags=["Classes"])


@router.get("/today", response_model=list[ClassResponseSchema])
def list_today_classes(db: Session = Depends(get_db)):
    return get_today_classes_service(db)


@router.get("", response_model=list[ClassResponseSchema])
def list_classes(db: Session = Depends(get_db)):
    return get_classes_service(db)


@router.get("/instructor/{instructor_id}", response_model=list[ClassResponseSchema])
def list_classes_by_instructor(instructor_id: int, db: Session = Depends(get_db)):
    return get_classes_by_instructor_service(db, instructor_id)


@router.get("/{class_id}", response_model=ClassResponseSchema)
def class_detail(class_id: int, db: Session = Depends(get_db)):
    return get_class_detail_service(db, class_id)


@router.post("", response_model=ClassResponseSchema, status_code=201)
def create_class(data: ClassCreateSchema, db: Session = Depends(get_db)):
    return create_class_service(db, data)


@router.put("/{class_id}", response_model=ClassResponseSchema)
def update_class(class_id: int, data: ClassUpdateSchema, db: Session = Depends(get_db)):
    return update_class_service(db, class_id, data)


@router.delete("/{class_id}")
def delete_class(class_id: int, db: Session = Depends(get_db), _admin: Administrador = Depends(get_current_admin)):
    return delete_class_service(db, class_id)


@router.get("/{class_id}/seats", response_model=list[SeatResponseSchema])
def get_class_seats_endpoint(class_id: int, db: Session = Depends(get_db)):
    return get_class_seats_service(db, class_id)
