class QrcodeCard {
  constructor() {
    this.qrcodeCardContainer = document.querySelector(".qrcode-card-container");

    this.qrocdeInfo = [];
    if (this.qrcodeCardContainer) {
      this.getCardInfo();
    }
  }

  getQrcodeDetail(id) {
    location.href = `/qrcodes/${id}`;
  }

  async getCardInfo() {
    const response = await fetch("/api/qrcodes", {
      credentials: "include",
      method: "GET",
    });
    const data = await response.json();
    try {
      if (data.ok) {
        // console.log(data);
        this.qrocdeInfo = data.data;
        this.cardGenerator();
      }
    } catch (e) {
      console.log(e);
    }
  }
  createElement(tag, className = [], textContent = "") {
    const element = document.createElement(tag);
    if (typeof className == "string" && className) {
      element.classList.add(className);
    } else if (Array.isArray(className)) {
      element.classList.add(...className);
    }
    if (textContent) element.textContent = textContent;
    return element;
  }

  cardGenerator() {
    this.qrocdeInfo.forEach((data) => {
      const card = this.createElement("div", ["qrcode-card", "mg-b2"]);

      // 圖片區塊
      const imgContainer = this.createElement("div", [
        "qr-img-container",
        "mg-r3",
      ]);
      const img = document.createElement("img");
      img.src = data.qr_code.image_path;
      imgContainer.appendChild(img);

      // 卡片內容
      const cardContent = this.createElement("div", "card-content");

      // content-top
      const contentTop = this.createElement("div", "content-top");

      // top-info
      const topInfo = this.createElement("div", "top-info");
      const title = this.createElement("h2", "mg-b05", data.title);
      const type = this.createElement("p", "mg-b05", "website");
      topInfo.append(title, type);

      // other-function
      const otherFunc = this.createElement("div", "other-fucntion");

      // drop-down 功能
      const dropDown = this.createElement("div", ["drop-down", "icon"]);
      // caret icon
      const icon = this.createElement("i", ["fa-solid", "fa-caret-down"]);
      dropDown.appendChild(icon);

      // dropdown menu container
      const more = this.createElement("div", "more");

      // menu items
      const editItem = this.createElement("div", [], "Edit");
      const deleteItem = this.createElement("div", [], "Delete");
      // delete 事件監聽
      deleteItem.addEventListener("click", () => {
        if (confirm("Are you sure you want to delete this?")) {
          this.deleteQrcode(data.qr_code.id);
        }
      });
      // 組合
      more.appendChild(editItem);
      more.appendChild(deleteItem);
      dropDown.appendChild(more);
      //
      //   dropDown.innerHTML = `
      //   <i class="fa-solid fa-caret-down"></i>
      //   <div class="more">
      //     <div>Edit</div>
      //     <div>Delete</div>
      //   </div>
      // `;

      // download-image 功能
      const download = this.createElement("div", ["download-image", "icon"]);
      download.innerHTML = `
      <i class="fa-solid fa-download"></i>
      <div class="more">
        <div>Download JPEG</div>
        <div>Download PNG</div>
        <div>Download SVG</div>
      </div>
    `;

      // view-detail 功能
      const viewDetail = this.createElement("div", ["view-detail", "pd-1"]);
      viewDetail.innerHTML = `
      <i class="fa-solid fa-chart-simple mg-r1"></i>
      <span> View Detail</span>
    `;
      this.addClickEvent(dropDown);
      this.addClickEvent(download);
      viewDetail.addEventListener("click", () => {
        this.getQrcodeDetail(data.qr_code.id);
      });

      otherFunc.append(dropDown, download, viewDetail);
      contentTop.append(topInfo, otherFunc);

      // content-bottom
      const contentBottom = this.createElement("div", "content-bottom");

      const linkData = this.createElement("div", "link-data");
      const arrorIcon = this.createElement("i", [
        "fa-solid",
        "fa-arrow-up-right-from-square",
        "mg-r05",
      ]);
      const a = document.createElement("a");
      a.href = data.target_url;
      a.target = "_blank";
      a.textContent = data.target_url;
      linkData.append(arrorIcon, a);

      const buttonInfo = this.createElement("div", ["botton-info", "mg-t1"]);

      const shortLink = this.createElement("div", ["short-link", "mg-r1"]);
      shortLink.innerHTML = `
      <i class="fa-solid fa-paperclip mg-r05"></i>
      <p>https://s.ppluchuli.com/s/${data.short_key || data.uuid}</p>
    `;

      const createdAT = this.createElement("div", "created-at");
      createdAT.innerHTML = `
      <i class="fa-solid fa-calendar mg-r05"></i>
       <p>${data.created_at.split(" ")[0]}</p>
      `;
      buttonInfo.append(shortLink, createdAT);

      contentBottom.append(linkData, buttonInfo);

      // 完整組裝
      cardContent.append(contentTop, contentBottom);
      card.append(imgContainer, cardContent);
      this.qrcodeCardContainer.appendChild(card);
    });
  }
  //   addclickEvent(btn) {
  //     const more = btn.querySelector(".more");

  //     btn.addEventListener("click", (e) => {
  //       e.stopPropagation(); // 阻止冒泡，不會觸發 document 的 click
  //       more.classList.toggle("display");
  //     });

  //     // 點擊其他地方時，關閉 .more
  //     document.addEventListener("click", (e) => {
  //       if (!btn.contains(e.target)) {
  //         more.classList.remove("display");
  //       }
  //     });
  //     //   more.classList.toggle("display");
  //   }
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
      document._moreClickEventBound = true; // 避免重複綁定
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
      location.reload();
    }
  }
}

export default QrcodeCard;
