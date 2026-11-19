# Base code dự án thực tập: HN-KS25-CNTT1

Khung dự án chung cho các nhóm (04/11 – 25/11/2026). Gồm 2 phần đã nối sẵn với nhau:

| Thư mục | Công nghệ | Hướng dẫn |
|---|---|---|
| [`backend/`](backend/README.md) | Python FastAPI + MySQL (SQLAlchemy) | `backend/README.md` |
| [`frontend/`](frontend/README.md) | HTML · CSS · JavaScript thuần | `frontend/README.md` |

```
Trình duyệt (frontend) --fetch JSON + Bearer JWT--> FastAPI (backend :8000/api) --SQLAlchemy--> MySQL (:3306)
```

## Chạy nhanh

1. **MySQL Workbench:** File → Open SQL Script → chọn `backend/sql/init.sql` → bấm ⚡ Execute.
2. **Backend** (terminal trong thư mục `backend/`):
   ```bash
   copy .env.example .env               # Mac/Linux: cp .env.example .env
   # mở .env, điền DB_PASSWORD và JWT_SECRET_KEY
   # JWT_SECRET_KEY: python -c "import secrets; print(secrets.token_urlsafe(48))"
   python -m venv .venv
   .venv\Scripts\activate               # Mac/Linux: source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload        # http://127.0.0.1:8000/docs
   ```
3. **Frontend:** VS Code → chuột phải `frontend/index.html` → *Open with Live Server*.

Frontend có giao diện đọc tin mẫu, đăng nhập/đăng ký thành viên và trang **Demo API**. Tạo admin riêng bằng `python -m app.create_admin` tại thư mục `backend/`. Sau đó mỗi nhóm đổi ví dụ `items` thành các chức năng của đề tài mình (xem mục *Thêm chức năng* / *Thêm trang mới* trong từng README).
