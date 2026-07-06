from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


DNI_ERROR_MESSAGE = "El DNI debe contener exactamente 8 dígitos."


class UserRegisterSchema(BaseModel):
    name: str = Field(validation_alias="nombre_completo")
    email: EmailStr = Field(validation_alias="correo_personal")
    password: str
    dni: str

    model_config = {"populate_by_name": True}

    @field_validator("dni")
    @classmethod
    def validate_dni(cls, value: str) -> str:
        if not isinstance(value, str) or not value.isdigit() or len(value) != 8:
            raise ValueError(DNI_ERROR_MESSAGE)
        return value


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


class ForgotPasswordRequest(BaseModel):
    correo: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    password: str
