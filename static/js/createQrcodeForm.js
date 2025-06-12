class CreateQrcodeForm {
  constructor() {
    if (!location.pathname.startsWith("/qrcodes/create")) {
      return;
    }
    this.utmCheckBox = document.querySelector(".check-box");
    this.utmForm = document.querySelector(".utm-form");
    this.utmHeader = document.querySelector(".UTM-header");
    this.errorMsg = document.querySelector("#qr-error");
    this.loader = document.querySelector(".loader");
    if (this.utmCheckBox) {
      this.utmCheckBox.addEventListener("change", () => {
        this.isUtm();
      });
      this.title = document.querySelector("#title");
      this.destination = document.querySelector("#destination");
      this.shortKey = document.querySelector("#custom-url");

      this.sourceInput = document.querySelector(".utm-source");
      this.mediumInput = document.querySelector(".utm-medium");
      this.campaignInput = document.querySelector(".utm-campaign");
      this.contentInput = document.querySelector(".utm-content");
      this.termInput = document.querySelector(".utm-term");

      this.createQrcodeBtn = document.querySelector(".qr-create-btn");
      if (this.createQrcodeBtn) {
        this.createQrcodeBtn.addEventListener("click", (e) => {
          e.preventDefault();
          this.createNewQrocde();
        });
      }
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
      title: this.title.value.trim(),
      target_url: this.destination.value.trim(),
      short_key: this.shortKey.value.trim() || null,
      utm_params: {
        utm_source: this.sourceInput.value.trim() || null,
        utm_medium: this.mediumInput.value.trim() || null,
        utm_campaign: this.campaignInput.value.trim() || null,
        utm_term: this.contentInput.value.trim() || null,
        utm_content: this.termInput.value.trim() || null,
      },
    };
  }
  async createNewQrocde() {
    const payload = this.getPayload();
    try {
      this.loader.classList.add("visible");
      const responese = await fetch("/api/qrcodes", {
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        method: "POST",
        body: JSON.stringify(payload),
      });
      const data = await responese.json();
      if (data.ok) {
        location.href = "/qrcodes";
      } else {
        throw new Error(data.message);
      }
    } catch (e) {
      this.errorMsg.textContent = e.message;
      this.errorMsg.style.color = "red";
      this.loader.classList.remove("visible");
    }
  }
}
new CreateQrcodeForm();
