from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.security import get_db
from app.models.class_model import Clase
from app.models.reservation_model import Reserva
from app.models.user_model import Usuario

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats")
def admin_stats(db: Session = Depends(get_db)):
    total_classes = db.query(Clase).count()
    total_reservations = db.query(Reserva).count()
    total_clients = db.query(Usuario).count()
    return {
        "totalClasses": total_classes,
        "totalReservations": total_reservations,
        "totalClients": total_clients,
    }
