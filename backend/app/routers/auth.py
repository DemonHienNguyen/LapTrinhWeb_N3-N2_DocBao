from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    bearer_scheme,
    create_access_token,
    get_current_user,
    hash_password,
    revoke_access_token,
    verify_password,
)
from app.crud import user as user_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserOut

router = APIRouter(prefix="/auth", tags=["Authentication"])


def build_auth_response(user: User) -> AuthResponse:
    return AuthResponse(
        access_token=create_access_token(user),
        expires_in=settings.JWT_ACCESS_TOKEN_MINUTES * 60,
        user=user,
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if user_crud.get_user_by_email(db, data.email):
        raise HTTPException(status_code=409, detail="Email này đã được đăng ký")

    try:
        user = user_crud.create_user(
            db,
            full_name=data.name,
            email=data.email,
            password_hash=hash_password(data.password),
            role="member",
        )
    except IntegrityError:
        db.rollback()
        if user_crud.get_user_by_email(db, data.email):
            raise HTTPException(status_code=409, detail="Email này đã được đăng ký")
        raise
    return build_auth_response(user)


@router.post("/login", response_model=AuthResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = user_crud.get_user_by_email(db, data.email)
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không đúng",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản của bạn đã bị khóa. Vui lòng liên hệ quản trị viên.",
        )
    return build_auth_response(user)


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if credentials is not None:
        revoke_access_token(db, credentials.credentials, user_id=user.id)
    return {"message": "Đăng xuất thành công"}


@router.get("/me", response_model=UserOut)
def get_me(user: User = Depends(get_current_user)):
    return user
