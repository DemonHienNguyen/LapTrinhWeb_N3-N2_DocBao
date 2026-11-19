const adminDashboard = document.getElementById("admin-dashboard");

if (AUTH.requireAnyRole(["admin"])) {
  const { payload } = AUTH.getSession();
  adminDashboard.hidden = false;
  document.getElementById("admin-name").textContent =
    payload.name || payload.full_name || payload.username || payload.sub || "Quản trị viên";
  document.querySelector("[data-logout]").addEventListener("click", AUTH.logout);
}
