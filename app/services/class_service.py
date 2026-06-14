from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.enum.class_enums import EstadoClase
from app.repositories.class_repository import (
    get_active_classes,
    get_today_classes,
    get_class_by_id,
    get_classes_by_instructor,
    create_class,
    update_class,
    delete_class,
    get_class_seats,
)
from app.schemas.class_schemas import (
    ClassCreateSchema,
    ClassUpdateSchema,
    ClassResponseSchema,
    SeatResponseSchema,
)
from app.services.notification_service import (
    notify_class_schedule_change,
    notify_class_instructor_change,
    notify_class_cancelled,
)


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
    cls = get_class_by_id(db, class_id)
    if not cls:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clase no encontrada",
        )

    old_horario = f"{cls.hora_inicio.strftime('%H:%M')} - {cls.hora_fin.strftime('%H:%M')}" if cls.hora_inicio else ""
    old_instructor = cls.instructor.nombre_completo if cls.instructor else ""
    old_estado = cls.estado

    cls = update_class(db, class_id, data.model_dump(exclude_unset=True))

    new_horario = f"{cls.hora_inicio.strftime('%H:%M')} - {cls.hora_fin.strftime('%H:%M')}" if cls.hora_inicio else ""
    new_instructor = cls.instructor.nombre_completo if cls.instructor else ""

    if old_horario and old_horario != new_horario:
        notify_class_schedule_change(db, cls, old_horario, new_horario)

    if old_instructor and old_instructor != new_instructor:
        notify_class_instructor_change(db, cls, old_instructor, new_instructor)

    if old_estado != EstadoClase.CANCELADA and cls.estado == EstadoClase.CANCELADA:
        motivo = data.motivo_cancelacion or ""
        notify_class_cancelled(db, cls, motivo)

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


def get_classes_by_instructor_service(db: Session, instructor_id: int) -> list[ClassResponseSchema]:
    classes = get_classes_by_instructor(db, instructor_id)
    result = []
    for c in classes:
        schema = ClassResponseSchema.model_validate(c)
        _populate_instructor_name(c, schema)
        result.append(schema)
    return result


def get_class_seats_service(db: Session, class_id: int) -> list[SeatResponseSchema]:
    from app.models.reservation_model import Reserva
    seats = get_class_seats(db, class_id)
    active_seat_ids = set(
        r.id_espacio for r in db.query(Reserva.id_espacio).filter(
            Reserva.id_clase == class_id,
            Reserva.estado_reserva == "ACTIVA",
        ).all()
    )
    result = []
    for s in seats:
        if s.estado in ("RESERVADO", "OCUPADO") and s.id_espacio not in active_seat_ids:
            s.estado = "DISPONIBLE"
            db.commit()
        result.append(SeatResponseSchema.model_validate(s))
    return result
