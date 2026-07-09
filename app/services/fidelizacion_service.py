from datetime import date
from sqlalchemy.orm import Session

from app.models.reservation_model import Reserva
from app.enum.reservation_enums import EstadoReserva, EstadoPagoReserva

BRONCE_HORAS_MAX = 7
PLATA_HORAS_MIN = 8
PLATA_HORAS_MAX = 20
ORO_HORAS_MIN = 21

NIVEL_BRONCE = "BRONCE"
NIVEL_PLATA = "PLATA"
NIVEL_ORO = "ORO"


def calcular_horas_mes(db: Session, user_id: int) -> float:
    today = date.today()
    inicio_mes = today.replace(day=1)
    if today.month == 12:
        fin_mes = today.replace(year=today.year + 1, month=1, day=1)
    else:
        fin_mes = today.replace(month=today.month + 1, day=1)

    reservas = (
        db.query(Reserva)
        .filter(
            Reserva.id_usuario == user_id,
            Reserva.fecha_clase >= inicio_mes,
            Reserva.fecha_clase < fin_mes,
            Reserva.estado_reserva.in_([
                EstadoReserva.ACTIVA,
                EstadoReserva.FINALIZADA,
            ]),
            Reserva.estado_pago != EstadoPagoReserva.PENDIENTE,
        )
        .all()
    )

    total_horas = 0.0
    for r in reservas:
        if r.clase and r.clase.duracion_minutos:
            total_horas += r.clase.duracion_minutos / 60.0
        else:
            total_horas += 1.0

    return round(total_horas, 1)


def obtener_nivel(horas: float) -> str:
    if horas >= ORO_HORAS_MIN:
        return NIVEL_ORO
    if horas >= PLATA_HORAS_MIN:
        return NIVEL_PLATA
    return NIVEL_BRONCE


def obtener_descuento(horas: float) -> int:
    nivel = obtener_nivel(horas)
    if nivel == NIVEL_ORO:
        return 20
    if nivel == NIVEL_PLATA:
        return 10
    return 0


def obtener_acompanante_gratis(horas: float) -> bool:
    return obtener_nivel(horas) == NIVEL_ORO


def obtener_info_fidelizacion(db: Session, user_id: int) -> dict:
    horas = calcular_horas_mes(db, user_id)
    nivel = obtener_nivel(horas)
    descuento = obtener_descuento(horas)
    acompanante = obtener_acompanante_gratis(horas)
    siguiente_nivel = None
    horas_restantes = 0

    if nivel == NIVEL_BRONCE:
        siguiente_nivel = NIVEL_PLATA
        horas_restantes = PLATA_HORAS_MIN - horas
    elif nivel == NIVEL_PLATA:
        siguiente_nivel = NIVEL_ORO
        horas_restantes = ORO_HORAS_MIN - horas

    return {
        "horas_mes": horas,
        "nivel": nivel,
        "descuento_porcentaje": descuento,
        "acompanante_gratis": acompanante,
        "siguiente_nivel": siguiente_nivel,
        "horas_restantes": round(max(0, horas_restantes), 1) if siguiente_nivel else 0,
    }