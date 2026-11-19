"""Insert repeatable sample records for the news schema."""

from sqlalchemy import select

from app import models  # noqa: F401 - register every model before create_all
from app.core.config import settings
from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
from app.models import Article, ArticleImage, ArticleTag, Category, Comment, Tag, User


def main() -> None:
    if len(settings.SEED_USER_PASSWORD) < 12:
        raise SystemExit(
            "SEED_USER_PASSWORD trong .env phải có ít nhất 12 ký tự trước khi chạy seed."
        )

    Base.metadata.create_all(bind=engine)
    with SessionLocal.begin() as db:
        users_by_email = {}
        for full_name, email in (
            ("Biên tập viên mẫu", "editor@example.com"),
            ("Độc giả mẫu", "reader@example.com"),
        ):
            user = db.scalar(select(User).where(User.email == email))
            if user is None:
                user = User(
                    full_name=full_name,
                    email=email,
                    password_hash=hash_password(settings.SEED_USER_PASSWORD),
                    role="member",
                    status="active",
                )
                db.add(user)
                db.flush()
            users_by_email[email] = user

        categories_by_slug = {}
        for name, slug, description in (
            ("Thời sự", "thoi-su", "Tin tức thời sự trong nước và quốc tế."),
            ("Công nghệ", "cong-nghe", "Sản phẩm và xu hướng công nghệ."),
            ("Đời sống", "doi-song", "Nhịp sống và câu chuyện thường ngày."),
        ):
            category = db.scalar(select(Category).where(Category.slug == slug))
            if category is None:
                category = Category(name=name, slug=slug, description=description)
                db.add(category)
                db.flush()
            categories_by_slug[slug] = category

        tags_by_slug = {}
        for name, slug in (
            ("AI", "ai"),
            ("Chuyển đổi số", "chuyen-doi-so"),
            ("Tin mới", "tin-moi"),
        ):
            tag = db.scalar(select(Tag).where(Tag.slug == slug))
            if tag is None:
                tag = Tag(name=name, slug=slug)
                db.add(tag)
                db.flush()
            tags_by_slug[slug] = tag

        articles_by_slug = {}
        for title, slug, summary, category_slug, thumbnail_url in (
            (
                "Trí tuệ nhân tạo đang thay đổi cách làm việc",
                "ai-thay-doi-cach-lam-viec",
                "Một số ứng dụng AI đang giúp tự động hóa các công việc thường ngày.",
                "cong-nghe",
                "https://images.unsplash.com/photo-1677442136019-21780ecad995",
            ),
            (
                "Đô thị xanh bắt đầu từ những thay đổi nhỏ",
                "do-thi-xanh-thay-doi-nho",
                "Các sáng kiến cộng đồng góp phần cải thiện chất lượng sống đô thị.",
                "doi-song",
                "https://images.unsplash.com/photo-1518005020951-eccb494ad742",
            ),
        ):
            article = db.scalar(select(Article).where(Article.slug == slug))
            if article is None:
                article = Article(
                    title=title,
                    slug=slug,
                    summary=summary,
                    content=f"{summary}\n\nĐây là nội dung mẫu để kiểm tra cấu trúc bài viết.",
                    thumbnail_url=thumbnail_url,
                    author=users_by_email["editor@example.com"],
                    category=categories_by_slug[category_slug],
                    status="published",
                    is_featured=(slug == "ai-thay-doi-cach-lam-viec"),
                )
                db.add(article)
                db.flush()
            articles_by_slug[slug] = article

        first_article = articles_by_slug["ai-thay-doi-cach-lam-viec"]
        image_url = "https://images.unsplash.com/photo-1677442136019-21780ecad995"
        if db.scalar(
            select(ArticleImage.id).where(
                ArticleImage.article_id == first_article.id,
                ArticleImage.image_url == image_url,
            )
        ) is None:
            db.add(ArticleImage(
                article_id=first_article.id,
                image_url=image_url,
                caption="Minh họa về trí tuệ nhân tạo",
            ))

        comment_text = "Cảm ơn bài viết, thông tin rất hữu ích."
        if db.scalar(
            select(Comment.id).where(
                Comment.article_id == first_article.id,
                Comment.user_id == users_by_email["reader@example.com"].id,
                Comment.content == comment_text,
            )
        ) is None:
            db.add(Comment(
                article_id=first_article.id,
                user_id=users_by_email["reader@example.com"].id,
                content=comment_text,
            ))

        tag_pairs = (
            (first_article, tags_by_slug["ai"]),
            (first_article, tags_by_slug["chuyen-doi-so"]),
            (articles_by_slug["do-thi-xanh-thay-doi-nho"], tags_by_slug["tin-moi"]),
        )
        for article, tag in tag_pairs:
            if db.get(ArticleTag, (article.id, tag.id)) is None:
                db.add(ArticleTag(article_id=article.id, tag_id=tag.id))

    print("Đã khởi tạo các bảng và dữ liệu mẫu. Seed có thể chạy lại an toàn.")


if __name__ == "__main__":
    main()
