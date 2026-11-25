import math

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.crud import article as article_crud
from app.db.session import get_db
from app.models.article import Article
from app.schemas.article import ArticleListOut, ArticleSummaryOut

router = APIRouter(prefix="/articles", tags=["Articles"])


def _serialize_summary(article: Article) -> ArticleSummaryOut:
    return ArticleSummaryOut(
        id=article.id,
        title=article.title,
        slug=article.slug,
        summary=article.summary,
        thumbnail_url=article.thumbnail_url,
        views_count=article.views_count,
        is_featured=article.is_featured,
        created_at=article.created_at,
        author=article.author,
        category=article.category,
        tags=[link.tag for link in article.tag_links if link.tag is not None],
    )


@router.get("/featured", response_model=list[ArticleSummaryOut])
def get_featured_articles(
    limit: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db),
):
    """Lấy danh sách bài viết nổi bật cho trang chủ."""
    articles = article_crud.list_featured_articles(db, limit=limit)
    return [_serialize_summary(article) for article in articles]


@router.get("", response_model=ArticleListOut)
def get_articles(
    category_slug: str | None = Query(default=None),
    tag_slug: str | None = Query(default=None),
    q: str | None = Query(default=None, max_length=200),
    is_featured: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Lấy danh sách bài viết đã xuất bản, hỗ trợ lọc, tìm kiếm và phân trang."""
    articles, total = article_crud.list_published_articles(
        db,
        category_slug=category_slug,
        tag_slug=tag_slug,
        q=q,
        is_featured=is_featured,
        page=page,
        limit=limit,
    )
    total_pages = math.ceil(total / limit) if total > 0 else 0
    return ArticleListOut(
        items=[_serialize_summary(article) for article in articles],
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
    )
