class CreateChart {
  constructor() {
    this.ctx = document.querySelector("#click-Chart").getContext("2d");
    this.getData();
  }
  async getData() {
    const uuid = location.pathname.split("/")[2];
    const response = await fetch(`/api/click/report/${uuid}`, {
      credentials: "include",
    });
    const result = await response.json();
    if (result.ok) {
      this.drawData(result.data);
    }
  }
  drawData(rawData) {
    const labels = rawData.map((item) => item.day);
    const count = rawData.map((item) => item.clickCount);
    new Chart(this.ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "點擊次數",
            data: count,
            backgroundColor: "#13C2C2",
          },
        ],
      },
      options: {
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              stepSize: 1,
              precision: 0,
            },
          },
        },
      },
    });
  }
}
new CreateChart();
