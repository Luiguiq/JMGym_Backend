import uuid
import random
import string
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.user_model import Usuario
from app.models.yape_model import YapePago
from app.schemas.yape_schemas import (
    YapeInitiateRequest,
    YapeInitiateResponse,
    YapeConfirmRequest,
    YapeConfirmResponse,
    YapePagoResponse,
)
from app.security import get_db, get_current_user, get_current_admin
from app.repositories.yape_repository import (
    create_yape_pago,
    get_yape_pago_by_id,
    update_yape_pago,
    get_all_yape_pagos,
)
from app.services.notification_service import notify_payment_confirmed
from app.enum.reservation_enums import EstadoPagoReserva, MetodoPago, EstadoReserva
from app.models.class_model import Clase

router = APIRouter(prefix="/payments/yape", tags=["Yape"])


@router.post("/initiate", response_model=YapeInitiateResponse, status_code=201)
def initiate_yape_payment(
    data: YapeInitiateRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    yape_pago = create_yape_pago(db, {
        "id_usuario": current_user.id_usuario,
        "id_clase": data.id_clase,
        "id_espacio": data.id_espacio,
        "celular": data.celular,
        "estado": "PENDIENTE",
        "monto": data.monto,
        "fecha_creacion": datetime.now(),
    })
    return YapeInitiateResponse(
        id_yape_pago=yape_pago.id_yape_pago,
        estado="PENDIENTE",
    )


@router.post("/confirm", response_model=YapeConfirmResponse)
def confirm_yape_payment(
    data: YapeConfirmRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    yape_pago = get_yape_pago_by_id(db, data.id_yape_pago)
    if not yape_pago:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pago Yape no encontrado",
        )

    if yape_pago.estado != "PENDIENTE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este pago Yape ya fue procesado",
        )

    if yape_pago.id_usuario != current_user.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Este pago no te pertenece",
        )

    # Mock: code "000000" always fails
    if data.codigo == "000000":
        update_yape_pago(db, data.id_yape_pago, {
            "estado": "RECHAZADO",
            "codigo_confirmacion": data.codigo,
            "fecha_confirmacion": datetime.now(),
        })
        return YapeConfirmResponse(
            estado="RECHAZADO",
            mensaje="El código ingresado no es válido. Intenta nuevamente.",
        )

    # Success — create reservation
    clase = db.query(Clase).filter(Clase.id_clase == yape_pago.id_clase).first()
    if not clase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clase no encontrada",
        )

    codigo_reserva = uuid.uuid4().hex[:10].upper()
    codigo_operacion = "YAPE-" + "".join(
        random.choices(string.ascii_uppercase + string.digits, k=10)
    )

    from app.models.reservation_model import Reserva
    reserva = Reserva(
        codigo_reserva=codigo_reserva,
        id_usuario=current_user.id_usuario,
        id_clase=yape_pago.id_clase,
        id_espacio=yape_pago.id_espacio,
        metodo_pago=MetodoPago.YAPE,
        estado_pago=EstadoPagoReserva.PAGADO,
        estado_reserva=EstadoReserva.ACTIVA,
        monto=yape_pago.monto,
        fecha_clase=clase.fecha,
    )
    db.add(reserva)
    db.flush()

    from app.models.payment_model import Pago
    from app.enum.payment_enums import EstadoPago as EstadoPagoEnum, MetodoPago as MetodoPagoEnum
    pago = Pago(
        id_reserva=reserva.id_reserva,
        metodo_pago=MetodoPagoEnum.YAPE,
        estado=EstadoPagoEnum.CONFIRMADO,
        monto=yape_pago.monto,
        codigo_operacion=codigo_operacion,
        fecha_pago=datetime.now(),
    )
    db.add(pago)

    yape_pago.id_reserva = reserva.id_reserva
    yape_pago.estado = "APROBADO"
    yape_pago.codigo_confirmacion = data.codigo
    yape_pago.fecha_confirmacion = datetime.now()

    db.commit()

    try:
        notify_payment_confirmed(db, current_user.id_usuario, reserva)
    except Exception:
        pass

    return YapeConfirmResponse(
        estado="APROBADO",
        mensaje="Pago Yape confirmado exitosamente.",
        id_reserva=reserva.id_reserva,
    )


@router.get("/admin", response_model=list[YapePagoResponse])
def list_yape_pagos(
    db: Session = Depends(get_db),
    _admin= Depends(get_current_admin),
):
    pagos = get_all_yape_pagos(db)
    result = []
    for p in pagos:
        result.append(YapePagoResponse(
            id_yape_pago=p.id_yape_pago,
            id_usuario=p.id_usuario,
            id_reserva=p.id_reserva,
            celular=p.celular,
            estado=p.estado,
            monto=p.monto,
            fecha_creacion=p.fecha_creacion,
            fecha_confirmacion=p.fecha_confirmacion,
            usuario_nombre=p.usuario.nombre_completo if p.usuario else None,
            usuario_correo=p.usuario.correo if p.usuario else None,
        ))
    return result
