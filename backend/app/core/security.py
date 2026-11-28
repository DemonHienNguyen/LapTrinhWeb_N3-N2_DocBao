import functools
import hashlib
import inspect
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud.revoked_token import is_token_revoked, revoke_token
from app.db.session import get_db
from app.models.user import User

JWT_ALGORITHM = "HS256"
password_hasher = PasswordHasher()
bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return password_hasher.verify(password_hash, password)
    except VerificationError:
        return False


def create_access_token(user: User) -> str:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_MINUTES)
    jti = uuid.uuid4().hex
    claims = {
        "sub": str(user.id),
        "email": user.email,
        "name": user.full_name,
        "role": user.role,
        "jti": jti,
        "iat": now,
        "exp": expires_at,
    }
    return jwt.encode(claims, settings.JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def extract_token_claims(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM],
        options={"require": ["exp", "sub"]},
    )


def get_token_jti(claims: dict[str, Any], raw_token: str | None = None) -> str:
    jti = claims.get("jti")
    if jti:
        return str(jti)
    if raw_token:
        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    raise ValueError("Không thể xác định token JTI")


def revoke_access_token(db: Session, token: str, user_id: int) -> None:
    try:
        claims = extract_token_claims(token)
    except jwt.PyJWTError:
        return
    jti = get_token_jti(claims, token)
    exp = claims.get("exp")
    if exp:
        expires_at = datetime.fromtimestamp(exp, tz=timezone.utc).replace(tzinfo=None)
    else:
        expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_MINUTES
        )
    if not is_token_revoked(db, jti):
        revoke_token(db, jti=jti, user_id=user_id, expires_at=expires_at)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Thông tin đăng nhập không hợp lệ hoặc đã hết hạn",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized

    try:
        claims = extract_token_claims(credentials.credentials)
        user_id = int(claims["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise unauthorized

    jti = get_token_jti(claims, credentials.credentials)
    if is_token_revoked(db, jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Phiên đăng nhập đã bị hủy hoặc token đã bị thu hồi",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.get(User, user_id)
    if user is None:
        raise unauthorized
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị khóa",
        )
    return user


def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    if credentials is None:
        return None
    return get_current_user(credentials=credentials, db=db)


def _validate_user_role(user: User | None, allowed_roles: tuple[str, ...]) -> None:
    if "guest" in allowed_roles:
        if user is None:
            return
        if len(allowed_roles) == 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Thao tác này chỉ dành cho khách chưa đăng nhập",
            )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yêu cầu đăng nhập để truy cập tài nguyên này",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị khóa",
        )

    effective_roles = set(allowed_roles)
    if "member" in effective_roles:
        effective_roles.add("admin")
    if user.role not in effective_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền thực hiện thao tác này",
        )


def require_roles(*roles: str) -> Callable[..., User | None]:
    def role_dependency(
        user: User | None = Depends(
            get_optional_user if "guest" in roles else get_current_user
        ),
    ) -> User | None:
        _validate_user_role(user, roles)
        return user

    return role_dependency


require_guest = require_roles("guest")
require_member = require_roles("member")
require_admin = require_roles("admin")


def roles_required(*allowed_roles: str):
    """Decorator phân quyền cho các endpoint.
    Hỗ trợ kiểm tra quyền 'guest', 'member', 'admin'.
    
    Áp dụng cho function có tham số user hoặc current_user:
        @router.get("/admin-zone")
        @roles_required("admin")
        def admin_zone(user: User = Depends(get_current_user)):
            return {"ok": True}
    """
    def decorator(func: Callable):
        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                user = kwargs.get("user") or kwargs.get("current_user")
                _validate_user_role(user, allowed_roles)
                return await func(*args, **kwargs)

            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                user = kwargs.get("user") or kwargs.get("current_user")
                _validate_user_role(user, allowed_roles)
                return func(*args, **kwargs)

            return sync_wrapper

    return decorator
