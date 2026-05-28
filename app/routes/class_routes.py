from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.class_schemas import ClassCreateSchema, ClassUpdateSchema, ClassResponseSchema
from app.security import get_db
from app.services.class_service import (
    get_classes_service,
    get_today_classes_service,
    get_class_detail_service,
    create_class_service,
    update_class_service,
    delete_class_service,
)

router = APIRouter(prefix="/classes", tags=["Classes"])


@router.get("/today", response_model=list[ClassResponseSchema])
def list_today_classes(db: Session = Depends(get_db)):
    return get_today_classes_service(db)


@router.get("", response_model=list[ClassResponseSchema])
def list_classes(db: Session = Depends(get_db)):
    return get_classes_service(db)


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
def delete_class(class_id: int, db: Session = Depends(get_db)):
    return delete_class_service(db, class_id)
