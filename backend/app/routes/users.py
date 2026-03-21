from fastapi import APIRouter, Depends, status
from typing import List
from ..dependencies import get_user_service, get_current_user
from ..schemas.user import UserResponse
from ..services.user_service import UserService
from ..models.user import User

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
def get_all_users(user_service: UserService = Depends(get_user_service)):
    return user_service.get_all_users()

@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)

@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user_by_id(user_id: int, user_service: UserService = Depends(get_user_service)):
    return user_service.get_user_by_id(user_id)

@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(user_id: int, user_service: UserService = Depends(get_user_service)):
    return user_service.delete_user(user_id)