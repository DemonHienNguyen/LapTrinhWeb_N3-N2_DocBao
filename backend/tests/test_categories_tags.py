import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401 - register all models with Base
from app.db.session import Base
from app.models.category import Category
from app.models.tag import Tag
from app.routers.categories import get_categories
from app.routers.tags import get_tags


class CategoryAndTagEndpointTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)

        self.db.add_all([
            Category(name="Thể thao", slug="the-thao", description="Tin thể thao"),
            Category(name="Công nghệ", slug="cong-nghe", description="Tin công nghệ"),
            Tag(name="Python", slug="python"),
            Tag(name="AI", slug="ai"),
        ])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_categories_and_tags_list(self):
        categories = get_categories(self.db)
        tags = get_tags(self.db)
        self.assertEqual([c.slug for c in categories], ["cong-nghe", "the-thao"])
        self.assertEqual([t.slug for t in tags], ["ai", "python"])


if __name__ == "__main__":
    unittest.main()
