// Layout chung: tự chèn header (menu) và footer vào mọi trang.
//
// Mỗi trang cần có:  <body data-root="./">   (trang ở thư mục gốc)
//              hoặc  <body data-root="../">  (trang trong thư mục pages/)
// và hai thẻ rỗng:   <header id="app-header"></header> ... <footer id="app-footer"></footer>

// Thêm trang mới vào menu: thêm 1 dòng vào mảng này (đường dẫn tính từ thư mục frontend/)
const MENU = [
  { href: "index.html", label: "Trang chủ" },
  { href: "pages/items.html", label: "Demo API" },
  { href: "pages/login.html", label: "Đăng nhập", visibility: "anonymous" },
  { href: "pages/register.html", label: "Đăng ký", visibility: "anonymous" },
  { href: "pages/profile.html", label: "Trang cá nhân", visibility: "authenticated", roles: ["member", "admin"] },
  { href: "pages/admin.html", label: "Quản trị", visibility: "authenticated", roles: ["admin"] },
];

function renderLayout() {
  const root = document.body.dataset.root || "./";
  const currentPath = window.location.pathname;
  const session = AUTH.getSession();
  const isAuthenticated = session.status === "authenticated";

  const links = MENU
    .filter((item) => {
      if (item.visibility === "anonymous" && isAuthenticated) return false;
      if (item.visibility === "authenticated" && !isAuthenticated) return false;
      return !item.roles || AUTH.hasAnyRole(item.roles);
    })
    .map((item) => {
      const isActive = currentPath.endsWith("/" + item.href) ||
        (item.href === "index.html" && currentPath.endsWith("/"));
      return `<a href="${root}${item.href}" class="${isActive ? "active" : ""}"${isActive ? ' aria-current="page"' : ""}>${item.label}</a>`;
    }).join("");
  const logoutButton = isAuthenticated
    ? '<button class="nav-logout" type="button" data-header-logout>Đăng xuất</button>'
    : "";

  document.getElementById("app-header").innerHTML = `
    <div class="container header-inner">
      <a href="${root}index.html" class="brand">
        <img src="${root}assets/images/logo.svg" alt="" width="28" height="28">
        <span>${CONFIG.APP_NAME}</span>
      </a>
      <button class="nav-toggle" type="button" aria-controls="primary-navigation"
        aria-expanded="false" aria-label="Mở menu">
        <span></span><span></span><span></span>
      </button>
      <div class="header-actions">
        <nav id="primary-navigation" class="nav" aria-label="Điều hướng chính">${links}${logoutButton}</nav>
      </div>
    </div>`;

  document.getElementById("app-footer").innerHTML = `
    <div class="container footer-inner">
      <a href="${root}index.html" class="footer-brand">${CONFIG.APP_NAME}</a>
      <span>© ${new Date().getFullYear()} HN-KS25-CNTT1 · Base code thực tập doanh nghiệp</span>
    </div>`;

  const toggle = document.querySelector(".nav-toggle");
  const navigation = document.getElementById("primary-navigation");
  const headerActions = document.querySelector(".header-actions");
  toggle.addEventListener("click", () => {
    const isExpanded = toggle.getAttribute("aria-expanded") === "true";
    toggle.setAttribute("aria-expanded", String(!isExpanded));
    toggle.setAttribute("aria-label", isExpanded ? "Mở menu" : "Đóng menu");
    headerActions.classList.toggle("is-open", !isExpanded);
  });
  headerActions.addEventListener("click", (event) => {
    if (event.target.closest("[data-header-logout]")) {
      AUTH.logout();
      return;
    }
    if (event.target.closest("a")) {
      headerActions.classList.remove("is-open");
      toggle.setAttribute("aria-expanded", "false");
      toggle.setAttribute("aria-label", "Mở menu");
    }
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      headerActions.classList.remove("is-open");
      toggle.setAttribute("aria-expanded", "false");
      toggle.setAttribute("aria-label", "Mở menu");
    }
  });
}

renderLayout();
