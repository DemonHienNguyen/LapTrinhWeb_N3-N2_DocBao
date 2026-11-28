from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.article import Article
from app.models.comment import Comment


def get_published_article_by_id(db: Session, article_id: int) -> Article | None:
    """Tìm bài viết đã xuất bản theo ID."""
    return db.scalar(
        select(Article).where(Article.id == article_id, Article.status == "published")
    )


def list_comments_by_article(db: Session, article_id: int) -> list[Comment]:
    """Lấy danh sách bình luận của một bài viết kèm thông tin tác giả."""
    stmt = (
        select(Comment)
        .options(selectinload(Comment.user))
        .where(Comment.article_id == article_id)
        .order_by(Comment.created_at.desc(), Comment.id.desc())
    )
    return list(db.scalars(stmt))


def create_comment(
    db: Session,
    *,
    article_id: int,
    user_id: int,
    content: str,
) -> Comment:
    """Tạo bình luận mới và tải lại thông tin người gửi."""
    comment = Comment(article_id=article_id, user_id=user_id, content=content)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return db.scalar(
        select(Comment)
        .options(selectinload(Comment.user))
        .where(Comment.id == comment.id)
    )


def get_comment_by_id(db: Session, comment_id: int) -> Comment | None:
    """Tìm bình luận theo ID."""
    return db.get(Comment, comment_id)


def delete_comment(db: Session, comment: Comment) -> None:
    """Xóa bình luận."""
    db.delete(comment)
    db.commit()
