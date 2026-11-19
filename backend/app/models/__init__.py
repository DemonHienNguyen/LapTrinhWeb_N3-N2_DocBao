# Import mọi model ở đây để Base.metadata.create_all() "nhìn thấy" và tạo bảng.
# Thêm model mới -> nhớ thêm 1 dòng import vào file này.
from app.models.user import User  # noqa: F401
from app.models.category import Category  # noqa: F401
from app.models.article import Article  # noqa: F401
from app.models.article_image import ArticleImage  # noqa: F401
from app.models.comment import Comment  # noqa: F401
from app.models.tag import Tag  # noqa: F401
from app.models.article_tag import ArticleTag  # noqa: F401
