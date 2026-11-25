import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401 - register all models with Base
from app.core.security import hash_password
from app.db.session import Base
from app.models.article import Article
from app.models.article_image import ArticleImage
from app.models.article_tag import ArticleTag
from app.models.category import Category
from app.models.tag import Tag
from app.models.user import User
from app.routers.articles import get_article_detail, get_articles, get_featured_articles


class ArticleListEndpointTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)

        self.author = User(
            full_name="Editor",
            email="editor@example.com",
            password_hash=hash_password("StrongPass123"),
            role="member",
        )
        self.cat_tech = Category(name="Công nghệ", slug="cong-nghe")
        self.cat_sport = Category(name="Thể thao", slug="the-thao")
        self.tag_ai = Tag(name="AI", slug="ai")
        self.tag_python = Tag(name="Python", slug="python")
        self.db.add_all([self.author, self.cat_tech, self.cat_sport, self.tag_ai, self.tag_python])
        self.db.flush()

        self.article_1 = Article(
            title="AI thay đổi lập trình web",
            slug="ai-thay-doi-lap-trinh-web",
            summary="Tổng quan xu hướng AI",
            content="<p>Nội dung chi tiết về AI</p>",
            author_id=self.author.id,
            category_id=self.cat_tech.id,
            status="published",
            is_featured=True,
        )
        self.article_2 = Article(
            title="FastAPI cho người mới",
            slug="fastapi-cho-nguoi-moi",
            summary="Hướng dẫn FastAPI",
            content="<p>Chi tiết FastAPI</p>",
            author_id=self.author.id,
            category_id=self.cat_tech.id,
            status="published",
            is_featured=False,
        )
        self.article_pending = Article(
            title="Bài chờ duyệt",
            slug="bai-cho-duyet",
            summary="Chưa xuất bản",
            content="<p>Draft</p>",
            author_id=self.author.id,
            category_id=self.cat_sport.id,
            status="pending",
            is_featured=True,
        )
        self.db.add_all([self.article_1, self.article_2, self.article_pending])
        self.db.flush()
        self.db.add_all([
            ArticleTag(article_id=self.article_1.id, tag_id=self.tag_ai.id),
            ArticleTag(article_id=self.article_2.id, tag_id=self.tag_python.id),
            ArticleImage(
                article_id=self.article_1.id,
                image_url="https://example.com/ai.png",
                caption="Minh họa AI",
            ),
        ])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_articles_featured_filter_search_and_pagination(self):
        featured = get_featured_articles(limit=5, db=self.db)
        self.assertEqual([a.slug for a in featured], ["ai-thay-doi-lap-trinh-web"])

        all_pub = get_articles(
            category_slug=None,
            tag_slug=None,
            q=None,
            is_featured=None,
            page=1,
            limit=1,
            db=self.db,
        )
        self.assertEqual(all_pub.total, 2)
        self.assertEqual(all_pub.total_pages, 2)
        self.assertEqual(len(all_pub.items), 1)

        by_tag = get_articles(
            category_slug=None,
            tag_slug="python",
            q=None,
            is_featured=None,
            page=1,
            limit=10,
            db=self.db,
        )
        self.assertEqual([a.slug for a in by_tag.items], ["fastapi-cho-nguoi-moi"])

        by_search = get_articles(
            category_slug=None,
            tag_slug=None,
            q="FastAPI",
            is_featured=None,
            page=1,
            limit=10,
            db=self.db,
        )
        self.assertEqual([a.slug for a in by_search.items], ["fastapi-cho-nguoi-moi"])

    def test_article_detail_increments_views_and_returns_related(self):
        detail = get_article_detail("ai-thay-doi-lap-trinh-web", self.db)
        self.assertEqual(detail.views_count, 1)
        self.assertEqual(detail.author.full_name, "Editor")
        self.assertEqual(detail.category.slug, "cong-nghe")
        self.assertEqual([t.slug for t in detail.tags], ["ai"])
        self.assertEqual(len(detail.images), 1)
        self.assertEqual([r.slug for r in detail.related_articles], ["fastapi-cho-nguoi-moi"])

        with self.assertRaises(HTTPException) as not_found:
            get_article_detail("bai-cho-duyet", self.db)
        self.assertEqual(not_found.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
