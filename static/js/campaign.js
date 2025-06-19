class Campaign {
  constructor() {
    this.eventType = document.querySelector("#event-type");
    this.sumAllUsers = document.querySelector(".summary-all-users");
    this.sumNewUsers = document.querySelector(".summary-new-users");
    this.sumRatio = document.querySelector(".summary-ratio");
    this.sumLevel = document.querySelector("#summary-level");
    this.gridContent = document.querySelector(".append");
    this.selectBtn = document.querySelector("#apply-range");
    this.selectBtn.addEventListener("click", () => this.buttonChange());
    this.getAllCampaign();
  }
  buttonChange() {
    const eventType = this.eventType.value;
    const start = document.getElementById("start-date").value;
    // console.log(eventType);
    const end = document.getElementById("end-date").value;
    if (!start && !end) {
      this.getAllCampaign(eventType, null, null);
      return;
    }
    if (!start || !end) {
      alert("Please select both start and end dates.");
      return;
    }
    const startDate = new Date(start).toISOString().slice(0, 10);
    const endDate = new Date(end).toISOString().slice(0, 10);

    // console.log(endDate);
    this.getAllCampaign(eventType, startDate, endDate);
  }

  async getAllCampaign(eventType = null, startDate = null, endDate = null) {
    const url = this.getUrl(eventType, startDate, endDate);
    // console.log(url);
    const response = await fetch(url, {
      credentials: "include",
    });
    const result = await response.json();
    if (result.ok) {
      const summary = result.data.summary;

      // console.log(result.data);
      const data = result.data.data;
      this.appendSummary(summary);
      this.appendGridData(this.gridContent, data);
    }
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
      container.appendChild(this.createElement("div", [], item.campaign));
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
  getUrl(eventType, startDate, endDate) {
    let url = "";

    const hasDate = startDate && endDate;
    const hasEventType = eventType && eventType !== "all";

    // 有 eventType（非 all/null）：用 `/campaign`
    if (hasEventType) {
      url = `/api/report/utm/campaign?event_type=${eventType}`;
      if (hasDate) {
        url += `&start_date=${startDate}&end_date=${endDate}`;
      }
    }
    // 無 eventType 或 eventType = all：用 `/campaigns`
    else {
      url = `/api/report/utm/campaigns`;
      const params = [];
      if (startDate) params.push(`start_date=${startDate}`);
      if (endDate) params.push(`end_date=${endDate}`);
      if (params.length) {
        url += `?${params.join("&")}`;
      }
    }
    return url;
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
new Campaign();
