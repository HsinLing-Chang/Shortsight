class CreateChart {
  constructor() {
    this.ctx = document.querySelector("#click-Chart").getContext("2d");
    this.ctx_location = document.querySelector("#location").getContext("2d");
    this.ctx_referrer = document.querySelector("#referrer-chart");
    this.ctx_device = document.querySelector("#device");
    this.getData();
  }
  async getData() {
    const uuid = location.pathname.split("/")[2];
    const response = await fetch(`/api/click/report/${uuid}`, {
      credentials: "include",
    });
    const result = await response.json();
    if (result.ok) {
      console.log(result.data);
      this.drawClickEvents(result.data.clickEvents);
      this.drawLocation(result.data.location);
      this.drawReferrerPie(result.data.referrer);
      this.drawDevice(result.data.device);
    }
  }
  drawClickEvents(rawData) {
    const labels = rawData.map((item) => item.day);
    const count = rawData.map((item) => item.clickCount);
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
              size: 20,
              weight: "bold",
              color: "#233D63",
            },
            padding: { top: 10 },
          },
          legend: {
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
          },
          y: {
            grid: {
              display: false,
            },
            beginAtZero: true,
            suggestedMax: 50,
            ticks: {
              stepSize: 10,
              precision: 0,
            },
          },
        },
      },
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
            font: { size: 20, weight: "bold" },
            color: "#233D63",
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                const i = context.dataIndex;
                return `Clicks: ${data[i]}, Percent: ${percents[i]}%`;
              },
            },
          },
        },
        scales: {
          x: {
            grid: {
              display: false,
            },
            suggestedMax: 50,
            beginAtZero: true,
            ticks: { precision: 0 },
          },
          y: {
            grid: {
              display: false,
            },
            ticks: { font: { size: 16, weight: "bold" } },
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
            "#36A2EB",
            "#FF6384",
            "#FFCE56",
            "#4BC0C0",
            "#9966FF",
            "#A3A948",
            "#FFB347",
            "#8DD3C7",
          ],
          borderWidth: 0,
        },
      ],
    };
    const options = {
      plugins: {
        title: {
          display: true,
          text: "Referrer",
          font: { size: 22 },
          position: "top",
          align: "start",
        },
        legend: {
          position: "right",
          align: "start",
          labels: {
            font: {
              size: 20,
            },
          },
        },
      },
      cutout: "70%",
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
            "#36A2EB",
            "#FF6384",
            "#FFCE56",
            "#4BC0C0",
            "#9966FF",
            "#A3A948",
            "#FFB347",
            "#8DD3C7",
          ],
          borderWidth: 0,
        },
      ],
    };
    const options = {
      plugins: {
        title: {
          display: true,
          text: "Device",
          font: { size: 22 },
          position: "top",
          align: "start",
        },
        legend: {
          position: "right",
          align: "start",
          labels: {
            font: {
              size: 20,
            },
          },
        },
      },
      cutout: "70%",
    };
    new Chart(this.ctx_device, {
      type: "doughnut",
      data: chartData,
      options: options,
    });
  }
}
new CreateChart();
