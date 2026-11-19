// Các hàm tiện ích dùng chung cho nhiều trang.

// Chống XSS: luôn dùng hàm này khi chèn dữ liệu người dùng nhập vào innerHTML
function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value ?? "";
  return div.innerHTML;
}

// 45000 -> "45.000 ₫"
function formatMoney(value) {
  return Number(value).toLocaleString("vi-VN") + " ₫";
}

// "2026-11-04T09:30:00" -> "09:30 4/11/2026"
function formatDateTime(value) {
  const d = new Date(value);
  return d.toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" }) + " " +
    d.toLocaleDateString("vi-VN");
}

// Hiện thông báo trong live region dùng chung. type: success | error | info | warning
function showToast(message, type = "success") {
  const allowedTypes = ["success", "error", "info", "warning"];
  const toastType = allowedTypes.includes(type) ? type : "info";
  let container = document.getElementById("toast-container");

  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    container.className = "toast-container";
    container.setAttribute("aria-live", "polite");
    container.setAttribute("aria-relevant", "additions");
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `toast toast-${toastType}`;
  toast.setAttribute("role", toastType === "error" ? "alert" : "status");

  const text = document.createElement("span");
  text.textContent = message;
  const closeButton = document.createElement("button");
  closeButton.className = "toast-close";
  closeButton.type = "button";
  closeButton.setAttribute("aria-label", "Đóng thông báo");
  closeButton.textContent = "×";
  closeButton.addEventListener("click", () => toast.remove());

  toast.append(text, closeButton);
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}
