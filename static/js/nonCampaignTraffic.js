class Traffic {
  constructor() {
    this.eventType = document.querySelector("#event-type");
    this.sumAllUsers = document.querySelector(".summary-all-users");
    this.sumNewUsers = document.querySelector(".summary-new-users");
    this.sumRatio = document.querySelector(".summary-ratio");
    this.sumLevel = document.querySelector("#summary-level");
    this.gridContent = document.querySelector(".append");
    this.selectBtn = document.querySelector("#apply-range");
    this.selectBtn.addEventListener("click", () => this.buttonChange());
    this.getSourceData();
  }
  buttonChange() {
    const eventType = this.eventType.value;
    const start = document.getElementById("start-date").value;
    const end = document.getElementById("end-date").value;
    if (!start && !end) {
      this.getSourceData(eventType, null, null);
      return;
    }
    if (!start || !end) {
      alert("Please select both start and end dates.");
      return;
    }
    const startDate = new Date(start).toISOString().slice(0, 10);
    const endDate = new Date(end).toISOString().slice(0, 10);

    this.getSourceData(eventType, startDate, endDate);
  }
  async getSourceData(eventType, startDate, endDate) {
    const url = this.getUrl(eventType, startDate, endDate);
    // console.log(url);
    const response = await fetch(url, {
      credentials: "include",
    });
    const result = await response.json();
    if (result.ok) {
      //   console.log(result);
      const summary = result.data.summary;
      const data = result.data.data;
      this.appendSummary(summary);
      this.appendGridData(this.gridContent, data);
      //   console.log(summary, data);
    }
  }
  getUrl(eventType, startDate, endDate) {
    let baseUrl = "";
    if (!eventType || eventType === "all") {
      baseUrl = "/api/non-campaign-traffic";
    } else {
      baseUrl = "/api/non-campaign-traffic-event-type";
    }
    const params = new URLSearchParams();
    if (eventType && eventType !== "all") {
      params.set("event_type", eventType);
    }
    if (startDate) {
      params.set("start_date", startDate);
    }
    if (endDate) {
      params.set("end_date", endDate);
    }
    return `${baseUrl}?${params.toString()}`;
  }
  appendSummary(summary) {
    this.sumAllUsers.textContent = summary.total_users;
    this.sumNewUsers.textContent = summary.total_new_users;
    this.sumRatio.textContent = `${summary.overall_ratio} %`;
    this.sumLevel.textContent = summary.new_user_level;
    this.sumLevel.className = "";
    this.addLevelColor(this.sumLevel);
  }
  appendGridData(container, data) {
    container.innerHTML = "";
    data.forEach((item) => {
      container.appendChild(
        this.createElement("div", [], `${item.source}/${item.medium}`)
      );
      container.appendChild(
        this.createElement("div", [], item.total_interactions)
      );
      container.appendChild(this.createElement("div", [], item.new_users));
      container.appendChild(
        this.createElement("div", [], `${item.new_user_ratio} %`)
      );
      // 最後一欄有 <span class="high">high</span>
      const spanWrapper = this.createElement("div");
      const span = this.createElement("span", [], item.new_user_level); // 套上 high / medium / low class
      this.addLevelColor(span);
      spanWrapper.appendChild(span);
      container.appendChild(spanWrapper);
    });
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
  addLevelColor(level) {
    if (level.textContent == "High") {
      level.classList.add("high");
    } else if (level.textContent == "Medium") {
      level.classList.add("medium");
    } else if (level.textContent == "Low") {
      level.classList.add("low");
    } else if (level.textContent == "Very Low") {
      level.classList.add("very-low");
    } else if (level.textContent == "Unstable") {
      level.classList.add("unstable");
    } else if (level.textContent == "Very High") {
      level.classList.add("very-high");
    }
  }
}
new Traffic();
