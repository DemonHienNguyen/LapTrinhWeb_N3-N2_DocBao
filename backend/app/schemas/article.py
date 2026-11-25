from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ArticleAuthorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    avatar_url: str | None = None


class ArticleCategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str


class ArticleTagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str


class ArticleSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    summary: str | None = None
    thumbnail_url: str | None = None
    views_count: int
    is_featured: bool
    created_at: datetime
    author: ArticleAuthorOut
    category: ArticleCategoryOut
    tags: list[ArticleTagOut] = []


class ArticleListOut(BaseModel):
    items: list[ArticleSummaryOut]
    total: int
    page: int
    limit: int
    total_pages: int
