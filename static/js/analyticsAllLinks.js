class Analytics {
  constructor() {
    this.links = document.querySelector(".links-display");
    this.allItems = null;
    this.currentPage = 1;
    this.pageSize = 5;
    this.getLinkPerformance();
  }
  createElement(tag, className = [], textContent = "") {
    const element = document.createElement(tag);
    if (typeof className == "string" && className) {
      element.classList.add(className);
    } else if (Array.isArray(className)) {
      element.classList.add(...className);
    }
    if (textContent !== null && textContent !== undefined) {
      element.textContent = textContent;
    }
    return element;
  }
  async getLinkPerformance() {
    const response = await fetch("/api/report/performance", {
      credentials: "include",
    });
    const linkPerformance = await response.json();
    // console.log(linkPerformance);
    if (linkPerformance.ok) {
      this.allItems = linkPerformance.data.items;
      this.currentPage = 1;
      this.pageSize = 5;
      this.renderPage();
      //   linkPerformance.data.items.forEach((item) => {
      //     this.createLinkRow(item);
      //   });
    }
  }
  renderPage() {
    const container = document.querySelector(".links-display");
    container.innerHTML = "";

    const start = (this.currentPage - 1) * this.pageSize;
    const end = start + this.pageSize;
    const pageItems = this.allItems.slice(start, end);

    pageItems.forEach((item) => {
      this.createLinkRow(item);
    });
    if (this.allItems.length > 5) {
      this.renderPaginationControls();
    }
  }

  renderPaginationControls() {
    const controls = document.querySelector(".pagination");
    controls.innerHTML = "";

    const totalPages = Math.ceil(this.allItems.length / this.pageSize);
    const lefttag = this.createElement("span", [], "< ");
    const righttag = this.createElement("span", [], " >");
    controls.appendChild(lefttag);
    for (let i = 1; i <= totalPages; i++) {
      const btn = document.createElement("div");
      btn.textContent = i;
      if (i === this.currentPage) btn.classList.add("active");
      btn.addEventListener("click", () => {
        this.currentPage = i;
        this.renderPage();
      });

      controls.appendChild(btn);
    }
    controls.appendChild(righttag);
  }
  createLinkRow(data) {
    const row = this.createElement("div", "link-row");

    // Left section
    const linkSection = this.createElement("div", [
      "align-right",
      "link-section",
    ]);

    const titleEl = this.createElement("div", "link-title", data.link.title);
    const shortEl = this.createElement(
      "div",
      "link-sub",
      data.link.shortKey || data.link.uuid
    );

    const hrefContainer = this.createElement("div", "href-container");

    const linkHref = this.createElement("div", ["link-href", "href"]);
    const linkATag = this.createElement("a", []);
    linkATag.href = `/links/${data.link.uuid}`;
    const linkIcon = this.createElement("i", [
      "fa-solid",
      "fa-arrow-up-right-from-square",
      "mg-r025",
    ]);
    const linkText = this.createElement("span", [], "link");
    linkATag.appendChild(linkIcon);
    linkATag.appendChild(linkText);
    linkHref.appendChild(linkATag);

    hrefContainer.appendChild(linkHref);

    if (data.qrcode.id) {
      const qrHref = this.createElement("div", ["qrcode-href", "href"]);
      const qrATag = this.createElement("a", []);
      qrATag.href = `/qrcodes/${data.qrcode.id}`;
      const qrIcon = this.createElement("i", [
        "fa-solid",
        "fa-qrcode",
        "mg-r025",
      ]);
      const qrText = this.createElement("span", [], "QR code");
      qrATag.appendChild(qrIcon);
      qrATag.appendChild(qrText);
      qrHref.appendChild(qrATag);
      hrefContainer.appendChild(qrHref);
    }

    linkSection.appendChild(titleEl);
    linkSection.appendChild(shortEl);
    linkSection.appendChild(hrefContainer);

    // Data cells
    const clickEl = this.createElement("div", [], data.link.clicks);
    const scanEl = this.createElement("div", [], data.link.scan);
    const totalEl = this.createElement("div", [], data.link.totalInteraction);

    const levelEl = this.createElement("div");
    const levelSpan = this.createElement(
      "span",
      [],
      data.link.interactionLevel
    ); // e.g., "High"
    this.addLevelColor(levelSpan);
    levelEl.appendChild(levelSpan);

    // Append all to row
    row.appendChild(linkSection);
    row.appendChild(clickEl);
    row.appendChild(scanEl);
    row.appendChild(totalEl);
    row.appendChild(levelEl);

    this.links.appendChild(row);
  }
  addLevelColor(level) {
    if (level.textContent == "High") {
      level.classList.add("high");
    } else if (level.textContent == "Medium") {
      level.classList.add("medium");
    } else if (level.textContent == "Low") {
      level.classList.add("low");
    } else if (level.textContent == "None") {
      level.classList.add("none");
    } else if (level.textContent == "Very high") {
      level.classList.add("very-high");
    }
  }
}
new Analytics();
