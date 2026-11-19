from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def create_user(
    db: Session,
    *,
    name: str,
    email: str,
    password_hash: str,
    role: str = "member",
) -> User:
    user = User(name=name, email=email, password_hash=password_hash, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
