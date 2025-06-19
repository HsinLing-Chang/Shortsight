class SignIn {
  constructor() {
    this.email = document.querySelector(".email");
    this.password = document.querySelector(".password");
    this.form = document.querySelector(".sign-in-form");
    this.signInMsg = document.querySelector("#signin-msg");
    this.email.value = "demo@example.com";
    this.password.value = "demo";
    if (this.form) {
      this.form.addEventListener("submit", async (e) => {
        e.preventDefault();
        await this.signIn();
      });
    }
  }
  validate() {
    if (!this.form.reportValidity()) {
      return false;
    }
    return true;
  }
  getPayload() {
    return {
      email: this.email.value.trim(),
      password: this.password.value.trim(),
    };
  }
  async signIn() {
    try {
      if (!this.validate()) throw Error("Form cannot be empty.");
      const payload = this.getPayload();
      const response = await fetch("/api/user/signin", {
        headers: {
          "Content-Type": "application/json",
        },
        method: "POST",
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (data.ok) {
        // const token = data.token;
        // localStorage.setItem("access_token", token);
        window.location.href = "/";
      } else if (data.error) {
        throw Error(data.message);
      }
    } catch (e) {
      this.signInMsg.textContent = e.message;
      this.signInMsg.style.color = "red";
      return;
    }
  }
}
new SignIn();
