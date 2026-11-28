from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.revoked_token import RevokedToken


def is_token_revoked(db: Session, jti: str) -> bool:
    stmt = select(RevokedToken.id).where(RevokedToken.jti == jti).limit(1)
    return db.scalar(stmt) is not None


def revoke_token(
    db: Session,
    *,
    jti: str,
    user_id: int,
    expires_at: datetime,
) -> RevokedToken:
    revoked = RevokedToken(
        jti=jti,
        user_id=user_id,
        expires_at=expires_at,
    )
    db.add(revoked)
    db.commit()
    db.refresh(revoked)
    return revoked
