"""
Seed natural para probar nivel Oro sin clases con nombres de test.

Idempotente: se puede ejecutar varias veces sin duplicar usuario, clases,
espacios ni reservas del usuario de prueba.

Ejecutar: python insertar_oro_natural.py
"""

import shutil
import uuid
from datetime import date, time
from pathlib import Path

from app.core.database import SessionLocal
from app.security import hash_password
from app.models.user_model import Usuario
from app.models.class_model import Clase
from app.models.seat_model import Espacio
from app.models.reservation_model import Reserva
from app.models.genre_model import GeneroClase
from app.models.instructor_model import Instructor
from app.enum.class_enums import IntensidadClase, EstadoClase
from app.enum.espacio_enums import EstadoEspacio
from app.enum.reservation_enums import MetodoPago, EstadoPagoReserva, EstadoReserva


USER_EMAIL = "oro2@test.com"
USER_DNI = "44444444"
USER_PASSWORD = "test123"
CAPACIDAD = 20


def copiar_imagenes() -> dict[str, str]:
    root = Path(__file__).resolve().parent
    front_images = root.parent / "JMGym_Front" / "src" / "assets" / "images"
    upload_dir = root / "app" / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    fuentes = {
        "zumba": front_images / "zumba.jpg",
        "cardio": front_images / "cardio.jpg",
        "fuerza": front_images / "trensuperior.jpg",
    }
    urls = {}
    for key, src in fuentes.items():
        if not src.exists():
            urls[key] = ""
            continue
        dest = upload_dir / f"seed-{key}{src.suffix.lower()}"
        if not dest.exists():
            shutil.copyfile(src, dest)
        urls[key] = f"/uploads/{dest.name}"
    return urls


def get_genero(db, nombre: str) -> GeneroClase:
    genero = db.query(GeneroClase).filter(GeneroClase.nombre_genero == nombre).first()
    if genero:
        return genero
    return db.query(GeneroClase).first()


def get_instructor(db, index: int) -> Instructor:
    instructores = db.query(Instructor).order_by(Instructor.id_instructor).all()
    if not instructores:
        raise RuntimeError("No hay instructores. Ejecuta seed.py primero.")
    return instructores[index % len(instructores)]


def generar_codigo_espacio(index: int) -> str:
    fila = chr(65 + index // 5)
    col = (index % 5) + 1
    return f"{fila}{col}"


def asegurar_espacios(db, clase: Clase) -> list[Espacio]:
    existentes = {
        e.codigo_espacio: e
        for e in db.query(Espacio).filter(Espacio.id_clase == clase.id_clase).all()
    }
    for i in range(CAPACIDAD):
        codigo = generar_codigo_espacio(i)
        if codigo not in existentes:
            espacio = Espacio(
                id_clase=clase.id_clase,
                codigo_espacio=codigo,
                estado=EstadoEspacio.DISPONIBLE,
            )
            db.add(espacio)
            existentes[codigo] = espacio
    db.commit()
    return db.query(Espacio).filter(Espacio.id_clase == clase.id_clase).order_by(Espacio.codigo_espacio).all()


def main():
    db = SessionLocal()
    try:
        imagenes = copiar_imagenes()
        genero_zumba = get_genero(db, "Zumba") or get_genero(db, "Baile")
        genero_cardio = get_genero(db, "Cardio")
        genero_fuerza = get_genero(db, "Fuerza")

        user = db.query(Usuario).filter(Usuario.correo == USER_EMAIL).first()
        if not user:
            user = Usuario(
                nombre_completo="Test Oro Natural",
                dni=USER_DNI,
                correo=USER_EMAIL,
                password_hash=hash_password(USER_PASSWORD),
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"OK Usuario creado: {USER_EMAIL} (id={user.id_usuario})")
        else:
            print(f"OK Usuario existente: {USER_EMAIL} (id={user.id_usuario})")

        clases_data = [
            ("Zumba Power", genero_zumba, imagenes["zumba"], IntensidadClase.ALTA),
            ("Cardio Full Body", genero_cardio, imagenes["cardio"], IntensidadClase.ALTA),
            ("Ritmo Zumba", genero_zumba, imagenes["zumba"], IntensidadClase.MEDIA),
            ("Cardio Quemagrasa", genero_cardio, imagenes["cardio"], IntensidadClase.ALTA),
            ("Baile Fit Latino", genero_zumba, imagenes["zumba"], IntensidadClase.MEDIA),
            ("Fuerza Funcional", genero_fuerza, imagenes["fuerza"], IntensidadClase.MEDIA),
            ("Zumba Explosiva", genero_zumba, imagenes["zumba"], IntensidadClase.ALTA),
            ("Cardio HIIT", genero_cardio, imagenes["cardio"], IntensidadClase.ALTA),
            ("Dance Cardio", genero_cardio, imagenes["cardio"], IntensidadClase.MEDIA),
            ("Zumba Tonificacion", genero_zumba, imagenes["zumba"], IntensidadClase.MEDIA),
            ("Cardio Resistencia", genero_cardio, imagenes["cardio"], IntensidadClase.ALTA),
            ("Tren Superior Express", genero_fuerza, imagenes["fuerza"], IntensidadClase.MEDIA),
            ("Zumba Party", genero_zumba, imagenes["zumba"], IntensidadClase.MEDIA),
            ("Cardio Core", genero_cardio, imagenes["cardio"], IntensidadClase.MEDIA),
            ("Baile Urbano Fit", genero_zumba, imagenes["zumba"], IntensidadClase.MEDIA),
            ("Cardio Power", genero_cardio, imagenes["cardio"], IntensidadClase.ALTA),
            ("Fuerza Total", genero_fuerza, imagenes["fuerza"], IntensidadClase.ALTA),
            ("Zumba Latina", genero_zumba, imagenes["zumba"], IntensidadClase.MEDIA),
            ("Cardio Metabolico", genero_cardio, imagenes["cardio"], IntensidadClase.ALTA),
            ("Baile y Energia", genero_zumba, imagenes["zumba"], IntensidadClase.MEDIA),
            ("Cardio Box", genero_cardio, imagenes["cardio"], IntensidadClase.ALTA),
            ("Zumba Gold", genero_zumba, imagenes["zumba"], IntensidadClase.BAJA),
            ("Functional Cardio", genero_cardio, imagenes["cardio"], IntensidadClase.MEDIA),
            ("Zumba Night", genero_zumba, imagenes["zumba"], IntensidadClase.MEDIA),
        ]

        creadas = 0
        reservas_creadas = 0
        for idx, (nombre, genero, imagen, intensidad) in enumerate(clases_data, start=1):
            fecha = date(2026, 7, idx)
            clase = db.query(Clase).filter(
                Clase.nombre_clase == nombre,
                Clase.fecha == fecha,
            ).first()
            if not clase:
                instructor = get_instructor(db, idx)
                clase = Clase(
                    nombre_clase=nombre,
                    id_genero=genero.id_genero,
                    id_instructor=instructor.id_instructor,
                    descripcion=f"Clase de {nombre.lower()} para mejorar resistencia, energia y coordinacion.",
                    intensidad=intensidad,
                    reglas_vestimenta="Ropa deportiva comoda, zapatillas y botella de agua.",
                    duracion_minutos=60,
                    fecha=fecha,
                    hora_inicio=time(10 + (idx % 8), 0),
                    hora_fin=time(11 + (idx % 8), 0),
                    precio=22.00 if genero.nombre_genero == "Cardio" else 20.00,
                    cupos_totales=CAPACIDAD,
                    cupos_disponibles=CAPACIDAD,
                    alumnos_minimos=5,
                    imagen_clase=imagen,
                    estado=EstadoClase.ACTIVA,
                )
                db.add(clase)
                db.commit()
                db.refresh(clase)
                creadas += 1

            espacios = asegurar_espacios(db, clase)
            reserva = db.query(Reserva).filter(
                Reserva.id_usuario == user.id_usuario,
                Reserva.id_clase == clase.id_clase,
                Reserva.estado_reserva == EstadoReserva.ACTIVA,
            ).first()
            if reserva:
                continue

            espacio = next(
                (e for e in espacios if e.estado == EstadoEspacio.DISPONIBLE),
                espacios[0],
            )
            reserva = Reserva(
                codigo_reserva=uuid.uuid4().hex[:10].upper(),
                qr_checkin=f"CHECKIN:{uuid.uuid4().hex[:10].upper()}",
                id_usuario=user.id_usuario,
                id_clase=clase.id_clase,
                id_espacio=espacio.id_espacio,
                metodo_pago=MetodoPago.YAPE,
                estado_pago=EstadoPagoReserva.PAGADO,
                estado_reserva=EstadoReserva.ACTIVA,
                monto=clase.precio,
                fecha_clase=clase.fecha,
                es_clase_gratis=False,
            )
            db.add(reserva)
            espacio.estado = EstadoEspacio.RESERVADO
            clase.cupos_disponibles = max(0, (clase.cupos_disponibles or CAPACIDAD) - 1)
            reservas_creadas += 1
            db.commit()

        print(f"OK Clases naturales creadas: {creadas}")
        print(f"OK Reservas nuevas para {USER_EMAIL}: {reservas_creadas}")
        print(f"Credenciales: {USER_EMAIL} / {USER_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
