from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator
from typing import Optional


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=30)
    surname: str = Field(..., min_length=2, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)

    @field_validator('email', mode='before')
    @classmethod
    def validate_email(cls, v: str) -> str:
        import re
        pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Некорректный email адрес')
        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if len(v) < 2:
            raise ValueError('Имя должно содержать минимум 2 символа')
        if len(v) > 30:
            raise ValueError('Имя не должно превышать 30 символов')
        return v

    @field_validator('surname')
    @classmethod
    def validate_surname(cls, v: str) -> str:
        if len(v) < 2:
            raise ValueError('Фамилия должна содержать минимум 2 символа')
        if len(v) > 30:
            raise ValueError('Фамилия не должна превышать 30 символов')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Пароль должен содержать минимум 8 символов')
        if len(v) > 100:
            raise ValueError('Пароль не должен превышать 100 символов')
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Иван",
                "surname": "Иванов",
                "email": "ivan@example.com",
                "password": "password123"
            }
        }
    }


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Пароль должен содержать минимум 8 символов')
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "ivan@example.com",
                "password": "password123"
            }
        }
    }


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="Access token for the user")
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: int = Field(..., description="User ID")
    exp: Optional[int] = None
