from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud import category as category_crud
from app.db.session import get_db
from app.schemas.category import CategoryOut

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryOut])
def get_categories(db: Session = Depends(get_db)):
    """Lấy danh sách chuyên mục công khai."""
    return category_crud.list_categories(db)
