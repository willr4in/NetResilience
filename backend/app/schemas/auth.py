from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=30, description="First name of the user")
    surname: str = Field(..., min_length=2, max_length=30, description="Last name of the user")
    email: EmailStr = Field(..., description="Email address of the user")
    password: str = Field(..., min_length=8, max_length=100, description="Password of the user")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "John",
                "surname": "Doe",
                "email": "john.doe@example.com",
                "password": "strongpassword123"
            }
        }
    }

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Email address of the user")
    password: str = Field(..., min_length=8, max_length=100, description="Password of the user")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "john.doe@example.com",
                "password": "strongpassword123"
            }
        }
    }

class TokenResponse(BaseModel):
    access_token: str = Field(..., description="Access token for the user")
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: int = Field(..., description="User ID")
    exp: Optional[int] = None