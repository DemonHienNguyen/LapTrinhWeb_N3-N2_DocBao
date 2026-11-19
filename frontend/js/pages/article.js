const articleId = new URLSearchParams(window.location.search).get("id");
const article = NEWS_ARTICLES.find((item) => item.id === articleId);

if (article) {
  document.title = `${article.title} | Tin Tức 24h`;
  document.getElementById("article-category").textContent = article.category;
  document.getElementById("article-title").textContent = article.title;
  document.getElementById("article-byline").textContent =
    `${article.author} · ${article.date} · ${article.readTime}`;
  document.getElementById("article-cover").src = article.image;
  document.getElementById("article-cover").alt = article.title;
  document.getElementById("article-excerpt").textContent = article.excerpt;
  document.getElementById("article-body").innerHTML = article.body
    .map((paragraph) => `<p>${escapeHtml(paragraph)}</p>`)
    .join("");
} else {
  document.getElementById("article-masthead").hidden = true;
  document.getElementById("article-cover-wrap").hidden = true;
  document.getElementById("article-content").hidden = true;
  document.getElementById("article-not-found").hidden = false;
}
