class CreateLink {
  constructor() {
    this.destination = document.querySelector("#destination");
    this.title = document.querySelector("#title");
    this.customUrl = document.querySelector("#custom-url");
    this.errorMsg = document.querySelector("#error");
    this.form = document.querySelector("#link-form");
    if (this.form) {
      this.form.addEventListener("submit", async (e) => {
        e.preventDefault();
        await this.createNewLink();
      });
    }
  }
  getPayload() {
    return {
      title: this.title.value.trim(),
      short_key: this.customUrl.value.trim() || undefined, //後端無此欄位
      target_url: this.destination.value.trim(),
    };
  }
  validate() {
    if (!this.form.reportValidity()) {
      return false;
    }
    return true;
  }
  async createNewLink() {
    try {
      if (!this.validate()) throw Error("Form cannot be empty.");
      const payload = this.getPayload();
      const token = localStorage.getItem("access_token");
      const response = await fetch("/api/links/shorten", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (data.ok) {
        window.location.href = "/links";
      } else if (data.error) {
        this.errorMsg.textContent = data.message;
        this.errorMsg.style.color = "red";
        throw new Error(`Server error: ${data.message}`);
      }
    } catch (e) {
      console.log(e);
      return;
    }
  }
}

export default CreateLink;
