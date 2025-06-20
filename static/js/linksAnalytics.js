class LinksAnalytics {
  constructor() {
    this.linkId = null;
    this.title = document.querySelector(".title");
    this.shortKey = document.querySelector(".short-key");
    this.destination = document.querySelector(".destination");
    this.createDate = document.querySelector(".created-at > span");
    this.copyBtn = document.querySelector(".copy-btn");
    this.copyText = document.querySelector(".copy-text");
    this._copyTimeoutId = null;
    this.uuid = null;
    this.qrcodeBtn = document.querySelector(".generate-view");
    this.dropDownBtn = document.querySelector(".drop-down-btn");
    this.dropDown = document.querySelector(".drop-down");
    this.edit = document.querySelector(".edit");
    this.delete = document.querySelector(".delete");
    this.utmView = document.querySelector(".view-utm");
    this.utmContainerTrue = document.querySelector(".utm-container-true");
    this.utmContainerFalse = document.querySelector(".utm-container-false");
    if (this.dropDownBtn && this.edit && this.delete) {
      this.dropDownBtn.addEventListener("click", () => {
        this.clickDropDown();
      });
      this.edit.addEventListener("click", () => {
        this.clickUpdata();
      });
      this.delete.addEventListener("click", () => {
        this.clickDelete();
      });
    }
  }
  async createUtm() {
    let payload;
    const utmCampaign = document.querySelector("#utm-campaign");
    const utmSource = document.querySelector("#utm-source");
    const utmMedium = document.querySelector("#utm-medium");
    const utm_campaign = utmCampaign.value.trim() || null;
    const utm_source = utmSource.value.trim() || null;
    const utm_medium = utmMedium.value.trim() || null;
    console.log(utm_campaign, utm_source, utm_medium);
    if (utm_campaign || utm_source || utm_medium) {
      payload = {
        utm_campaign: utm_campaign,
        utm_source: utm_source,
        utm_medium: utm_medium,
      };
    } else {
      alert("UTM parameters cannot be empty.");
      return;
    }
    console.log(this.linkId);
    const response = await fetch(`/api/utm/${this.linkId}`, {
      headers: {
        "Content-Type": "application/json",
        credentials: "include",
      },

      method: "POST",
      body: JSON.stringify(payload),
    });
    const result = await response.json();

    if (result.ok) {
      alert("UTM params cteated succefully.");
      location.reload();
    }
  }
  generateOrView(qrcodeId) {
    if (!qrcodeId) {
      this.qrcodeBtn.textContent = "Generate Qrcode";
      this.qrcodeBtn.addEventListener("click", () => {
        if (confirm("Are you sure you want to create a new QR code?"))
          this.generateQrcode();
      });
    } else {
      this.qrcodeBtn.textContent = "View Qr code";
      this.qrcodeBtn.addEventListener("click", () => {
        location.href = `/qrcodes/${qrcodeId}`;
      });
    }
  }
  async generateQrcode() {
    const response = await fetch(`/api/qrcodes/${this.uuid}`, {
      credentials: "include",
      method: "POST",
    });
    const result = await response.json();
    if (result.ok) {
      location.href = `/qrcodes/${result.qrcodeId}`;
    }
  }
  clickDropDown() {
    this.dropDown.classList.toggle("display");
  }

  clickUpdata() {
    location.href = `/links/update?id=${this.uuid}&title=${this.title.textContent}&short_key=${this.shortKey.textContent}&destination=${this.destination.textContent}`;
  }
  async clickDelete() {
    if (confirm("Are you sure you wnat to delete it?")) {
      const response = await fetch(`/api/links/${this.uuid}`, {
        credentials: "include",
        method: "DELETE",
      });
      const data = await response.json();
      if (data.ok) {
        alert("Link deleted successfully.");
        location.href = "/links";
      } else {
        alert("刪除失敗請重新嘗試");
      }
    }
  }

  _addCopyEvent() {
    if (this.copyBtn) {
      this.copyBtn.addEventListener("click", () => {
        const url = this.shortKey.textContent;
        this._copyLink(url);
      });
    }
  }

  async _copyLink(url) {
    if (this._copyTimeoutId) {
      clearTimeout(this._copyTimeoutId);
    }
    await navigator.clipboard.writeText(url);
    this.copyText.textContent = "copied";
    this._copyTimeoutId = setTimeout(() => {
      this.copyText.textContent = "copy";
      this._copyTimeoutId = null;
    }, 1200);
  }
  async load() {
    const path = window.location.pathname;
    const uuid = path.split("/")[2];
    if (!uuid) return;

    try {
      const response = await fetch(`/api/links/${uuid}`, {
        credentials: "include",
      });
      if (!response.ok) throw new Error("載入失敗");
      const linkData = await response.json();
      if (linkData.data) {
        this.linkId = linkData.data.id;

        console.log(linkData.data);
        this.uuid = linkData.data.uuid;
        this.title.textContent = linkData.data.title;
        const shortCode = linkData.data.short_key
          ? linkData.data.short_key
          : linkData.data.uuid;

        this.shortKey.textContent = `https://s.ppluchuli.com/s/${shortCode}`;
        this.destination.textContent = linkData.data.target_url;
        this.destination.href = linkData.data.target_url;
        this.destination.target = "_blank";
        this.createDate.textContent = linkData.data.created_at;
        this._addCopyEvent();
        this.generateOrView(linkData.data.qrcode_id);

        this.utmView.addEventListener("click", () => {
          if (
            linkData.data.utm_campaign ||
            linkData.data.utm_source ||
            linkData.data.utm_medium
          ) {
            this.utmContainerTrue.classList.toggle("display");
            const campaignText = document.querySelector(".campaign-text");
            const sourceText = document.querySelector(".source-text");
            const mediumText = document.querySelector(".medium-text");
            campaignText.textContent = linkData.data.utm_campaign;
            sourceText.textContent = linkData.data.utm_source;
            mediumText.textContent = linkData.data.utm_medium;
          } else {
            this.utmContainerFalse.classList.toggle("display");

            const utmBtn = document.querySelector(".utmBtn");
            utmBtn.addEventListener("click", () => {
              this.createUtm();
            });
          }
        });
      }
    } catch (e) {
      console.error("取得連結資料失敗", err);
      this.titleElem.textContent = "載入失敗";
    }
  }

  createReferreralTable() {
    pass;
  }
}

const analytic = new LinksAnalytics();
analytic.load();
