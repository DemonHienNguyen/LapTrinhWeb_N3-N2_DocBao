# Backend base: Python FastAPI + MySQL

Backend ứng dụng báo dành cho lớp **HN-KS25-CNTT1**. Đã có sẵn:

- Kết nối **MySQL** bằng SQLAlchemy + PyMySQL, cấu hình đọc từ file `.env`
- Đăng ký thành viên, đăng nhập JWT và API lấy thông tin tài khoản hiện tại
- Mật khẩu được băm bằng Argon2; admin được tạo riêng bằng lệnh CLI, không thể đăng ký qua form công khai
- Endpoint **health-check** `GET /api/health` kiểm tra kết nối DB
- **CORS** đã bật để frontend gọi được
- File `sql/init.sql` tạo database và 7 bảng tin tức; `python -m app.seed` thêm dữ liệu mẫu
- Trang tài liệu API tự sinh: http://127.0.0.1:8000/docs

## 1. Cần cài trước

| Phần mềm | Ghi chú |
|---|---|
| Python **3.10 trở lên** | https://www.python.org/downloads/ (Windows: tick **Add python.exe to PATH** khi cài) |
| MySQL Server 8 + MySQL Workbench | Bản các bạn đang dùng trên lớp là được |

Kiểm tra Python: mở terminal gõ `python --version` (Mac: `python3 --version`).

## 2. Cấu trúc thư mục

```
backend/
├── app/
│   ├── main.py            # Điểm khởi động: tạo app, bật CORS, gắn các router
│   ├── core/
│   │   ├── config.py      # Đọc cấu hình từ .env
│   │   └── security.py    # Băm mật khẩu, JWT và kiểm tra quyền
│   ├── db/session.py      # Kết nối MySQL, hàm get_db()
│   ├── models/            # Model Users, Categories, Articles, Images, Comments, Tags, Article_Tags
│   ├── schemas/           # Schema request/response cho API
│   ├── crud/              # Truy vấn users
│   ├── routers/           # API health và auth
│   ├── seed.py            # Tạo dữ liệu mẫu bằng SQLAlchemy
│   └── create_admin.py    # Tạo tài khoản admin bằng prompt an toàn
├── sql/
│   ├── init.sql           # Tạo database + 7 bảng (chạy bằng Workbench)
│   └── migrations/        # Migration từ schema users cũ
├── requirements.txt       # Danh sách thư viện Python
├── .env.example           # Mẫu file cấu hình
└── docker-compose.yml     # KHÔNG bắt buộc, xem mục 8
```

Một request đi qua các lớp như sau:

```
Frontend --HTTP--> routers/auth.py --> crud/user.py --> models/user.py --> MySQL
                   (kiểm tra dữ liệu bằng schemas/auth.py)
```

## 3. Bước 1: tạo database bằng MySQL Workbench

1. Mở **MySQL Workbench**, bấm vào connection **Local instance MySQL80** (hoặc connection bạn hay dùng), nhập mật khẩu root.
2. Menu **File → Open SQL Script...**, chọn file `backend/sql/init.sql`.
3. Bấm nút **tia sét ⚡ (Execute)** để chạy cả file.
4. Ở khung **SCHEMAS** bên trái, bấm nút **Refresh ⟳**. Thấy `app_db` với 7 bảng: `users`, `categories`, `articles`, `article_images`, `comments`, `tags`, `article_tags`.

> Nhớ lại thông tin connection (chuột phải connection ở màn hình Home → **Edit Connection**): **Hostname** (thường `127.0.0.1`), **Port** (thường `3306`), **Username** (thường `root`) và mật khẩu. Bước sau sẽ điền đúng các thông tin này.
>
> Nếu nâng cấp database cũ đã có bảng `users` với cột `name` và `is_active`, sau khi chạy `init.sql`, mở và chạy **một lần** `sql/migrations/001_users_news_schema.sql` để chuyển schema tài khoản. Không chạy migration này trên database mới.

## 4. Bước 2: tạo file `.env`

Mở terminal **trong thư mục `backend/`** (VS Code: chuột phải thư mục `backend` → *Open in Integrated Terminal*).

```bash
# Windows
copy .env.example .env
# Mac / Linux
cp .env.example .env
```

Mở file `.env`, điền **mật khẩu root MySQL** và sinh khóa JWT riêng:

```
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=mat_khau_root_cua_ban
DB_NAME=app_db
JWT_SECRET_KEY=...
JWT_ACCESS_TOKEN_MINUTES=60
```

Sinh giá trị `JWT_SECRET_KEY` bằng lệnh `python -c "import secrets; print(secrets.token_urlsafe(48))"` rồi dán vào `.env`. Khóa có tối thiểu 32 ký tự và không được commit hoặc chia sẻ. File `.env` đã được bỏ qua bởi `.gitignore`.

## 5. Bước 3: cài thư viện Python

Tạo môi trường ảo (chỉ làm 1 lần):

```bash
python -m venv .venv
```

Kích hoạt môi trường ảo (làm lại **mỗi lần mở terminal mới**):

| Hệ điều hành | Lệnh |
|---|---|
| Windows PowerShell | `.venv\Scripts\Activate.ps1` |
| Windows CMD | `.venv\Scripts\activate.bat` |
| Mac / Linux | `source .venv/bin/activate` |

> PowerShell báo lỗi "running scripts is disabled"? Chạy một lần:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

Khi đầu dòng terminal hiện `(.venv)` là đã kích hoạt. Cài thư viện:

```bash
pip install -r requirements.txt
```

## 6. Bước 4: tạo dữ liệu mẫu

Thêm vào `.env` một mật khẩu seed riêng dài tối thiểu 12 ký tự:

```
SEED_USER_PASSWORD=mat_khau_mau_tu_12_ky_tu
```

Sau khi đã tạo database bằng MySQL Workbench và cài dependencies, chạy tại thư mục `backend/`:

```bash
python -m app.seed
```

Lệnh tạo dữ liệu mẫu cho tài khoản biên tập/độc giả, danh mục, bài viết, ảnh, bình luận và tag. Có thể chạy lại an toàn; các bản ghi đã có sẽ được giữ nguyên. Mật khẩu này áp dụng cho `editor@example.com` và `reader@example.com`; không sử dụng mật khẩu này trên môi trường thật.

## 7. Bước 5: chạy server

```bash
uvicorn app.main:app --reload
```

Terminal in ra `[DB] Đã kết nối MySQL ...` là thành công. `--reload` giúp server tự khởi động lại mỗi khi bạn lưu code. Tắt server: `Ctrl + C`.

Kiểm tra:

- http://127.0.0.1:8000/api/health → `{"status":"ok","database":"connected"}`
- http://127.0.0.1:8000/docs → thử trực tiếp mọi API bằng nút **Try it out**

### Tạo tài khoản admin

Trong terminal tại `backend/`, chạy `python -m app.create_admin`. Lệnh sẽ hỏi email, tên và mật khẩu admin (tối thiểu 12 ký tự); mật khẩu được nhập ẩn và lưu dưới dạng Argon2 hash. Đăng ký công khai chỉ tạo role `member`.

## 8. Danh sách API hiện có

| Method | URL | Việc làm | Body (JSON) |
|---|---|---|---|
| GET | `/api/health` | Kiểm tra server + DB | |
| POST | `/api/auth/register` | Tạo tài khoản thành viên và nhận JWT | `{"name":"An","email":"an@example.com","password":"StrongPass123"}` |
| POST | `/api/auth/login` | Đăng nhập và nhận JWT | `{"email":"an@example.com","password":"StrongPass123"}` |
| GET | `/api/auth/me` | Lấy tài khoản hiện tại (Bearer JWT) | |

Khi lỗi, API trả về JSON dạng `{"detail": "..."}`. Ví dụ: 404 khi không tìm thấy, 422 khi dữ liệu gửi lên sai.

JWT dùng HS256 và thời hạn cấu hình bởi `JWT_ACCESS_TOKEN_MINUTES`. Backend xác minh chữ ký, hạn token, trạng thái tài khoản và role từ database; không dựa vào role do frontend gửi lên.

## 9. Frontend nối với backend thế nào?

- Frontend gọi tới `http://127.0.0.1:8000/api/...` (cấu hình ở `frontend/js/config.js`).
- Trình duyệt chặn web ở địa chỉ khác gọi API nếu backend không cho phép. Đó là **CORS**. Backend đã cho phép bằng `CORS_ORIGINS` trong `.env`:
  - File `.env.example` đã khai báo hai origin Live Server cục bộ.
  - Khi deploy, thêm chính xác domain frontend vào danh sách phân tách bằng dấu phẩy; không dùng `*` trên môi trường thật.
- Sửa `.env` xong phải **tắt (`Ctrl + C`) và chạy lại** uvicorn.

## 10. Thêm bảng mới

Tạo model trong `app/models/`, import model đó trong `app/models/__init__.py`, và cập nhật `sql/init.sql` (cùng migration nếu database đã chạy). `Base.metadata.create_all()` chỉ tạo bảng còn thiếu, không sửa schema của bảng đã tồn tại.

## 11. Lỗi hay gặp

| Lỗi | Cách sửa |
|---|---|
| `Access denied for user 'root'@'localhost'` | Sai `DB_PASSWORD` trong `.env`. Dùng đúng mật khẩu đăng nhập Workbench |
| `Can't connect to MySQL server on '127.0.0.1'` | MySQL chưa bật. Windows: mở **Services**, tìm **MySQL80**, bấm **Start**. Hoặc kiểm tra lại `DB_PORT` |
| `Unknown database 'app_db'` | Chưa chạy `sql/init.sql` trong Workbench (bước 1) |
| `ModuleNotFoundError: No module named 'fastapi'` | Chưa kích hoạt `.venv` hoặc chưa `pip install -r requirements.txt` |
| `Error loading ASGI app. Could not import module "app.main"` | Đang đứng sai thư mục. Phải `cd` vào `backend/` rồi mới chạy uvicorn |
| `'python' is not recognized...` / mở ra Microsoft Store | Cài lại Python và tick **Add python.exe to PATH** |
| Cổng 8000 đã bị dùng | `uvicorn app.main:app --reload --port 8001`, nhớ sửa `frontend/js/config.js` theo |
| Tiếng Việt bị lỗi font trong DB | Database/bảng phải là `utf8mb4`. Tạo bằng `sql/init.sql` là đúng sẵn |

## 12. (Không bắt buộc) Chạy MySQL bằng Docker

Chỉ dành cho bạn nào đã biết Docker và không muốn cài MySQL. Trong `backend/` chạy `docker compose up -d`: MySQL chạy ở cổng **3307**, tự tạo bảng từ `sql/init.sql`. Khi đó sửa `.env` thành `DB_PORT=3307`, `DB_USER=app_user`, `DB_PASSWORD=app_password`.
