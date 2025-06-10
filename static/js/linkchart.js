class CreateChart {
  constructor() {
    this.ctx = document.querySelector("#click-Chart").getContext("2d");
    this.ctx_location = document.querySelector("#location").getContext("2d");
    this.ctx_referrer = document.querySelector("#pie-chart1");
    this.ctx_device = document.querySelector("#pie-chart2");
    this.getData();
  }
  async getData() {
    const path = location.pathname.split("/");
    let router;
    if (path[1] == "links") {
      const uuid = path[2];
      router = `/api/click/report/${uuid}`;
    } else {
      const id = path[2];
      router = `/api/scan/report/${id}`;
    }

    const response = await fetch(router, {
      credentials: "include",
    });
    const result = await response.json();
    if (result.ok && result.data.total > 0) {
      // console.log(result.data);
      this.drawClickEvents(result.data.clickEvents, result.data.total);
      this.drawLocation(result.data.location);
      this.drawReferrerPie(result.data.referrer);
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
    const labels = Object.keys(referrerData);
    const data = Object.values(referrerData);
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
          text: "Referrers",
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
}
new CreateChart();
