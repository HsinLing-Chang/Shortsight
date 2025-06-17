class Index {
  constructor() {
    this.userInfo = document.querySelector(".user-info");
    this.ctx = document.getElementById("trafficPieChart").getContext("2d");
    this.editBtn = document.querySelector(".edit-btn");
    this.createBtn = document.querySelector(".create-btn");
    this.username = document.querySelector(".user-name");
    this.email = document.querySelector(".user-email");
    this.totalInteractions = document.querySelector(".total-interactions");
    this.totalClicks = document.querySelector(".total-clicks");
    this.totalScans = document.querySelector(".total-scans");
    this.ratioPie = document.querySelector(".ratio-pie");
    this.editBtn.addEventListener("click", () => {
      this.editName();
    });
    this.createBtn.addEventListener("click", () => {
      this.createLink();
    });
    this.isEditing = false;
    this.getClicksScanRatio();
    this.getUserInfo();
  }
  async getUserInfo() {
    const response = await fetch("/api/user", {
      credentials: "include",
    });
    const result = await response.json();
    if (result.ok) {
      this.username.textContent = result.data.username;
      this.email.textContent = result.data.email;
    }
  }
  async getClicksScanRatio() {
    const response = await fetch("/api/report/interaction-ratio", {
      credentials: "include",
    });
    const result = await response.json();
    const data = result.data;
    console.log(data);

    this.totalInteractions.textContent = `Total interactions: ${data.total}`;
    this.totalClicks.textContent = `${data.clicks} (${data.click_percent} %)`;
    this.totalScans.textContent = `${data.scans} (${data.scan_percent} %)`;
    if (data.total == 0) {
      this.ratioPie.innerHTML = "No interaction data yet";
      this.ratioPie.classList.add("pie-true");
      return;
    }
    this.ratioPie.classList.remove("pie-true");
    this.drawRatio(data);
  }
  drawRatio(data) {
    new Chart(this.ctx, {
      type: "doughnut", // 或 'pie'
      data: {
        labels: ["Clicks", "Scans"],
        datasets: [
          {
            data: [data.clicks, data.scans],
            backgroundColor: ["#3b82f6", "#f59e0b"], // 藍與橘
            hoverOffset: 20,
          },
        ],
      },
      options: {
        plugins: {
          title: {
            display: true,
            text: "Interaction Source Distribution",
          },
          legend: {
            position: "bottom",
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                const label = context.label || "";
                const value = context.raw;
                const total = data.total;
                const percent = ((value / total) * 100).toFixed(1);
                return `${label}: ${value} (${percent}%)`;
              },
            },
          },
        },
      },
    });
  }
  async editName() {
    const nameSpan = document.querySelector(".user-name");

    if (!this.isEditing) {
      const name = nameSpan.textContent;

      this.userInfo.style.padding = "2rem";
      nameSpan.innerHTML = `<input type="text" id="name-input" value="${name}">`;
      this.editBtn.textContent = "Save";
    } else {
      this.userInfo.style.padding = "2rem 4rem";
      const newName = document.getElementById("name-input").value;
      const response = await fetch("/api/user", {
        headers: {
          "Content-Type": "application/json",
        },
        method: "PUT",
        credentials: "include",
        body: JSON.stringify({
          username: newName,
        }),
      });
      const result = await response.json();
      console.log(result);
      nameSpan.textContent = newName;

      this.editBtn.textContent = "Edit";
    }

    this.isEditing = !this.isEditing;
  }

  async createLink() {
    const linkInput = document.querySelector("#link-input");
    const destination = linkInput.value.trim();

    if (!destination) {
      alert("Please enter your destination URL before creating a link.");
      return;
    }
    const payload = {
      target_url: destination,
    };
    const response = await fetch("/api/links/shorten", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        credentials: "include",
      },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (result.ok) {
      alert("Short link generated!");
      location.href = "/links";
    }
  }
}
new Index();
