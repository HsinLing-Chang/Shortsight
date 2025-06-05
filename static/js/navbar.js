const navItem = [
  { element: document.querySelector(".home"), path: "/" },
  { element: document.querySelector(".links"), path: "/links" },
  { element: document.querySelector(".qrcodes"), path: "/qrcodes" },
  { element: document.querySelector(".analytics"), path: "/analytics" },
  { element: document.querySelector(".campaign"), path: "/campaign" },
];
// const token = localStorage.getItem("access_token");

navItem.forEach(({ element, path }) => {
  if (!element) return;
  element.addEventListener("click", (e) => {
    e.preventDefault();
    // if (!token) {
    //   window.location.href = "signin";
    //   return;
    // }
    window.location.href = path;
  });
});

class SideBarController {
  constructor({
    btnSelector = ".shrink-button",
    barSelector = ".side-bar",
    itemSelector = ".nav-bar-ul li",
    expendClass = "expend",
    iconOnlyClass = "icon-only",
  } = {}) {
    this.btn = document.querySelector(btnSelector);
    this.sideBar = document.querySelector(barSelector);
    this.navItems = document.querySelectorAll(itemSelector);
    this.expendClass = expendClass;
    this.iconOnlyClass = iconOnlyClass;
    this.arrowIcon = this.btn.querySelector("i");
    this._bindEvents();
    this.signOutBtn = document.querySelector(".login-state");
    this.path = window.location.pathname.split("/")[1];

    if (this.signOutBtn) {
      if (this.signOutBtn.textContent == "Sign In") return;
      this.signOutBtn.addEventListener("click", async () => this._signOut());
    }
    this.targetPage();
  }
  targetPage() {
    this.navItems.forEach((item) => {
      const raw = item.dataset.text;
      const txt = raw.replace(/\s+/g, "").toLowerCase();
      const path = this.path.trim();
      if (txt === path || (txt == "home" && path == "")) {
        const activaIndicator = item.querySelector(".active-indicator");
        item.style.backgroundColor = "#DBEAFE";
        item.style.color = "#1E3A8A";
        activaIndicator.style.backgroundColor = " #1e40af";
      }
    });
  }

  async _signOut() {
    const response = await fetch("/api/user/signout", {
      credentials: "include",
      method: "POST",
    });
    const result = await response.json();
    if (result.ok) {
      alert("Logout successfully.");

      location.href = "/";
    }
  }
  _bindEvents() {
    this.btn.addEventListener("click", () => this.toggle());
  }

  toggle() {
    const isExpended = this.sideBar.classList.toggle(this.expendClass);
    if (isExpended) {
      this._applyExpanded();
    } else {
      this._applyShunk();
    }
  }
  _applyShunk() {
    this.navItems.forEach((item) => {
      const span = item.querySelector("span");
      if (span) {
        span.remove();
        item.classList.add(this.iconOnlyClass);
      }
    });
    this.arrowIcon.className = "fa-solid fa-arrow-right";
  }

  _applyExpanded() {
    this.navItems.forEach((item) => {
      const span = item.querySelector("span");
      if (!span) {
        const txt = item.dataset.text;
        const newSpan = document.createElement("span");
        newSpan.textContent = txt;
        item.appendChild(newSpan);
        item.classList.remove(this.iconOnlyClass);
      }
    });
    this.arrowIcon.className = "fa-solid fa-arrow-left";
  }
}

export default SideBarController;
