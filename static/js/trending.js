class Trending {
  constructor() {
    this.shortKey = document.querySelector(".short-key");
    this.clicks = document.querySelector(".clicks");
    this.scans = document.querySelector(".scans");
    this.highestDay = document.querySelector(".highest-day");
    this.trendChartInstance = null;
    document
      .getElementById("apply-range")
      .addEventListener("click", async () => {
        const start = document.getElementById("start-date").value;
        const end = document.getElementById("end-date").value;
        if (!start || !end) {
          alert("Please select both start and end dates.");
          return;
        }
        const startDate = new Date(start);
        const endDate = new Date(end);
        console.log(endDate);
        const diffDays =
          Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24)) + 1; // 加 1 表示包含當天

        if (diffDays < 7) {
          alert("請選擇至少 7 天的日期範圍。");
          return;
        }
        await this.getTrend(start, end);
      });
    this.init();
  }
  async init() {
    await this.getTrend(); // ✅ 確保初次正確載入圖表
  }
  async getTrend(startDate = null, endDate = null) {
    // const params = new URLSearchParams({
    //   start_date: startDate,
    //   end_date: endDate,
    // });
    // console.log(startDate);
    let url;
    if (!startDate) {
      url = "/api/report/trend";
    } else {
      url = `/api/report/trend?start_date=${startDate}&end_date=${endDate}`;
    }
    const response = await fetch(url, {
      credentials: "include",
    });
    const data = await response.json();
    console.log(data.data);
    this.trendChart(data.data);
    this.topLink(data.data.summary, data.data.top_info);
  }

  topLink(summary, topInfo) {
    const container = document.querySelector(".top-link-info"); // 你要放入的容器
    container.innerHTML = "";
    topInfo.forEach((info) => {
      const topLink = this.createElement("div", ["top-link", "card-shadow"]);

      // 🔹 第一層：Top Link + a 標籤
      const linkDiv = this.createElement("div", ["mg-b05"]);
      const strongLabel = this.createElement("strong", [], "Link:");
      const anchor = this.createElement("a", ["a-link"]);
      anchor.href = `/links/${info.uuid}`;
      const spanShortKey = this.createElement(
        "span",
        "short-key",
        ` ${info.shortKey}`
      );
      anchor.appendChild(spanShortKey);
      linkDiv.appendChild(strongLabel);
      linkDiv.appendChild(anchor);

      // 🔹 第二層：Clicks
      const clickDiv = this.createElement("div", ["mg-b05"]);
      const clickLabel = this.createElement("strong", [], "Clicks:");
      const clickValue = this.createElement(
        "span",
        "clicks",
        ` ${info.clicks}`
      );
      clickDiv.appendChild(clickLabel);
      clickDiv.appendChild(clickValue);

      // 🔹 第三層：Scans
      const scanDiv = this.createElement("div");
      const scanLabel = this.createElement("strong", [], "Scans:");
      const scanValue = this.createElement("span", "scans", ` ${info.scans}`);
      scanDiv.appendChild(scanLabel);
      scanDiv.appendChild(scanValue);

      // 加入三個區塊
      topLink.appendChild(linkDiv);
      topLink.appendChild(clickDiv);
      topLink.appendChild(scanDiv);

      container.appendChild(topLink);
    });

    this.highestDay.textContent = `Highest Activity: ${summary.max_day} (${summary.max_count} total)`;
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
  trendChart(data) {
    const trend = data.trend;
    const labels = trend.map((item) => item.day);
    const clicks = trend.map((item) => item.clicks);
    const scans = trend.map((item) => item.scans);
    const total = trend.map((item) => item.total);

    const config = {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Clicks",
            data: clicks,
            borderColor: "#007bff",
            backgroundColor: "#007bff",
            tension: 0.3,
            pointRadius: 0,
            pointHoverRadius: 5,
          },
          {
            label: "Scans",
            data: scans,
            borderColor: "#28a745",
            backgroundColor: "#28a745",
            tension: 0.3,
            pointRadius: 0,
            pointHoverRadius: 5,
          },
          {
            label: "Total",
            data: total,
            borderColor: "#ffc107",
            backgroundColor: "#ffc107",
            tension: 0.3,
            pointRadius: 0,
            pointHoverRadius: 5,
          },
        ],
      },
      options: {
        maintainAspectRatio: false,
        interaction: {
          mode: "index",
          intersect: false,
        },
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: "Trend Chart: Clicks, Scans, Total",
            color: "#2b3e50",
          },
          legend: {
            position: "top",
          },
        },
        scales: {
          y: {
            grid: {
              display: false,
            },
            beginAtZero: true,
            ticks: {
              precision: 0,
            },
            suggestedMax: 50,
          },
          x: {
            grid: {
              display: false,
            },
            ticks: {
              maxRotation: 45,
              minRotation: 45,
            },
          },
        },
      },
    };
    const ctx = document.getElementById("trendChart").getContext("2d");
    if (this.trendChartInstance) {
      this.trendChartInstance.destroy(); // 更新前先銷毀舊圖
    }

    this.trendChartInstance = new Chart(ctx, config);
  }
  fillMissingDates(trend, startDateStr, endDateStr) {
    const start = new Date(startDateStr);
    const end = new Date(endDateStr);
    const map = new Map(trend.map((item) => [item.day, item]));

    const filled = [];
    for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
      const dayStr = d.toISOString().slice(0, 10); // YYYY-MM-DD
      if (map.has(dayStr)) {
        filled.push(map.get(dayStr));
      } else {
        filled.push({
          day: dayStr,
          clicks: 0,
          scans: 0,
          total: 0,
        });
      }
    }
    return filled;
  }
}

new Trending();
