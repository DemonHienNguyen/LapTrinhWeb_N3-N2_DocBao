from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tag import Tag


def list_tags(db: Session) -> list[Tag]:
    """Lấy toàn bộ thẻ tag sắp xếp theo tên."""
    return list(db.scalars(select(Tag).order_by(Tag.name.asc(), Tag.id.asc())))
