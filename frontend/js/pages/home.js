const articles = NEWS_ARTICLES;

const newsGrid = document.getElementById("news-grid");
const searchInput = document.getElementById("search-input");
const emptyState = document.getElementById("empty-state");
let selectedCategory = "all";

const authNotice = new URLSearchParams(window.location.search).get("auth");
const authMessages = {
  anonymous: "Bạn cần đăng nhập để truy cập khu vực này.",
  expired: "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.",
  invalid: "Token không hợp lệ. Vui lòng đăng nhập lại.",
  forbidden: "Tài khoản của bạn không có quyền truy cập trang này.",
};
if (authNotice && authMessages[authNotice]) {
  showToast(authMessages[authNotice], "error");
  window.history.replaceState(null, "", window.location.pathname + window.location.hash);
}

function renderArticles() {
  const query = searchInput.value.trim().toLocaleLowerCase("vi");
  const visibleArticles = articles.filter((article) => {
    const matchesCategory = selectedCategory === "all" || article.category === selectedCategory;
    const searchableText = `${article.title} ${article.excerpt} ${article.category}`.toLocaleLowerCase("vi");
    return matchesCategory && searchableText.includes(query);
  });

  newsGrid.innerHTML = visibleArticles.map((article, index) => `
    <article class="news-card${index === 0 && selectedCategory === "all" && !query ? " is-featured" : ""}">
      <div class="news-image-wrap">
        <img class="news-image" src="${article.image}" alt="" loading="${index > 2 ? "lazy" : "eager"}">
        <span class="news-category">${escapeHtml(article.category)}</span>
      </div>
      <div class="news-card-content">
        <p class="news-meta">${escapeHtml(article.date)} <span aria-hidden="true">·</span> ${escapeHtml(article.readTime)}</p>
        <h3><a href="pages/article.html?id=${encodeURIComponent(article.id)}">${escapeHtml(article.title)}</a></h3>
        <p class="news-excerpt">${escapeHtml(article.excerpt)}</p>
        <div class="news-card-footer">
          <span class="news-author">${escapeHtml(article.author)}</span>
          <a class="story-link" href="pages/article.html?id=${encodeURIComponent(article.id)}">Đọc bài <span aria-hidden="true">→</span></a>
        </div>
      </div>
    </article>`).join("");
  emptyState.hidden = visibleArticles.length !== 0;
}

document.querySelectorAll(".filter-chip").forEach((button) => {
  button.addEventListener("click", () => {
    selectedCategory = button.dataset.category;
    document.querySelectorAll(".filter-chip").forEach((chip) => {
      const active = chip === button;
      chip.classList.toggle("is-active", active);
      chip.setAttribute("aria-pressed", String(active));
    });
    renderArticles();
  });
});

document.getElementById("search-form").addEventListener("submit", (event) => {
  event.preventDefault();
  renderArticles();
});
searchInput.addEventListener("input", renderArticles);

renderArticles();
