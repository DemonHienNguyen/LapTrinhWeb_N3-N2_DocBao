const profileDashboard = document.getElementById("profile-dashboard");

if (AUTH.requireAnyRole(["member", "admin"])) {
  const { payload } = AUTH.getSession();
  const displayName = payload.name || payload.full_name || payload.username || payload.sub || "Thành viên";
  const role = AUTH.hasAnyRole(["admin"], payload) ? "Quản trị viên" : "Thành viên";

  profileDashboard.hidden = false;
  document.getElementById("profile-name").textContent = displayName;
  document.getElementById("profile-name-detail").textContent = displayName;
  document.getElementById("profile-email").textContent = payload.email || "Chưa có trong token";
  document.getElementById("profile-subject").textContent = payload.sub || "Chưa có trong token";
  document.getElementById("profile-role").textContent = role;
  document.getElementById("profile-admin-link").hidden = role !== "Quản trị viên";
  document.querySelector("[data-logout]").addEventListener("click", AUTH.logout);
}
