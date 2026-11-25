from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category


def list_categories(db: Session) -> list[Category]:
    """Lấy toàn bộ danh mục sắp xếp theo tên."""
    return list(db.scalars(select(Category).order_by(Category.name.asc(), Category.id.asc())))
