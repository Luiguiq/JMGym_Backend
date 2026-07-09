import asyncio
import socketio
from jose import JWTError, jwt
from app.core.config import SECRET_KEY, ALGORITHM
from app.core.database import SessionLocal
from app.models.admin_model import Administrador
from app.models.user_model import Usuario

sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*'
)

_loop = None


@sio.event
async def connect(sid, environ, auth):
    global _loop
    if _loop is None:
        _loop = asyncio.get_running_loop()

    token = auth.get('token') if auth else None
    if not token:
        return False

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get('sub')
        if not email:
            return False
    except JWTError:
        return False

    db = SessionLocal()
    try:
        user = db.query(Usuario).filter(Usuario.correo == email).first()
        if not user or user.estado != 'ACTIVO':
            return False

        sio.enter_room(sid, f'user_{user.id_usuario}')

        admin = db.query(Administrador).filter(
            Administrador.correo_institucional == email
        ).first()
        if admin and admin.estado == 'ACTIVO':
            sio.enter_room(sid, 'admins')

        return True
    finally:
        db.close()


@sio.event
async def disconnect(sid):
    pass


def emit_to_user(user_id: int, event: str, data: dict):
    loop = _loop
    if loop and loop.is_running():
        asyncio.run_coroutine_threadsafe(
            sio.emit(event, data, room=f'user_{user_id}'),
            loop
        )


def emit_to_admins(event: str, data: dict):
    loop = _loop
    if loop and loop.is_running():
        asyncio.run_coroutine_threadsafe(
            sio.emit(event, data, room='admins'),
            loop
        )


def create_socket_app(app):
    return socketio.ASGIApp(sio, other_asgi_app=app)
