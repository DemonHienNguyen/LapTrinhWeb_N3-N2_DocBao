import unittest

import jwt
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401 - register all models with Base
from app.core.config import settings
from app.core.security import get_current_user, hash_password, require_admin
from app.crud.user import create_user, get_user_by_email
from app.db.session import Base
from app.routers.auth import login, register
from app.schemas.auth import LoginRequest, RegisterRequest


class AuthEndpointTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_public_registration_creates_member_and_returns_signed_token(self):
        data = RegisterRequest.model_validate({
            "name": "  News Reader  ",
            "email": "Reader@Example.com",
            "password": "StrongPass123",
            "role": "admin",
        })

        result = register(data, self.db)

        self.assertEqual(result.user.role, "member")
        self.assertEqual(result.user.name, "News Reader")
        self.assertEqual(result.user.email, "reader@example.com")
        user = get_user_by_email(self.db, "reader@example.com")
        self.assertEqual(user.full_name, "News Reader")
        self.assertEqual(user.status, "active")
        self.assertIsNone(user.avatar_url)
        self.assertNotEqual(user.password_hash, "StrongPass123")
        self.assertTrue({
            "users",
            "categories",
            "articles",
            "article_images",
            "comments",
            "tags",
            "article_tags",
        }.issubset(Base.metadata.tables))
        claims = jwt.decode(result.access_token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        self.assertEqual(claims["role"], "member")
        self.assertEqual(claims["sub"], str(user.id))

    def test_login_checks_password_and_duplicate_email_is_rejected(self):
        register(RegisterRequest(
            name="Member",
            email="member@example.com",
            password="StrongPass123",
        ), self.db)

        result = login(LoginRequest(email="MEMBER@example.com", password="StrongPass123"), self.db)
        self.assertEqual(result.user.role, "member")

        with self.assertRaises(HTTPException) as bad_password:
            login(LoginRequest(email="member@example.com", password="WrongPass123"), self.db)
        self.assertEqual(bad_password.exception.status_code, 401)

        with self.assertRaises(HTTPException) as duplicate:
            register(RegisterRequest(
                name="Another",
                email="member@example.com",
                password="AnotherPass123",
            ), self.db)
        self.assertEqual(duplicate.exception.status_code, 409)

    def test_me_requires_valid_token_and_admin_dependency_checks_database_role(self):
        member_response = register(RegisterRequest(
            name="Member",
            email="member@example.com",
            password="StrongPass123",
        ), self.db)
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=member_response.access_token,
        )
        member = get_current_user(credentials, self.db)
        self.assertEqual(member.role, "member")
        with self.assertRaises(HTTPException) as forbidden:
            require_admin(member)
        self.assertEqual(forbidden.exception.status_code, 403)

        with self.assertRaises(HTTPException) as unauthorized:
            get_current_user(None, self.db)
        self.assertEqual(unauthorized.exception.status_code, 401)

        token_without_expiration = jwt.encode(
            {"sub": str(member.id)},
            settings.JWT_SECRET_KEY,
            algorithm="HS256",
        )
        with self.assertRaises(HTTPException) as missing_expiration:
            get_current_user(
                HTTPAuthorizationCredentials(
                    scheme="Bearer",
                    credentials=token_without_expiration,
                ),
                self.db,
            )
        self.assertEqual(missing_expiration.exception.status_code, 401)

        admin = create_user(
            self.db,
            full_name="Admin",
            email="admin@example.com",
            password_hash=hash_password("AdminStrongPass123"),
            role="admin",
        )
        self.assertEqual(require_admin(admin).role, "admin")


if __name__ == "__main__":
    unittest.main()
