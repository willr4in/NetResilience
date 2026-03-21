from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.user import User
from ..schemas.user import UserCreate

class UserRepository:
    def __init__(self, db:Session):
        self.db = db

    def create_user(self, user_data: UserCreate) -> User:
        user = User(
            name=user_data.name,
            surname=user_data.surname,
            email=user_data.email,
            hashed_password=user_data.password  
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
    
    def get_all_users(self) -> List[User]:
        return self.db.query(User).all()
    
    def delete_user(self, user_id: int) -> bool:
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        self.db.delete(user)
        self.db.commit()
        return True