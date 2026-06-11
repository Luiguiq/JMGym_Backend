from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
import os

from app.core.database import engine, Base
from app.models import Usuario, Clase, Reserva, Pago, GeneroClase, Instructor, InstructorGenero, Espacio, Administrador, Notificacion, Cancelacion

from app.routes.auth_routes import router as auth_router
from app.routes.class_routes import router as class_router
from app.routes.reservation_routes import router as reservation_router
from app.routes.payment_routes import router as payment_router
from app.routes.admin_routes import router as admin_router
from app.routes.admin_auth_routes import router as admin_auth_router
from app.routes.instructor_routes import router as instructor_router
from app.routes.genre_routes import router as genre_router
from app.routes.admin_user_routes import router as admin_user_router
from app.routes.user_routes import router as user_router
from app.routes.upload_routes import router as upload_router
from app.routes.notification_routes import router as notification_router

Base.metadata.create_all(bind=engine)

# Actualizar ENUM de notificaciones para soportar nuevos tipos
try:
    with engine.connect() as conn:
        conn.execute(
            text(
                "ALTER TABLE notificaciones "
                "MODIFY COLUMN tipo ENUM("
                "'RECORDATORIO','PAGO','PAGO_CONFIRMADO','CAMBIO_HORARIO',"
                "'CAMBIO_INSTRUCTOR','NUEVA_CLASE','CANCELACION','REEMBOLSO',"
                "'BLOQUEO_CUENTA','RESERVA_CONFIRMADA','RESERVA_CANCELADA',"
                "'CAMBIO_ESPACIO','NOTIFICACION_GENERAL'"
                ") NOT NULL"
            )
        )
        conn.commit()
except Exception:
    pass  # La tabla podría no existir aún, no importa

app = FastAPI(
    title="JMGym API",
    version="1.0.0"
)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

app.include_router(auth_router, prefix="/api")
app.include_router(class_router, prefix="/api")
app.include_router(reservation_router, prefix="/api")
app.include_router(payment_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(admin_auth_router, prefix="/api")
app.include_router(instructor_router, prefix="/api")
app.include_router(genre_router, prefix="/api")
app.include_router(admin_user_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(upload_router, prefix="/api")
app.include_router(notification_router, prefix="/api")

@app.get("/")
def root():
    return {
        "message": "API funcionando"
    }