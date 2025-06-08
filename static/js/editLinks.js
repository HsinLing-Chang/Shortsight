class EditLinks {
  constructor() {
    this.title = document.querySelector("#title");
    this.shortKey = document.querySelector("#short-key");
    this.destination = document.querySelector(".destination-url");
    this.uuid = null;
    if (this.title && this.shortKey && this.destination) {
      this.addText();
    }

    this.editForm = document.querySelector(".edit-form");
    if (this.editForm) {
      this.editForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        this.saveUpdate();
      });
    }
    this.backToLink = document.querySelector(".back-to-list");
    if (this.backToLink) {
      this.backToLink.href = `/links/${this.uuid}`;
    }
  }

  addText() {
    const path = new URLSearchParams(window.location.search);
    const title = path.get("title");
    const shortKey = path.get("short_key").split("/")[4];
    const destination = path.get("destination");
    this.uuid = path.get("id");
    this.title.value = title;
    this.shortKey.value = shortKey;
    this.destination.textContent = destination;
    this.errorMsg = document.querySelector("#error");
  }
  _getPayload() {
    return {
      title: this.title.value,
      short_key: this.shortKey.value,
      target_url: this.destination.textContent,
    };
  }

  async saveUpdate() {
    const payload = this._getPayload();
    try {
      const response = await fetch(`/api/links/${this.uuid}`, {
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        method: "PUT",
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (data.ok) {
        alert("Update successfully.");
        location.href = `/links/${this.uuid}`;
      }
      if (data.error) {
        throw new Error(data.message);
      }
    } catch (e) {
      this.errorMsg.textContent = e.message;
      this.errorMsg.style.color = "red";
    }
  }
}
new EditLinks();
