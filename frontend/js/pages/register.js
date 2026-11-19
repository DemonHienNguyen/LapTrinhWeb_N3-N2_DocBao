const registerForm = document.getElementById("register-form");
const registerError = document.getElementById("register-error");
const registerButton = document.getElementById("register-submit");
const registerPassword = document.getElementById("register-password");
const confirmPassword = document.getElementById("register-confirm-password");

registerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  registerError.hidden = true;
  if (registerPassword.value !== confirmPassword.value) {
    registerError.textContent = "Mật khẩu xác nhận không khớp.";
    registerError.hidden = false;
    confirmPassword.focus();
    return;
  }

  registerButton.disabled = true;
  try {
    const result = await api.post("/auth/register", {
      name: registerForm.elements.namedItem("name").value.trim(),
      email: registerForm.elements.namedItem("email").value.trim(),
      password: registerPassword.value,
    });
    AUTH.setToken(result.access_token);
    window.location.replace("profile.html");
  } catch (error) {
    registerError.textContent = error.message;
    registerError.hidden = false;
  } finally {
    registerButton.disabled = false;
  }
});
