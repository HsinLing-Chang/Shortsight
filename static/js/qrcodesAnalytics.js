class QrcodesAnalytics {
  constructor() {
    this.uuid = null;
    if (!window.location.pathname.startsWith("/qrcodes/")) {
      return;
    }
    this.DropDown = document.querySelector(".drop-down");
    this.downloadImage = document.querySelector(".download-image");
    if (this.DropDown && this.downloadImage) {
      this.addClickEvent(this.DropDown);
      this.addClickEvent(this.downloadImage);
      this.getQrocdeInfo();
    }

    this.title = document.querySelector(".qr-title");
    this.destination = document.querySelector(".qr-destination");
    this.qrcodeImg = document.querySelector(".qr-img");
    this.createdAt = document.querySelector(".qr-create-at");
    this.shortUrl = document.querySelector(".qr-short-key");
    this.viewShortLink = document.querySelector(".view-detail");

    this.deleteBtn = document.querySelector(".delete-btn");
    this.download = document.querySelector(".download");
  }
  async getQrocdeInfo() {
    const qrcode_id = window.location.pathname.split("/")[2];
    const response = await fetch(`/api/qrcodes/${qrcode_id}`, {
      credentials: "include",
    });
    const qrocdeInfo = await response.json();
    // console.log(qrocdeInfo);
    if (qrocdeInfo.ok) {
      // console.log(qrocdeInfo);
      this.uuid = qrocdeInfo.data.uuid;
      this.title.textContent = qrocdeInfo.data.title;
      this.destination.textContent = qrocdeInfo.data.target_url;
      this.destination.href = qrocdeInfo.data.target_url;
      this.destination.target = "_blank";
      this.qrcodeImg.src = qrocdeInfo.data.qr_code.image_path;
      this.qrcodeImg.href = qrocdeInfo.data.qr_code.image_path;
      // this.download.href = qrocdeInfo.data.qr_code.image_path;
      // this.download.download = `qrcodes.PNG`;
      // this.download.click();
      this.createdAt.textContent = qrocdeInfo.data.qr_code.created_at;
      const shortKey = `https://s.ppluchuli.com/s/${
        qrocdeInfo.data.shortKey || qrocdeInfo.data.uuid
      }`;
      this.shortUrl.textContent = shortKey;
      this.shortUrl.href = shortKey;
      // this.shortUrl.target = "_blank";
      this.viewShortLink.addEventListener("click", () => {
        this.getShortLink(qrocdeInfo.data.uuid);
      });
      if (this.deleteBtn) {
        this.deleteBtn.addEventListener("click", () => {
          if (confirm("Are you sure you want to delete this?")) {
            this.deleteQrcode(qrocdeInfo.data.qr_code.id);
          }
        });
      }
    }
  }

  getShortLink(uuid) {
    location.href = `/links/${uuid}`;
  }
  async downloadQRcode(uuid, imgFormat) {
    const response = await fetch(`/api/qrcode/${uuid}/${imgFormat}`, {
      credentials: "include",
    });
    // const result = await response.json();
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${uuid}.${imgFormat}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url); // 清理
    // if (result.ok) {
    //   const link = document.createElement("a");
    //   link.href = result.data;
    //   link.download = "my_qrcode.png";
    //   document.body.appendChild(link);
    //   link.click();
    //   document.body.removeChild(link);
    // }
  }
  addClickEvent(btn) {
    const more = btn.querySelector(".more");
    if (!more) return;

    // 點擊按鈕時
    btn.addEventListener("click", (e) => {
      e.stopPropagation();

      // 收起所有其他 .more
      document.querySelectorAll(".more.display").forEach((el) => {
        if (el !== more) el.classList.remove("display");
      });
      const jpegBtn = document.querySelector(".jpeg");
      const pngBtn = document.querySelector(".png");
      jpegBtn.addEventListener("click", () => {
        more.classList.remove("display");
        this.downloadQRcode(this.uuid, "jpeg");
      });
      pngBtn.addEventListener("click", () => {
        more.classList.remove("display");
        this.downloadQRcode(this.uuid, "png");
      });
      // 切換自己
      more.classList.toggle("display");
    });
    more.addEventListener("click", (e) => {
      e.stopPropagation();
    });

    // 點擊畫面其他地方時，全部收起
    if (!document._moreClickEventBound) {
      document.addEventListener("click", () => {
        document.querySelectorAll(".more.display").forEach((el) => {
          el.classList.remove("display");
        });
      });
      document._moreClickEventBound = true;
    }
  }
  async deleteQrcode(id) {
    const responese = await fetch(`/api/qrcodes/${id}`, {
      credentials: "include",
      method: "DELETE",
    });
    const result = await responese.json();
    if (result.ok) {
      alert("The QR code was deleted successfully.");
      location.href = "/qrcodes";
    }
  }
}

new QrcodesAnalytics();
