from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
import os

from app.core.database import engine, Base
from app.models import Usuario, Clase, Reserva, Pago, GeneroClase, Instructor, InstructorGenero, Espacio, Administrador, Notificacion, Cancelacion, RestablecerContrasena, ReservaHistorialEstado, YapePago

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
from app.routes.cancelacion_routes import router as cancelacion_router
from app.routes.notification_routes import router as notification_router
from app.routes.reset_password_routes import router as reset_password_router
from app.routes.yape_routes import router as yape_router
from app.routes.fidelizacion_routes import router as fidelizacion_router
from app.routes.pexels_routes import router as pexels_router
from app.routes.admin_media_routes import router as admin_media_router

_ON_VERCEL = os.environ.get("VERCEL")
if not _ON_VERCEL:
    Base.metadata.create_all(bind=engine)

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
        pass

    try:
        with engine.connect() as conn:
            conn.execute(text("DROP INDEX uq_usuario_dia_activa ON reservas"))
            conn.commit()
    except Exception:
        pass

fastapi_app = FastAPI(
    title="JMGym API",
    version="1.0.0"
)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "")
if ALLOWED_ORIGINS:
    cors_kwargs = {"allow_origins": ALLOWED_ORIGINS.split(",")}
else:
    cors_kwargs = {"allow_origin_regex": r"https?://(localhost|127\.0\.0\.1|.*\.vercel\.app)(:\d+)?"}

fastapi_app.add_middleware(
    CORSMiddleware,
    **cors_kwargs,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if _ON_VERCEL:
    uploads_dir = "/tmp/uploads"
else:
    uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
try:
    fastapi_app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
except Exception:
    pass

fastapi_app.include_router(auth_router, prefix="/api")
fastapi_app.include_router(class_router, prefix="/api")
fastapi_app.include_router(reservation_router, prefix="/api")
fastapi_app.include_router(payment_router, prefix="/api")
fastapi_app.include_router(admin_router, prefix="/api")
fastapi_app.include_router(admin_auth_router, prefix="/api")
fastapi_app.include_router(instructor_router, prefix="/api")
fastapi_app.include_router(genre_router, prefix="/api")
fastapi_app.include_router(admin_user_router, prefix="/api")
fastapi_app.include_router(user_router, prefix="/api")
fastapi_app.include_router(upload_router, prefix="/api")
fastapi_app.include_router(notification_router, prefix="/api")
fastapi_app.include_router(cancelacion_router, prefix="/api")
fastapi_app.include_router(reset_password_router, prefix="/api")
fastapi_app.include_router(yape_router, prefix="/api")
fastapi_app.include_router(fidelizacion_router, prefix="/api")
fastapi_app.include_router(pexels_router, prefix="/api")
fastapi_app.include_router(admin_media_router, prefix="/api")


@fastapi_app.get("/")
def root():
    return {
        "message": "API funcionando"
    }


from app.services.socket_manager import create_socket_app
app = create_socket_app(fastapi_app)
