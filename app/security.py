from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.database import get_db
from app.models.user_model import Usuario
from app.models.admin_model import Administrador

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        correo: Optional[str] = payload.get("sub")
        if correo is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = (
        db.query(Usuario)
        .filter(Usuario.correo == correo)
        .first()
    )
    if user is None:
        raise credentials_exception
    return user


def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Administrador:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales de administrador",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        correo: Optional[str] = payload.get("sub")
        if correo is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    admin = (
        db.query(Administrador)
        .filter(Administrador.correo_institucional == correo)
        .first()
    )
    if admin is None:
        raise credentials_exception
    if admin.estado != "ACTIVO":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta de administrador inactiva",
        )
    return admin
