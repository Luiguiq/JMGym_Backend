from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.class_repository import (
    get_active_classes,
    get_today_classes,
    get_class_by_id,
    create_class,
    update_class,
    delete_class,
)
from app.schemas.class_schemas import ClassCreateSchema, ClassUpdateSchema, ClassResponseSchema


def _populate_instructor_name(cls_obj, schema: ClassResponseSchema) -> None:
    if cls_obj.instructor:
        schema.instructor_nombre = cls_obj.instructor.nombre_completo


def get_classes_service(db: Session) -> list[ClassResponseSchema]:
    classes = get_active_classes(db)
    result = []
    for c in classes:
        schema = ClassResponseSchema.model_validate(c)
        _populate_instructor_name(c, schema)
        result.append(schema)
    return result


def get_today_classes_service(db: Session) -> list[ClassResponseSchema]:
    classes = get_today_classes(db)
    result = []
    for c in classes:
        schema = ClassResponseSchema.model_validate(c)
        _populate_instructor_name(c, schema)
        result.append(schema)
    return result


def get_class_detail_service(db: Session, class_id: int) -> ClassResponseSchema:
    cls = get_class_by_id(db, class_id)
    if not cls:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clase no encontrada",
        )
    schema = ClassResponseSchema.model_validate(cls)
    _populate_instructor_name(cls, schema)
    return schema


def create_class_service(db: Session, data: ClassCreateSchema) -> ClassResponseSchema:
    cls = create_class(db, data.model_dump())
    schema = ClassResponseSchema.model_validate(cls)
    _populate_instructor_name(cls, schema)
    return schema


def update_class_service(
    db: Session, class_id: int, data: ClassUpdateSchema
) -> ClassResponseSchema:
    cls = update_class(db, class_id, data.model_dump(exclude_unset=True))
    if not cls:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clase no encontrada",
        )
    schema = ClassResponseSchema.model_validate(cls)
    _populate_instructor_name(cls, schema)
    return schema


def delete_class_service(db: Session, class_id: int) -> dict:
    deleted = delete_class(db, class_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clase no encontrada",
        )
    return {"message": "Clase eliminada correctamente"}
