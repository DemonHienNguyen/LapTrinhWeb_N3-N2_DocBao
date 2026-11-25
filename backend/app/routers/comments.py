from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.crud import comment as comment_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.comment import CommentCreateRequest, CommentOut

router = APIRouter(tags=["Comments"])


@router.get("/articles/{article_id}/comments", response_model=list[CommentOut])
def get_article_comments(article_id: int, db: Session = Depends(get_db)):
    """Lấy danh sách bình luận của bài viết đã xuất bản."""
    article = comment_crud.get_published_article_by_id(db, article_id)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy bài viết",
        )
    return comment_crud.list_comments_by_article(db, article_id)


@router.post(
    "/articles/{article_id}/comments",
    response_model=CommentOut,
    status_code=status.HTTP_201_CREATED,
)
def create_article_comment(
    article_id: int,
    data: CommentCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Gửi bình luận cho bài viết (yêu cầu đăng nhập)."""
    article = comment_crud.get_published_article_by_id(db, article_id)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy bài viết",
        )
    return comment_crud.create_comment(
        db,
        article_id=article_id,
        user_id=current_user.id,
        content=data.content,
    )


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Xóa bình luận (chỉ chủ bình luận hoặc admin)."""
    comment = comment_crud.get_comment_by_id(db, comment_id)
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy bình luận",
        )
    if comment.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xóa bình luận này",
        )
    comment_crud.delete_comment(db, comment)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
