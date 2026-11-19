# Frontend base: HTML · CSS · JavaScript thuần

Khung frontend chung cho các nhóm thực tập lớp **HN-KS25-CNTT1**. Không dùng framework, không cần cài đặt hay build gì. Đã có sẵn:

- Layout chung (header + menu + footer), đăng nhập và đăng ký thành viên
- Module gọi API `js/api.js` dùng **fetch**: cấu hình `baseURL` một lần, tự gửi JWT và chuẩn hoá lỗi
- Trang chủ tin tức mẫu: lọc chủ đề, tìm kiếm và đọc nội dung bài viết mẫu
- Trang **Items**: ví dụ CRUD đầy đủ (thêm / sửa / xoá / tìm kiếm) gọi sang backend FastAPI

## 1. Cấu trúc thư mục

```
frontend/
├── index.html             # Trang chủ tin tức
├── pages/
│   ├── items.html         # Trang CRUD mẫu
│   ├── article.html       # Trang chi tiết bài viết
│   ├── login.html         # Đăng nhập
│   ├── register.html      # Đăng ký thành viên
│   ├── profile.html       # Trang cá nhân (cần JWT member/admin)
│   └── admin.html         # Trang quản trị (cần JWT admin)
├── css/
│   └── style.css          # Style chung, đổi màu ở :root
├── js/
│   ├── config.js          # API_BASE_URL: địa chỉ backend
│   ├── api.js             # fetch wrapper + api.get / post / put / delete
│   ├── utils.js           # escapeHtml, formatMoney, showToast...
│   ├── layout.js          # Chèn header/menu/footer vào mọi trang
│   ├── news-data.js       # Dữ liệu bài viết mẫu dùng chung
│   ├── auth.js            # Đọc role trong JWT và kiểm soát menu/trang
│   └── pages/             # Mỗi trang 1 file JS riêng
│       ├── home.js
│       ├── article.js
│       ├── profile.js
│       ├── admin.js
│       ├── login.js
│       ├── register.js
│       └── items.js
└── assets/images/         # Ảnh, logo, icon
```

## 2. Chạy frontend

**Bước 1: chạy backend trước.** Làm theo `backend/README.md` cho đến khi mở http://127.0.0.1:8000/api/health thấy `"database":"connected"`.

**Bước 2: mở frontend bằng Live Server.** Trong VS Code, cài extension *Live Server* (Ritwick Dey), chuột phải `frontend/index.html` → **Open with Live Server**. Trang mở ở `http://127.0.0.1:5500/index.html` và tự tải lại khi bạn lưu file.

Trang chủ hiển thị giao diện đọc tin mẫu. Bấm **Demo API** trên menu để thử thêm / sửa / xoá item qua backend, rồi mở MySQL Workbench xem bảng `items` thay đổi theo.

Khi chưa đăng nhập, menu có **Đăng nhập** và **Đăng ký**. Đăng ký tạo tài khoản `member`; admin phải được tạo riêng từ backend. Sau khi đăng nhập, thành viên vào **Trang cá nhân**, admin thấy thêm **Quản trị**.

> Nhấp đúp mở thẳng file `index.html` (địa chỉ `file:///...`) thường vẫn chạy, nhưng hay gặp lỗi khó hiểu. Nên dùng Live Server.

## 3. Frontend nối với backend thế nào?

```
Trình duyệt (FE: 127.0.0.1:5500) --fetch + Bearer JWT--> Backend FastAPI (127.0.0.1:8000/api) --> MySQL
```

- Địa chỉ backend nằm ở **một chỗ duy nhất**: `js/config.js`
  ```js
  API_BASE_URL: "http://127.0.0.1:8000/api",
  AUTH_TOKEN_KEY: "token",
  ```
  Backend đổi cổng, hoặc deploy lên server, thì chỉ sửa dòng này.
- Mọi lời gọi API đều qua `js/api.js`; module dùng `fetch`, tự thêm `Authorization: Bearer <token>` khi `localStorage` có giá trị ở key `token`, và trả về dữ liệu JSON:
  ```js
  try {
    const items = await api.get("/items");               // GET /api/items
    const found = await api.get("/items", { q: "trà" }); // GET /api/items?q=trà
    const item  = await api.post("/items", { name: "Trà đá", price: 5000 });
    await api.put(`/items/${item.id}`, { price: 6000 });
    await api.delete(`/items/${item.id}`);
  } catch (error) {
    showToast(error.message, "error");  // câu báo lỗi đã được dịch cho dễ đọc
    console.log(error.status);          // 401, 403, 404, 422, 500... hoặc 0 nếu không gọi được server
  }
  ```
- Lưu JWT sau khi đăng nhập bằng `localStorage.setItem("token", jwt)`. API client gửi token ở mọi request; nhận `401` sẽ xoá token hết hạn và trả lỗi hướng dẫn đăng nhập lại. `403` trả lỗi không đủ quyền nhưng không xoá token.
- Trang đăng nhập theo bố cục form nổi ở giữa trang của giao diện tham khảo; form gọi `POST /api/auth/login`. Đăng ký gọi `POST /api/auth/register` và tự đăng nhập sau khi tạo tài khoản.
- `js/auth.js` đọc claim `role` (ví dụ `member` hoặc `admin`), `roles` hoặc `realm_access.roles` để hiện menu và bảo vệ `pages/profile.html` / `pages/admin.html`. JWT phía trình duyệt chỉ được giải mã, không xác minh chữ ký; backend bắt buộc phải xác minh token và quyền trên mọi API được bảo vệ.
  Payload tối thiểu cho giao diện: `{"sub":"user-123","name":"Tên người dùng","role":"member"}`. Token admin dùng `"role":"admin"`; token cần có `exp` để tự nhận diện hết hạn.
- `showToast(message, "success" | "error" | "info" | "warning")` hiển thị thông báo có thể đóng, tự ẩn và hỗ trợ screen reader.
- Backend phải cho phép FE gọi (**CORS**). `backend/.env.example` khai báo sẵn các origin Live Server thường dùng; cập nhật `CORS_ORIGINS` nếu frontend chạy ở địa chỉ khác.

`frontend/.env.example` ghi lại các cấu hình tương ứng cho frontend tĩnh. Trình duyệt không tự đọc file `.env`, vì vậy khi thay đổi các giá trị này hãy cập nhật `js/config.js`.

## 4. Thêm trang mới (vd: trang Sản phẩm)

1. Copy `pages/items.html` thành `pages/products.html`, sửa `<title>` và nội dung HTML.
2. Copy `js/pages/items.js` thành `js/pages/products.js`, đổi `/items` thành `/products` (API của nhóm bạn).
3. Ở cuối `pages/products.html`, đổi `../js/pages/items.js` thành `../js/pages/products.js`.
4. Thêm link vào menu trong `js/layout.js`:
   ```js
   { href: "pages/products.html", label: "Sản phẩm" },
   ```

Lưu ý khi tạo trang:

- Trang trong `pages/` để `<body data-root="../">`; trang ở thư mục gốc để `data-root="./"`.
- Giữ thứ tự thẻ `<script>`: `config.js` → `api.js` (nếu trang gọi API) → `utils.js` → `layout.js` → `news-data.js` (nếu trang dùng bài viết) → script riêng của trang.
- Khi chèn dữ liệu người dùng nhập vào `innerHTML`, luôn bọc bằng `escapeHtml(...)` để chống chèn mã độc (XSS).

## 5. Lỗi hay gặp

| Hiện tượng | Cách sửa |
|---|---|
| "Không kết nối được backend..." | Backend chưa chạy, hoặc `API_BASE_URL` trong `js/config.js` sai cổng |
| "Backend chạy nhưng MySQL lỗi" | Xem mục *Lỗi hay gặp* trong `backend/README.md` |
| Console (F12) báo `blocked by CORS policy` | Kiểm tra `CORS_ORIGINS` trong `backend/.env`, sửa xong nhớ chạy lại backend |
| Menu/header không hiện | Sai `data-root` ở thẻ `<body>`, hoặc sai đường dẫn file JS. Mở F12 → Console để xem lỗi |
| Sửa code mà trang không đổi | Tải lại cứng: `Ctrl + F5` |
