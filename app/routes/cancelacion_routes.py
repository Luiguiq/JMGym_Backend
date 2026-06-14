from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.admin_model import Administrador
from app.schemas.cancelacion_schemas import CancelacionAdminResponseSchema
from app.security import get_db, get_current_admin

router = APIRouter(prefix="/cancelaciones", tags=["Cancelaciones"])


@router.get("", response_model=list[CancelacionAdminResponseSchema])
def list_all_cancelaciones(
    db: Session = Depends(get_db),
    _admin: Administrador = Depends(get_current_admin),
):
    rows = db.execute(
        text("""
            SELECT
                c.id_cancelacion,
                c.id_reserva,
                c.motivo,
                c.detalle,
                c.cancelado_por,
                c.fecha_cancelacion,
                r.codigo_reserva,
                u.nombre_completo AS nombre_usuario,
                cl.nombre_clase,
                r.fecha_clase
            FROM cancelaciones c
            JOIN reservas r  ON c.id_reserva = r.id_reserva
            JOIN usuarios u  ON r.id_usuario  = u.id_usuario
            JOIN clases cl   ON r.id_clase    = cl.id_clase
            ORDER BY c.fecha_cancelacion DESC
        """)
    ).fetchall()

    return [
        CancelacionAdminResponseSchema(
            id_cancelacion=row.id_cancelacion,
            id_reserva=row.id_reserva,
            motivo=row.motivo,
            detalle=row.detalle,
            cancelado_por=row.cancelado_por,
            fecha_cancelacion=row.fecha_cancelacion,
            codigo_reserva=row.codigo_reserva,
            nombre_usuario=row.nombre_usuario,
            nombre_clase=row.nombre_clase,
            fecha_clase=row.fecha_clase,
        )
        for row in rows
    ]
