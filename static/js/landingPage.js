class LangingPage {
  constructor() {
    this.signInBtn = document.querySelector(".sign-up-btn");
    this.startBtn = document.querySelector(".start-btn");
    this.isLogin();
    this.signInBtn.addEventListener("click", () => {
      location.href = "/signin";
    });
    this.startBtn.addEventListener("click", () => {
      location.href = "/signin";
    });
  }
  async isLogin() {
    const responese = await fetch("/api/user/status");
    const result = await responese.json();
    if (!result.ok) {
      document.body.style.visibility = "visible";
      return;
    }

    window.location.replace("/home");
  }
}
new LangingPage();
