from sqlalchemy.orm import Session
from typing import List
from ..repositories.user_repository import UserRepository
from ..schemas.user import UserResponse
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)

    def get_user_by_id(self, user_id: int) -> UserResponse:
        user = self.user_repository.get_user_by_id(user_id)
        if not user:
            logger.warning(f"User not found with id: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        logger.info(f"User found: {user.email} (id={user.id})")
        return UserResponse.model_validate(user)

    def get_user_by_email(self, email: str) -> UserResponse:
        user = self.user_repository.get_user_by_email(email)
        if not user:
            logger.warning(f"User not found with email: {email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        logger.info(f"User found: {user.email} (id={user.id})")
        return UserResponse.model_validate(user)

    def get_all_users(self) -> List[UserResponse]:
        users = self.user_repository.get_all_users()
        logger.info(f"Retrieved all users: {len(users)} found")
        return [UserResponse.model_validate(user) for user in users]

    def delete_user(self, user_id: int) -> dict:
        user = self.user_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        self.user_repository.delete_user(user_id)
        logger.info(f"User deleted: {user.email} (id={user_id})")
        return {"message": f"User {user.email} deleted successfully"}