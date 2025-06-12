class SignUp {
  constructor() {
    this.username = document.querySelector(".username");
    this.email = document.querySelector(".email");
    this.password = document.querySelector(".password");
    this.confirmPassword = document.querySelector(".confirm-password");
    this.signUpMsg = document.querySelector("#signup-msg");
    this.form = document.querySelector(".sign-up-form");
    if (this.form) {
      this.form.addEventListener("submit", async (e) => {
        e.preventDefault();
        await this.signUp();
      });
    }
  }
  _verifyPassword() {
    if (!this.password || !this.confirmPassword) return false;
    return this.password.value === this.confirmPassword.value;
  }
  getPayload() {
    return {
      username: this.username.value.trim(),
      email: this.email.value.trim(),
      password: this.password.value.trim(),
    };
  }
  async signUp() {
    try {
      if (!this._verifyPassword()) {
        throw new Error("Passwords do not match.");
      }

      const payload = this.getPayload();
      const response = await fetch("/api/user/signup", {
        headers: {
          "Content-Type": "application/json",
        },
        method: "POST",
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (data.ok) {
        this.signUpMsg.textContent = "Signed up successfully.";
        this.signUpMsg.style.color = "green";
      }
      if (data.error) {
        throw new Error(data.message);
      }
    } catch (e) {
      this.signUpMsg.textContent = e.message;
      this.signUpMsg.style.color = "red";
      console.log(e);
    }
  }
}
// export default SignUp;
new SignUp();
