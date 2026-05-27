from app.core.database import SessionLocal
from app.models.user_model import Usuario
from app.models.class_model import Clase
from app.models.reservation_model import Reserva

db = SessionLocal()

usuarios = [
    Usuario(
        nombre="Erick Alegre",
        correo="erick@gmail.com",
        password="123456",
        rol="cliente"
    ),

    Usuario(
        nombre="Maria Torres",
        correo="maria@gmail.com",
        password="123456",
        rol="cliente"
    ),

    Usuario(
        nombre="Carlos Vega",
        correo="carlos@gmail.com",
        password="123456",
        rol="cliente"
    ),

    Usuario(
        nombre="Lucia Ramos",
        correo="lucia@gmail.com",
        password="123456",
        rol="cliente"
    ),

    Usuario(
        nombre="Admin Gym",
        correo="admin@gmail.com",
        password="admin123",
        rol="admin"
    )
]

db.add_all(usuarios)
db.commit()

clases = [
    Clase(
        nombre="Salsa Básica",
        instructor="Carla Mendoza",
        horario="Lunes 7:00 PM",
        cupos=20
    ),

    Clase(
        nombre="Zumba Fitness",
        instructor="Andrea Ruiz",
        horario="Martes 6:00 PM",
        cupos=25
    ),

    Clase(
        nombre="Merengue Intermedio",
        instructor="Luis Flores",
        horario="Miércoles 8:00 PM",
        cupos=15
    ),

    Clase(
        nombre="Salsa Avanzada",
        instructor="Carla Mendoza",
        horario="Jueves 7:30 PM",
        cupos=18
    ),

    Clase(
        nombre="Zumba Cardio",
        instructor="Andrea Ruiz",
        horario="Viernes 6:30 PM",
        cupos=30
    ),

    Clase(
        nombre="Merengue Básico",
        instructor="Luis Flores",
        horario="Sábado 5:00 PM",
        cupos=20
    )
]

db.add_all(clases)
db.commit()

usuarios_db = db.query(Usuario).all()
clases_db = db.query(Clase).all()

reservas = [
    Reserva(
        usuario_id=usuarios_db[0].id,
        clase_id=clases_db[0].id,
        estado="confirmada"
    ),

    Reserva(
        usuario_id=usuarios_db[1].id,
        clase_id=clases_db[1].id,
        estado="pendiente"
    ),

    Reserva(
        usuario_id=usuarios_db[2].id,
        clase_id=clases_db[2].id,
        estado="confirmada"
    ),

    Reserva(
        usuario_id=usuarios_db[3].id,
        clase_id=clases_db[3].id,
        estado="cancelada"
    ),

    Reserva(
        usuario_id=usuarios_db[0].id,
        clase_id=clases_db[4].id,
        estado="confirmada"
    ),

    Reserva(
        usuario_id=usuarios_db[1].id,
        clase_id=clases_db[5].id,
        estado="pendiente"
    )
]

db.add_all(reservas)
db.commit()

print("✅ Seeds insertados correctamente")

db.close()