from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRegisterSchema(BaseModel):
    name: str = Field(validation_alias="nombre_completo")
    email: EmailStr = Field(validation_alias="correo_personal")
    password: str
    dni: str

    model_config = {"populate_by_name": True}


class UserLoginSchema(BaseModel):
    email: EmailStr = Field(validation_alias="correo_personal")
    password: str

    model_config = {"populate_by_name": True}


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    dni: Optional[str] = None
    estado: str


class AuthResponse(BaseModel):
    user: UserOut
    token: str
