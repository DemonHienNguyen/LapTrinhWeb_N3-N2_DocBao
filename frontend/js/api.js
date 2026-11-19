// Module gọi API dùng fetch: mọi trang dùng chung và tự đính kèm JWT nếu có.
//
// Cách dùng (trong các file js/pages/*.js):
//   const items = await api.get("/items");
//   const items = await api.get("/items", { q: "com" });          // -> /items?q=com
//   const created = await api.post("/items", { name: "Trà đá", price: 5000 });
//   await api.put("/items/1", { name: "Tên mới" });
//   await api.delete("/items/1");
//
// Các hàm trả về thẳng dữ liệu JSON (đã lấy sẵn response.data).
// Nếu lỗi, hàm sẽ throw ApiError -> bắt bằng try/catch và hiện error.message cho người dùng.

class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = "ApiError";
    this.status = status; // mã HTTP: 404, 422, 500... (0 = không gọi được server)
    this.data = data; // nội dung lỗi gốc server trả về
  }
}

function getErrorMessage(data, status) {
  if (status === 401) return "Phiên đăng nhập đã hết hạn hoặc không hợp lệ. Vui lòng đăng nhập lại.";
  if (status === 403) return "Bạn không có quyền thực hiện thao tác này.";
  if (data && typeof data.detail === "string") return data.detail;
  if (data && Array.isArray(data.detail)) {
    return data.detail.map((error) => {
      const location = Array.isArray(error.loc) ? error.loc[error.loc.length - 1] : "Dữ liệu";
      return `${location}: ${error.msg}`;
    }).join("; ");
  }
  return `Lỗi ${status}`;
}

function buildUrl(path, params) {
  const url = new URL(`${CONFIG.API_BASE_URL.replace(/\/$/, "")}/${path.replace(/^\//, "")}`);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value === undefined || value === null) return;
      if (Array.isArray(value)) {
        value.forEach((entry) => url.searchParams.append(key, entry));
      } else {
        url.searchParams.set(key, value);
      }
    });
  }
  return url.toString();
}

async function request(path, { method = "GET", params, body, headers = {}, ...options } = {}) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), CONFIG.API_TIMEOUT_MS);
  const requestHeaders = new Headers(headers);
  const token = localStorage.getItem(CONFIG.AUTH_TOKEN_KEY);
  if (token) requestHeaders.set("Authorization", `Bearer ${token}`);
  if (body !== undefined && !requestHeaders.has("Content-Type")) {
    requestHeaders.set("Content-Type", "application/json");
  }
  requestHeaders.set("Accept", "application/json");

  let response;
  try {
    response = await fetch(buildUrl(path, params), {
      ...options,
      method,
      headers: requestHeaders,
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: controller.signal,
    });
  } catch (error) {
    const message = error.name === "AbortError"
      ? "Yêu cầu quá thời gian chờ. Vui lòng thử lại."
      : "Không kết nối được backend. Backend đã chạy chưa? Kiểm tra CONFIG.API_BASE_URL.";
    throw new ApiError(message, 0);
  } finally {
    clearTimeout(timeoutId);
  }

  let data = null;
  if (response.status !== 204) {
    const responseText = await response.text();
    if (responseText) {
      try {
        data = JSON.parse(responseText);
      } catch {
        data = { detail: responseText };
      }
    }
  }

  if (!response.ok) {
    if (response.status === 401 && token) {
      localStorage.removeItem(CONFIG.AUTH_TOKEN_KEY);
    }
    throw new ApiError(getErrorMessage(data, response.status), response.status, data);
  }
  return data;
}

const api = {
  request,
  get: (path, params) => request(path, { params }),
  post: (path, body) => request(path, { method: "POST", body }),
  put: (path, body) => request(path, { method: "PUT", body }),
  delete: (path) => request(path, { method: "DELETE" }),
};
