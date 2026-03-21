from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="John", description="First name of the user")
    surname: str = Field(..., min_length=2, max_length=100, example="Doe", description="Last name of the user")
    email: EmailStr = Field(..., example="john.doe@example.com", description="Email address of the user")
    password: str = Field(..., min_length=8, max_length=100, example="strongpassword123", description="Password of the user")

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., example="john.doe@example.com", description="Email address of the user")
    password: str = Field(..., min_length=8, max_length=100, example="strongpassword123", description="Password of the user")

class TokenResponse(BaseModel):
    access_token: str = Field(..., description="Access token for the user")
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: int = Field(..., description="User ID")
    exp: Optional[int] = None