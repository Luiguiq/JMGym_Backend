from datetime import date
from sqlalchemy.orm import Session

from app.models.reservation_model import Reserva
from app.enum.reservation_enums import EstadoReserva, EstadoPagoReserva

BRONCE_HORAS_MAX = 7
PLATA_HORAS_MIN = 8
PLATA_HORAS_MAX = 20
ORO_HORAS_MIN = 21
BONO_HORAS_TOPE = 30
CLASES_GRATIS_POR_MES = 2

NIVEL_BRONCE = "BRONCE"
NIVEL_PLATA = "PLATA"
NIVEL_ORO = "ORO"


def _calcular_horas_periodo(db: Session, user_id: int, mes: int, anio: int) -> float:
    inicio_mes = date(anio, mes, 1)
    if mes == 12:
        fin_mes = date(anio + 1, 1, 1)
    else:
        fin_mes = date(anio, mes + 1, 1)

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


def calcular_horas_mes(db: Session, user_id: int) -> dict:
    today = date.today()
    horas_base = _calcular_horas_periodo(db, user_id, today.month, today.year)

    if today.month == 1:
        prev_mes, prev_anio = 12, today.year - 1
    else:
        prev_mes, prev_anio = today.month - 1, today.year

    horas_previas = _calcular_horas_periodo(db, user_id, prev_mes, prev_anio)
    horas_bono = max(0, horas_previas - BONO_HORAS_TOPE)

    return {
        "horas_base": horas_base,
        "horas_bono": horas_bono,
        "total": round(horas_base + horas_bono, 1),
    }


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


def obtener_clases_gratis_restantes(db: Session, user_id: int) -> int:
    today = date.today()
    inicio_mes = date(today.year, today.month, 1)
    if today.month == 12:
        fin_mes = date(today.year + 1, 1, 1)
    else:
        fin_mes = date(today.year, today.month + 1, 1)

    usadas = (
        db.query(Reserva)
        .filter(
            Reserva.id_usuario == user_id,
            Reserva.fecha_clase >= inicio_mes,
            Reserva.fecha_clase < fin_mes,
            Reserva.es_clase_gratis == True,
        )
        .count()
    )
    return max(0, CLASES_GRATIS_POR_MES - usadas)


def obtener_info_fidelizacion(db: Session, user_id: int) -> dict:
    data = calcular_horas_mes(db, user_id)
    nivel = obtener_nivel(data["total"])
    descuento = obtener_descuento(data["total"])
    siguiente_nivel = None
    horas_restantes = 0

    if nivel == NIVEL_BRONCE:
        siguiente_nivel = NIVEL_PLATA
        horas_restantes = PLATA_HORAS_MIN - data["total"]
    elif nivel == NIVEL_PLATA:
        siguiente_nivel = NIVEL_ORO
        horas_restantes = ORO_HORAS_MIN - data["total"]

    return {
        "horas_mes": data["total"],
        "horas_base": data["horas_base"],
        "horas_bono": data["horas_bono"],
        "nivel": nivel,
        "descuento_porcentaje": descuento,
        "acompanante_gratis": nivel == NIVEL_ORO,
        "clases_gratis_restantes": obtener_clases_gratis_restantes(db, user_id) if nivel == NIVEL_ORO else 0,
        "siguiente_nivel": siguiente_nivel,
        "horas_restantes": round(max(0, horas_restantes), 1) if siguiente_nivel else 0,
    }
