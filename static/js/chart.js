class CreateChart {
  constructor() {
    this.ctx = document.querySelector("#click-Chart").getContext("2d");
    this.ctx_location = document.querySelector("#location").getContext("2d");
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
}
new CreateChart();
