"""
Script de prueba para los 3 niveles de fidelizacion:
- Bronce: 0-7h   (3h)
- Plata:  8-20h  (12h)
- Oro:    21h+   (24h)

Idempotente - se puede ejecutar multiples veces sin duplicar datos.

Ejecutar: python insertar_test_fidelizacion.py
"""

import uuid
from datetime import date, time

from app.core.database import SessionLocal
from app.models.user_model import Usuario
from app.models.class_model import Clase
from app.models.seat_model import Espacio
from app.models.reservation_model import Reserva
from app.models.genre_model import GeneroClase
from app.models.instructor_model import Instructor
from app.enum.class_enums import IntensidadClase
from app.enum.reservation_enums import MetodoPago, EstadoPagoReserva, EstadoReserva

PWD_HASH = "$pbkdf2-sha256$29000$F.Icw/j//x9jrBXiHAPgnA$D2Cp6BEAF7W/Tcg2ESx6uoI/mfXXcXLQHLQWPnH.Kqk"  # test123

db = SessionLocal()

# ─── 1. Referencias existentes ───────────────────────────────────
genero = db.query(GeneroClase).first()
instructor = db.query(Instructor).first()
if not genero or not instructor:
    print("ERROR: No hay generos ni instructores en la BD. Ejecuta seed.py primero.")
    db.close()
    exit(1)

# ─── 2. Usuarios de prueba ───────────────────────────────────────
usuarios_data = [
    ("Test Bronce", "11111111", "bronce@test.com"),
    ("Test Plata",  "22222222", "plata@test.com"),
    ("Test Oro",    "33333333", "oro@test.com"),
]

usuarios = []
for nombre, dni, correo in usuarios_data:
    existente = db.query(Usuario).filter(
        (Usuario.dni == dni) | (Usuario.correo == correo)
    ).first()
    if existente:
        usuarios.append(existente)
        print(f"  -> {nombre} ya existe (id={existente.id_usuario})")
        continue
    u = Usuario(
        nombre_completo=nombre,
        dni=dni,
        correo=correo,
        password_hash=PWD_HASH,
    )
    db.add(u)
    db.commit()
    usuarios.append(u)
    print(f"  -> {nombre} creado (id={u.id_usuario})")
print(f"OK {len(usuarios)} usuarios listos")

# ─── 3. Clases (30 dias de julio, 60 min c/u) ────────────────────
clases = db.query(Clase).filter(
    Clase.nombre_clase.like("Test Fidelizacion%")
).order_by(Clase.fecha).all()

if not clases:
    clases = []
    for dia in range(1, 31):
        c = Clase(
            nombre_clase=f"Test Fidelizacion Dia {dia}",
            id_genero=genero.id_genero,
            id_instructor=instructor.id_instructor,
            intensidad=IntensidadClase.MEDIA,
            duracion_minutos=60,
            fecha=date(2026, 7, dia),
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0),
            precio=20.00,
            cupos_totales=30,
            cupos_disponibles=30,
        )
        db.add(c)
        clases.append(c)
    db.commit()
    print(f"OK {len(clases)} clases creadas (1-30 julio)")
else:
    print(f"OK {len(clases)} clases ya existentes")

# ─── 4. Espacios (5 por clase) ──────────────────────────────────
clases_con_espacios = {}
for c in clases:
    espacios = db.query(Espacio).filter(Espacio.id_clase == c.id_clase).all()
    if not espacios:
        espacios = []
        for letra in ["A", "B", "C", "D", "E"]:
            e = Espacio(id_clase=c.id_clase, codigo_espacio=letra)
            db.add(e)
            espacios.append(e)
        db.commit()
    clases_con_espacios[c.id_clase] = espacios
print("OK Espacios listos (5 por clase)")

# ─── 5. Reservas ──────────────────────────────────────────────────
def crear_reservas(usuario, num_reservas, dias_offset):
    creadas = 0
    for i in range(num_reservas):
        idx = (dias_offset + i) % len(clases)
        c = clases[idx]
        espacio = clases_con_espacios[c.id_clase][i % 5]

        existe = db.query(Reserva).filter(
            Reserva.id_usuario == usuario.id_usuario,
            Reserva.fecha_clase == c.fecha,
            Reserva.estado_reserva == EstadoReserva.ACTIVA,
        ).first()
        if existe:
            continue

        r = Reserva(
            codigo_reserva=uuid.uuid4().hex[:10].upper(),
            id_usuario=usuario.id_usuario,
            id_clase=c.id_clase,
            id_espacio=espacio.id_espacio,
            metodo_pago=MetodoPago.YAPE,
            monto=c.precio,
            fecha_clase=c.fecha,
            estado_pago=EstadoPagoReserva.PAGADO,
            estado_reserva=EstadoReserva.ACTIVA,
        )
        db.add(r)
        creadas += 1
    if creadas:
        db.commit()
    return creadas

creadas_bronce = crear_reservas(usuarios[0], 3, 0)
creadas_plata  = crear_reservas(usuarios[1], 12, 0)
creadas_oro    = crear_reservas(usuarios[2], 24, 0)

print(f"OK Reservas:")
print(f"  - Bronce: {creadas_bronce} creadas (target 3h)")
print(f"  - Plata:  {creadas_plata} creadas (target 12h)")
print(f"  - Oro:    {creadas_oro} creadas (target 24h)")
print()
print("Resumen:")
print("  bronce@test.com / test123 -> Nivel BRONCE (0% dto)")
print("  plata@test.com  / test123 -> Nivel PLATA  (10% dto)")
print("  oro@test.com    / test123 -> Nivel ORO    (20% dto)")

db.close()
