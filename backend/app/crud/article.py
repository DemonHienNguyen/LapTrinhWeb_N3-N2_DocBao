from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.article import Article
from app.models.article_tag import ArticleTag
from app.models.category import Category
from app.models.tag import Tag


def _article_eager_options():
    return (
        selectinload(Article.author),
        selectinload(Article.category),
        selectinload(Article.tag_links).selectinload(ArticleTag.tag),
    )


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def list_featured_articles(db: Session, *, limit: int = 5) -> list[Article]:
    """Lấy danh sách bài viết nổi bật đã xuất bản."""
    stmt = (
        select(Article)
        .options(*_article_eager_options())
        .where(Article.status == "published", Article.is_featured.is_(True))
        .order_by(Article.created_at.desc(), Article.id.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt))


def list_published_articles(
    db: Session,
    *,
    category_slug: str | None = None,
    tag_slug: str | None = None,
    q: str | None = None,
    is_featured: bool | None = None,
    page: int = 1,
    limit: int = 10,
) -> tuple[list[Article], int]:
    """Lấy danh sách bài viết đã xuất bản có lọc, tìm kiếm và phân trang."""
    filters = [Article.status == "published"]

    if is_featured is not None:
        filters.append(Article.is_featured.is_(is_featured))

    if category_slug:
        filters.append(Article.category.has(Category.slug == category_slug))

    if tag_slug:
        filters.append(
            Article.tag_links.any(ArticleTag.tag.has(Tag.slug == tag_slug))
        )

    if q and q.strip():
        pattern = f"%{_escape_like(q.strip())}%"
        filters.append(
            or_(
                Article.title.ilike(pattern, escape="\\"),
                Article.summary.ilike(pattern, escape="\\"),
                Article.content.ilike(pattern, escape="\\"),
            )
        )

    total = db.scalar(select(func.count(Article.id)).where(*filters)) or 0
    offset = (page - 1) * limit

    stmt = (
        select(Article)
        .options(*_article_eager_options())
        .where(*filters)
        .order_by(Article.created_at.desc(), Article.id.desc())
        .offset(offset)
        .limit(limit)
    )
    items = list(db.scalars(stmt))
    return items, total
