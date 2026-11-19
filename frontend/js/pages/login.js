const loginForm = document.getElementById("login-form");
const loginError = document.getElementById("login-error");
const loginButton = document.getElementById("login-submit");

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  loginError.hidden = true;
  loginButton.disabled = true;

  try {
    const result = await api.post("/auth/login", {
      email: loginForm.elements.namedItem("email").value.trim(),
      password: loginForm.elements.namedItem("password").value,
    });
    const session = AUTH.setToken(result.access_token);
    const destination = AUTH.hasAnyRole(["admin"], session.payload) ? "admin.html" : "profile.html";
    window.location.replace(destination);
  } catch (error) {
    loginError.textContent = error.message;
    loginError.hidden = false;
  } finally {
    loginButton.disabled = false;
  }
});
