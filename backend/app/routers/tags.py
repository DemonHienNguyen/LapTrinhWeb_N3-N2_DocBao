from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud import tag as tag_crud
from app.db.session import get_db
from app.schemas.tag import TagOut

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get("", response_model=list[TagOut])
def get_tags(db: Session = Depends(get_db)):
    """Lấy danh sách thẻ tag công khai."""
    return tag_crud.list_tags(db)
