// async function getLinksInfo() {
//   const path = window.location.pathname;
//   const uuid = path.split("/")[2];
//   if (!uuid) return;
//   const token = localStorage.getItem("access_token");
//   const response = await fetch(`/api/links/${uuid}`, {
//     headers: {
//       credentials: "include",
//     },
//   });
//   const linkData = await response.json();
//   if (linkData.data) {
//     const title = document.querySelector(".title");
//     const shortKey = document.querySelector(".short-key");
//     const destination = document.querySelector(".destination");
//     const createDate = document.querySelector(".created-at > span");
//     title.textContent = linkData.data.title;

//     const shortCode = linkData.data.short_key
//       ? linkData.data.short_key
//       : linkData.data.uuid;

//     shortKey.textContent = `https://s.ppluchuli.com/s/${shortCode}`;
//     destination.textContent = linkData.data.target_url;
//     destination.href = linkData.data.target_url;
//     destination.target = "_blank";
//     createDate.textContent = linkData.data.created_at;
//   }
// }
// getLinksInfo();

class LinksAnalytics {
  constructor() {
    this.title = document.querySelector(".title");
    this.shortKey = document.querySelector(".short-key");
    this.destination = document.querySelector(".destination");
    this.createDate = document.querySelector(".created-at > span");
    this.copyBtn = document.querySelector(".copy-btn");
    this.copyText = document.querySelector(".copy-text");
    this._copyTimeoutId = null;
    this.uuid = null;
    this.dropDownBtn = document.querySelector(".drop-down-btn");
    this.dropDown = document.querySelector(".drop-down");
    this.edit = document.querySelector(".edit");
    this.delete = document.querySelector(".delete");
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
      }
    } catch (e) {
      console.error("取得連結資料失敗", err);
      this.titleElem.textContent = "載入失敗";
    }
  }
}

const analytic = new LinksAnalytics();
analytic.load();
