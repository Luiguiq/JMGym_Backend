from datetime import date, time
import uuid

from app.core.database import SessionLocal
from app.models.admin_model import Administrador
from app.models.genre_model import GeneroClase
from app.models.instructor_model import Instructor
from app.models.user_model import Usuario
from app.models.class_model import Clase
from app.models.seat_model import Espacio
from app.models.reservation_model import Reserva
from app.security import hash_password
from app.enum.class_enums import IntensidadClase
from app.enum.reservation_enums import MetodoPago, EstadoPagoReserva, EstadoReserva

db = SessionLocal()

# Géneros de clase
generos = [
    GeneroClase(nombre_genero="Salsa"),
    GeneroClase(nombre_genero="Zumba"),
    GeneroClase(nombre_genero="Merengue"),
]
db.add_all(generos)
db.commit()

# Instructores
instructores = [
    Instructor(nombre_completo="Carla Mendoza", especialidad="Salsa"),
    Instructor(nombre_completo="Andrea Ruiz", especialidad="Zumba"),
    Instructor(nombre_completo="Luis Flores", especialidad="Merengue"),
]
db.add_all(instructores)
db.commit()

# Usuarios
usuarios = [
    Usuario(
        nombre_completo="Erick Alegre",
        correo="erick@gmail.com",
        dni="12345678",
        password_hash=hash_password("123456"),
    ),
    Usuario(
        nombre_completo="Maria Torres",
        correo="maria@gmail.com",
        dni="23456789",
        password_hash=hash_password("123456"),
    ),
    Usuario(
        nombre_completo="Carlos Vega",
        correo="carlos@gmail.com",
        dni="34567890",
        password_hash=hash_password("123456"),
    ),
    Usuario(
        nombre_completo="Lucia Ramos",
        correo="lucia@gmail.com",
        dni="45678901",
        password_hash=hash_password("123456"),
    ),
]
db.add_all(usuarios)
db.commit()

# Admin
admin = Administrador(
    nombre="Admin JMGym",
    correo_institucional="admin@jmgym.com",
    password_hash=hash_password("admin123"),
)
db.add(admin)
db.commit()

# Clases
clases = [
    Clase(
        nombre_clase="Salsa Básica",
        id_genero=generos[0].id_genero,
        id_instructor=instructores[0].id_instructor,
        intensidad=IntensidadClase.BAJA,
        duracion_minutos=60,
        fecha=date.today(),
        hora_inicio=time(19, 0),
        hora_fin=time(20, 0),
        precio=15.00,
        cupos_totales=20,
        cupos_disponibles=20,
    ),
    Clase(
        nombre_clase="Zumba Fitness",
        id_genero=generos[1].id_genero,
        id_instructor=instructores[1].id_instructor,
        intensidad=IntensidadClase.ALTA,
        duracion_minutos=45,
        fecha=date.today(),
        hora_inicio=time(18, 0),
        hora_fin=time(18, 45),
        precio=12.00,
        cupos_totales=25,
        cupos_disponibles=25,
    ),
    Clase(
        nombre_clase="Merengue Intermedio",
        id_genero=generos[2].id_genero,
        id_instructor=instructores[2].id_instructor,
        intensidad=IntensidadClase.MEDIA,
        duracion_minutos=60,
        fecha=date.today(),
        hora_inicio=time(20, 0),
        hora_fin=time(21, 0),
        precio=18.00,
        cupos_totales=15,
        cupos_disponibles=15,
    ),
]
db.add_all(clases)
db.commit()

# Espacios para cada clase
espacios = []
for c in clases:
    for letra in ["A", "B", "C", "D", "E"]:
        espacios.append(
            Espacio(id_clase=c.id_clase, codigo_espacio=letra)
        )
db.add_all(espacios)
db.commit()

# Reservas
for i, c in enumerate(clases):
    reserva = Reserva(
        codigo_reserva=uuid.uuid4().hex[:10].upper(),
        id_usuario=usuarios[i].id_usuario,
        id_clase=c.id_clase,
        id_espacio=espacios[i * 5].id_espacio,
        metodo_pago=MetodoPago.YAPE,
        monto=c.precio,
        fecha_clase=c.fecha,
        estado_pago=EstadoPagoReserva.PAGADO,
        estado_reserva=EstadoReserva.ACTIVA,
    )
    db.add(reserva)

db.commit()

print("Seeds insertados correctamente")

db.close()