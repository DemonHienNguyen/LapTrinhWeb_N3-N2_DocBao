from getpass import getpass

from argon2 import PasswordHasher
from pydantic import EmailStr, TypeAdapter
from sqlalchemy.exc import IntegrityError

from app import models  # noqa: F401 - register all models before creating tables
from app.crud.user import create_user, get_user_by_email
from app.db.session import Base, SessionLocal, engine


def main() -> None:
    Base.metadata.create_all(bind=engine)
    email = str(TypeAdapter(EmailStr).validate_python(input("Admin email: ").strip())).lower()
    name = input("Admin display name: ").strip()
    if not name:
        raise SystemExit("Tên admin không được để trống.")

    password = getpass("Admin password (at least 12 characters): ")
    if len(password) < 12:
        raise SystemExit("Mật khẩu admin phải có ít nhất 12 ký tự.")
    if password != getpass("Confirm admin password: "):
        raise SystemExit("Mật khẩu xác nhận không khớp.")

    with SessionLocal() as db:
        if get_user_by_email(db, email):
            raise SystemExit("Email này đã tồn tại; không thay đổi tài khoản hiện có.")
        try:
            create_user(
                db,
                full_name=name,
                email=email,
                password_hash=PasswordHasher().hash(password),
                role="admin",
            )
        except IntegrityError as error:
            db.rollback()
            raise SystemExit("Không tạo được admin; email có thể đã được dùng.") from error

    print(f"Đã tạo tài khoản admin: {email}")


if __name__ == "__main__":
    main()
