from fastapi import APIRouter, Depends, status
from typing import List
from ..dependencies import get_user_service
from ..schemas.user import UserCreate, UserResponse
from ..services.user_service import UserService

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
def get_all_users(user_service: UserService = Depends(get_user_service)):
    return user_service.get_all_users()

@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user_by_id(user_id: int, user_service: UserService = Depends(get_user_service)):
    return user_service.get_user_by_id(user_id)

@router.get("/email/{email}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user_by_email(email: str, user_service: UserService = Depends(get_user_service)):
    return user_service.get_user_by_email(email)

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, user_service: UserService = Depends(get_user_service)):
    return user_service.create_user(user_data)

@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(user_id: int, user_service: UserService = Depends(get_user_service)):
    return user_service.delete_user(user_id)