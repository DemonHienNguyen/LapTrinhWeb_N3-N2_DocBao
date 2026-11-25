import html
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CommentAuthorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    avatar_url: str | None = None


class CommentCreateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=1000)

    @field_validator("content")
    @classmethod
    def sanitize_content(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Nội dung bình luận không được để trống")
        if len(stripped) > 1000:
            raise ValueError("Nội dung bình luận tối đa 1000 ký tự")
        return html.escape(stripped, quote=True)


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    article_id: int
    user_id: int
    content: str
    created_at: datetime
    user: CommentAuthorOut
