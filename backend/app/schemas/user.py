from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=30, description="Name")
    surname: str = Field(..., min_length=2, max_length=30, description="Surname")
    email: EmailStr = Field(..., description="Email address")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100, description="Password")

class UserResponse(UserBase):
    id: int = Field(..., description="ID of the user")
    created_at: datetime

    model_config = {"from_attributes": True}