(async function () {
  const responese = await fetch("/api/user/check_login");
  const result = await responese.json();
  if (!result.ok) {
    window.location.replace("/signin");
    return;
  }
  document.body.style.visibility = "visible";
  const loginState = document.querySelector(".login-state");
  loginState.textContent = "Sign Out";
})();
