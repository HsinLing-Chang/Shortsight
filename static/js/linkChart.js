class CreateChart {
  constructor() {
    this.ctx = document.querySelector("#click-Chart").getContext("2d");
    this.ctx_location = document.querySelector("#location").getContext("2d");
    this.ctx_referrer = document.querySelector("#pie-chart1");
    this.ctx_device = document.querySelector("#pie-chart2");
    this.chartContainer = document.querySelector(".chart-container");
    this.newReferrerContainer = document.querySelector("#referrer-container");
    // this.referrerContainer = document.querySelector(".analytics-container");
    this.getData();
    this.getReferrer();
    this.dropDown();
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
  async getData() {
    const uuid = location.pathname.split("/")[2];
    const response = await fetch(`/api/report/click/${uuid}`, {
      credentials: "include",
    });
    const result = await response.json();
    if (result.ok && result.data.total > 0) {
      // console.log(result);
      // console.log(result.data);

      this.drawClickEvents(result.data.clickEvents, result.data.total);
      this.drawLocation(result.data.location);
      // this.drawReferrerPie(result.data.referrer);
      this.drawDevice(result.data.device);
    } else {
      const chartContainer = document.querySelector(".chart-container");
      chartContainer.innerHTML = `<div class="empty-msg card-shadow">
      <h1>😕 😕 😕 😕</h1>
      <h2>😕 😕 😕 😕</h2>
      <h3>😕 😕 😕 😕</h3>
      <h4>😕 😕 😕 😕</h4>
      <h5>😕 😕 😕 😕</h5>
      <h6>😕 😕 😕 😕</h6>
      <h3>${result.message || "Oops... No clicks found"} </h3>
    </div>`;
    }
  }
  async getReferrer() {
    const uuid = location.pathname.split("/")[2];
    const response = await fetch(`/api/report/click/referrer/${uuid}`, {
      credentials: "include",
    });
    const result = await response.json();
    if (result.ok) {
      const channels = result.data.channels;
      // console.log(channels);
      // this.createReferrerData(channels);
      this.drawReferrerPie(channels);
      this.createNewReferrerData(this.newReferrerContainer, channels);
    }
    // console.log(result);
  }
  drawClickEvents(rawData, total) {
    const labels = rawData.map((item) => item.day);
    const count = rawData.map((item) => item.clickCount);
    const totalPlugin = {
      id: "totalPlugin",
      afterDraw(chart) {
        const { ctx, chartArea } = chart;
        ctx.save();
        ctx.font = "bold 18px Helvetica";
        ctx.fillStyle = "#233D63";
        ctx.textAlign = "right";
        ctx.fillText(
          `Total number of clicks: ${total}`,
          chartArea.right,
          chartArea.top - 70
        );
        ctx.restore();
      },
    };
    new Chart(this.ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Click count",
            data: count,
            backgroundColor: "#36B3A8",
            hoverBackgroundColor: "#209B8A",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: "Engagements over time",
            align: "start",
            font: {
              size: 22,
              weight: "bold",
              family: "Helvetica",
            },
            color: "#233D63",
            padding: { bottom: 60 },
          },
          legend: {
            display: false,
            labels: {
              color: "#566375",
              font: {
                size: 15,
                family: "Noto Sans TC, Arial, sans-serif",
              },
            },
          },
        },
        scales: {
          x: {
            grid: {
              display: false,
            },
            ticks: {
              font: {
                size: 12,
                family: "Arial",
              },
              color: "#333",
              font: { size: 12, weight: "bold" },
            },
          },
          y: {
            grid: {
              display: false,
            },
            beginAtZero: true,
            suggestedMax: 50,
            ticks: {
              color: "#333",
              stepSize: 10,
              precision: 0,
              font: { size: 12, weight: "bold" },
            },
          },
        },
      },
      plugins: [totalPlugin],
    });
  }
  drawLocation(locationData) {
    const labels = locationData.map((item) => item.country);
    const data = locationData.map((item) => item.clicks);
    const percents = locationData.map((item) => item.percent);
    new Chart(this.ctx_location, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Clicks",
            data: data,
            backgroundColor: "#007aff",
            borderRadius: 10,
            barThickness: 20,
            categoryPercentage: 0.6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: "y",
        plugins: {
          title: {
            display: true,
            text: "Country Ranking",
            align: "start",
            font: { size: 22, weight: "bold" },
            color: "#233D63",
            padding: { bottom: 30 },
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                const i = context.dataIndex;
                return `Clicks: ${data[i]}, Percent: ${percents[i]}%`;
              },
            },
          },
          legend: {
            display: false,
          },
        },
        scales: {
          x: {
            grid: {
              display: false,
            },
            suggestedMax: 50,
            beginAtZero: true,
            ticks: {
              precision: 0,
              color: "#333",
              font: { size: 12, weight: "bold" },
            },
          },
          y: {
            grid: {
              display: false,
            },
            ticks: { font: { size: 16, weight: "bold" }, color: "#333" },
          },
        },
      },
    });
  }
  drawReferrerPie(referrerData) {
    const labels = referrerData.map((item) => item.channel);
    const data = referrerData.map((item) => item.total_clicks);
    const chartData = {
      labels: labels,
      datasets: [
        {
          data: data,
          backgroundColor: [
            "#A78BFA",
            "#60A5FA",
            "#F472B6",
            "#FCD34D",

            "#F87171",
            "#FBBF24",
            "#41ba7c",
          ],
          borderWidth: 0,
        },
      ],
    };
    const options = {
      plugins: {
        title: {
          display: true,
          text: "Channels",
          font: { size: 22 },
          color: "#233D63",
          position: "top",
          align: "start",
          padding: {
            top: 30,
          },
        },
        legend: {
          position: "right",
          align: "start",
          labels: {
            font: {
              size: 16,
              weight: "bold",
            },
          },
          onHover: (event) => {
            event.native.target.style.cursor = "pointer";
          },
          onLeave: (event) => {
            event.native.target.style.cursor = "default";
          },
        },
      },
      cutout: "80%",
    };
    new Chart(this.ctx_referrer, {
      type: "doughnut",
      data: chartData,
      options: options,
    });
  }
  drawDevice(deviceData) {
    const labels = Object.keys(deviceData);
    const data = Object.values(deviceData);
    const chartData = {
      labels: labels,
      datasets: [
        {
          data: data,
          backgroundColor: [
            "#3B82F6",
            "#F87171",
            "#FBBF24",
            "#34D399",
            "#A78BFA",
            "#60A5FA",
            "#F472B6",
            "#FCD34D",
          ],
          borderWidth: 0,
        },
      ],
    };
    const options = {
      plugins: {
        title: {
          display: true,
          text: "Devices",
          font: { size: 22 },
          color: "#233D63",
          position: "top",
          align: "start",
          padding: {
            top: 30,
          },
        },
        legend: {
          position: "right",
          align: "start",
          labels: {
            font: {
              size: 16,
              weight: "bold",
            },
            padding: 20,
          },
          onHover: (event) => {
            event.native.target.style.cursor = "pointer";
          },
          onLeave: (event) => {
            event.native.target.style.cursor = "default";
          },
        },
      },
      cutout: "80%",
    };
    new Chart(this.ctx_device, {
      type: "doughnut",
      data: chartData,
      options: options,
    });
  }
  createReferrerData(channels) {
    const container = document.getElementById("dropdown-container");
    container.innerHTML = ""; // 清空舊資料

    channels.forEach((channel) => {
      const channelBox = this.createElement("div", "channel-box");

      const channelToggle = this.createElement(
        "div",
        ["toggle", "level-1"],
        `${channel.channel} (${channel.total_clicks})`
      );
      channelBox.appendChild(channelToggle);

      const sourceList = this.createElement("div", "nested");

      if (channel.sources.length > 0) {
        channel.sources.forEach((source) => {
          const sourceToggle = this.createElement(
            "div",
            ["toggle", "level-2"],
            `${source.source} (${source.total_clicks})`
          );

          sourceList.appendChild(sourceToggle);

          const domainList = this.createElement("div", "nested");

          if (source.domains.length > 0) {
            source.domains.forEach((domain) => {
              const domainItem = this.createElement(
                "div",
                ["level-3"],
                `${domain.domain} (${domain.clicks})`
              );
              domainList.appendChild(domainItem);
            });
          }

          sourceList.appendChild(domainList);
        });
      }

      channelBox.appendChild(sourceList);
      container.appendChild(channelBox);
    });
  }
  dropDown() {
    document.addEventListener("click", function (e) {
      if (e.target.classList.contains("toggle")) {
        e.target.classList.toggle("open");
        const next = e.target.nextElementSibling;
        if (next && next.classList.contains("nested")) {
          next.style.display =
            next.style.display === "block" ? "none" : "block";
        }
      }
    });
  }
  createNewReferrerData(container, channels) {
    channels.forEach((channelObj) => {
      const title = `${channelObj.channel} (${channelObj.total_clicks})`;

      const channelContainer = this.createElement("div", "channel-container");
      channelContainer.style.marginBottom = "12px";

      const channelName = this.createElement("div", ["channel-name"], title);

      const gridContainer = this.createElement("div", "grid-container");
      gridContainer.style.display = "none";

      if (channelObj.sources && channelObj.sources.length > 0) {
        const headers = ["Channel", "Source", "Medium", "Domain", "Click"];
        headers.forEach((title) =>
          gridContainer.appendChild(this.createElement("div", "g-title", title))
        );
        channelObj.sources.forEach((src) => {
          src.domains.forEach((domainObj) => {
            gridContainer.appendChild(
              this.createElement("div", [], channelObj.channel)
            );
            gridContainer.appendChild(
              this.createElement("div", [], src.source)
            );
            gridContainer.appendChild(
              this.createElement("div", [], src.medium)
            );
            gridContainer.appendChild(
              this.createElement("div", [], domainObj.domain)
            );
            gridContainer.appendChild(
              this.createElement("div", [], domainObj.clicks)
            );
          });
        });
      }

      channelName.addEventListener("click", () => {
        gridContainer.style.display =
          gridContainer.style.display === "none" ? "grid" : "none";
      });

      channelContainer.appendChild(channelName);
      channelContainer.appendChild(gridContainer);
      container.appendChild(channelContainer);
    });
  }
}
new CreateChart();
