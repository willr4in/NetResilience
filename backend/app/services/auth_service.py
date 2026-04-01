from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging

from ..config import settings
from ..repositories.user_repository import UserRepository
from ..repositories.token_repository import TokenRepository
from ..schemas.auth import RegisterRequest, TokenPayload
from ..schemas.user import UserCreate
from ..models.user import User

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)
        self.token_repository = TokenRepository(db)

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, user_id: int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {"sub": str(user_id), "exp": expire}
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def create_refresh_token(self, user_id: int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {"sub": str(user_id), "exp": expire}
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        self.token_repository.create_refresh_token(user_id, token, expire)
        return token

    def decode_token(self, token: str) -> TokenPayload:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return TokenPayload(sub=int(payload["sub"]), exp=payload.get("exp"))
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный токен"
            )

    def register(self, data: RegisterRequest) -> User:
        existing = self.user_repository.get_user_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )
        user_data = UserCreate(
            name=data.name,
            surname=data.surname,
            email=data.email,
            password=self.hash_password(data.password)
        )
        return self.user_repository.create_user(user_data)

    def login(self, email: str, password: str) -> User:
        user = self.user_repository.get_user_by_email(email)
        if not user or not self.verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль"
            )
        return user

    def refresh_access_token(self, refresh_token: str) -> str:
        payload = self.decode_token(refresh_token)
        db_token = self.token_repository.get_refresh_token(refresh_token)
        if not db_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный или отозванный токен"
            )
        return self.create_access_token(payload.sub)

    def logout(self, refresh_token: str) -> None:
        self.token_repository.revoke_refresh_token(refresh_token)