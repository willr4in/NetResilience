from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timezone
from ..models.token import RefreshToken

class TokenRepository:
    def __init__(self, db:Session):
        self.db = db

    def create_refresh_token(self, user_id: int, token: str, expires_at: datetime) -> RefreshToken:
        db_token = RefreshToken(user_id=user_id, token=token, expires_at=expires_at)
        self.db.add(db_token)
        self.db.commit()
        self.db.refresh(db_token)
        return db_token
    
    def get_refresh_token(self, token: str) -> Optional[RefreshToken]:
        return self.db.query(RefreshToken).filter(
            RefreshToken.token == token,
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > datetime.now(timezone.utc)
        ).first()
    
    def revoke_refresh_token(self, token: str) -> bool:
        db_token = self.db.query(RefreshToken).filter(
            RefreshToken.token == token
        ).first()
        if not db_token:
            return False
        db_token.is_revoked = True
        self.db.commit()
        return True
    
    def revoke_all_user_tokens(self, user_id: int) -> None:
        self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id
        ).update({"is_revoked": True})
        self.db.commit()