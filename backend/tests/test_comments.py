import unittest

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401 - register all models with Base
from app.core.security import hash_password
from app.db.session import Base
from app.models.article import Article
from app.models.category import Category
from app.models.user import User
from app.routers.comments import (
    create_article_comment,
    delete_comment,
    get_article_comments,
)
from app.schemas.comment import CommentCreateRequest


class CommentEndpointTests(unittest.TestCase):
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
        self.other_user = User(
            full_name="Reader",
            email="reader@example.com",
            password_hash=hash_password("StrongPass123"),
            role="member",
        )
        self.category = Category(name="Công nghệ", slug="cong-nghe")
        self.db.add_all([self.author, self.other_user, self.category])
        self.db.flush()

        self.article = Article(
            title="Bài viết công nghệ",
            slug="bai-viet-cong-nghe",
            summary="Tóm tắt",
            content="<p>Nội dung</p>",
            author_id=self.author.id,
            category_id=self.category.id,
            status="published",
        )
        self.db.add(self.article)
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_comments_create_sanitize_list_and_delete_permissions(self):
        with self.assertRaises(ValidationError):
            CommentCreateRequest(content="   ")

        with self.assertRaises(ValidationError):
            CommentCreateRequest(content="a" * 1001)

        created = create_article_comment(
            self.article.id,
            CommentCreateRequest(content="  <script>alert(1)</script> Hay quá!  "),
            db=self.db,
            current_user=self.other_user,
        )
        self.assertEqual(
            created.content,
            "&lt;script&gt;alert(1)&lt;/script&gt; Hay quá!",
        )

        comments = get_article_comments(self.article.id, db=self.db)
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0].user.full_name, "Reader")

        with self.assertRaises(HTTPException) as forbidden:
            delete_comment(created.id, db=self.db, current_user=self.author)
        self.assertEqual(forbidden.exception.status_code, 403)

        delete_comment(created.id, db=self.db, current_user=self.other_user)
        self.assertEqual(get_article_comments(self.article.id, db=self.db), [])


if __name__ == "__main__":
    unittest.main()
