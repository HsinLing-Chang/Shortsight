(function () {
  const token = localStorage.getItem("access_token");
  if (!token) {
    window.location.replace("/signin");
    return;
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.body.style.visibility = "visible";
    const loginState = document.querySelector(".login-state");
    loginState.textContent = "Sign Out";
  });
})();
