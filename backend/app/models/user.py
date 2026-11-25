from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, synonym

from app.db.session import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('member', 'admin')", name="ck_users_role"),
        CheckConstraint("status IN ('active', 'locked')", name="ck_users_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    bio: Mapped[str | None] = mapped_column(String(500), nullable=True)
    role: Mapped[str] = mapped_column(String(20), default="member", server_default="member")
    status: Mapped[str] = mapped_column(String(20), default="active", server_default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Keep the existing authentication API compatible while the database uses the news schema.
    name = synonym("full_name")

    @property
    def is_active(self) -> bool:
        return self.status == "active"

    @is_active.setter
    def is_active(self, value: bool) -> None:
        self.status = "active" if value else "locked"
