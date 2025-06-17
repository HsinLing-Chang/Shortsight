class CreateLink {
  constructor() {
    if (!location.pathname.startsWith("/links/create")) {
      return;
    }
    this.destination = document.querySelector("#destination");
    this.title = document.querySelector("#title");
    this.customUrl = document.querySelector("#custom-url");

    this.utmForm = document.querySelector(".utm-form");
    this.utmHeader = document.querySelector(".UTM-header");
    this.sourceInput = document.querySelector(".utm-source");
    this.mediumInput = document.querySelector(".utm-medium");
    this.campaignInput = document.querySelector(".utm-campaign");
    this.contentInput = document.querySelector(".utm-content");
    this.termInput = document.querySelector(".utm-term");

    this.utmCheckBox = document.querySelector(".check-box");
    this.loader = document.querySelector(".loader");
    this.errorMsg = document.querySelector("#error");
    this.form = document.querySelector("#link-form");
    if (this.form) {
      this.form.addEventListener("submit", async (e) => {
        e.preventDefault();
        await this.createNewLink();
      });
    }
    if (this.utmCheckBox) {
      this.utmCheckBox.addEventListener("change", () => {
        this.isUtm();
      });
    }
  }
  isUtm() {
    if (this.utmCheckBox.checked) {
      this.utmForm.classList.add("display");
      this.utmHeader.classList.add("mg-b2");
      this.errorMsg.textContent = "";
    } else {
      this.utmForm.classList.remove("display");
      this.utmHeader.classList.remove("mg-b2");
      this.errorMsg.textContent = "";
    }
  }

  getPayload() {
    return {
      title:
        this.title.value.trim() === "" ? "Untitled" : this.title.value.trim(),
      short_key: this.customUrl.value.trim() || undefined, //後端無此欄位
      target_url: this.destination.value.trim(),
      utm_params: {
        utm_source: this.sourceInput.value.trim() || null,
        utm_medium: this.mediumInput.value.trim() || null,
        utm_campaign: this.campaignInput.value.trim() || null,
        // utm_term: this.contentInput.value.trim() || null,
        // utm_content: this.termInput.value.trim() || null,
      },
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
      this.loader.classList.add("visible");
      const payload = this.getPayload();
      console.log(payload.title);
      // const token = localStorage.getItem("access_token");
      const response = await fetch("/api/links/shorten", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          credentials: "include",
        },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (data.ok) {
        window.location.href = "/links";
      } else if (data.error) {
        throw new Error(data.message);
      }
    } catch (e) {
      this.errorMsg.textContent = e.message;
      this.errorMsg.style.color = "red";
      this.loader.classList.remove("visible");
    }
  }
}

new CreateLink();
