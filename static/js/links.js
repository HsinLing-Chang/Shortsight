function createElement(tag, className = [], textContent = "") {
  const element = document.createElement(tag);
  if (typeof className == "string" && className) {
    element.classList.add(className);
  } else if (Array.isArray(className)) {
    element.classList.add(...className);
  }
  if (textContent) element.textContent = textContent;
  return element;
}

const linkCardContainer = document.querySelector(".link-card-container");

function addCopyEvent(copyBtn, copyText, url) {
  if (copyBtn) {
    copyBtn.addEventListener("click", async () => {
      clickCopy(url, copyText);
    });
  }
}

async function clickCopy(url, copyText, copyTimeoutId = null) {
  if (copyTimeoutId) {
    clearTimeout(copyTimeoutId);
  }
  await navigator.clipboard.writeText(url);
  copyText.textContent = "copied";
  copyTimeoutId = setTimeout(() => {
    copyText.textContent = "copy";
    copyTimeoutId = null;
  }, 1200);
}

async function getLinks() {
  // const token = localStorage.getItem("access_token");
  const response = await fetch("/api/links", {
    headers: {
      credentials: "include",
    },
    method: "GET",
  });
  const data = await response.json();
  if (data.data) {
    data.data.forEach((linkData) => {
      const shortLink = `https://s.ppluchuli.com/s/${
        linkData.short_key ? linkData.short_key : linkData.uuid
      }`;
      const linkCard = createElement("div", "link-card");
      const linkInfo = createElement("div", "link-info");
      const btnCopy = createElement("button", [
        "copy-btn",
        "pd-05",
        "self-align-start",
      ]);
      const copyImg = createElement("i", ["fa-solid", "fa-copy"]);
      const copyText = createElement("div", "copy-text", "copy");
      const title = createElement("h3", ["title", "padding-bt", "font-la"]);
      const linkInfoWrapper = createElement("div", "link-info-wrapper");
      const calanderWrapper = createElement("div", "mg-t1");
      const line = createElement("div", "line");
      const date = createElement("span", "", linkData.created_at.split(" ")[0]);
      const calander = createElement("i", ["fa-solid", "fa-calendar"]);
      calander.style.marginRight = "0.5rem";
      const shortKey = createElement(
        "a",
        ["short-key", "padding-bt", "font-rg", "font-w600"],
        shortLink
      );

      const destination = createElement(
        "a",
        ["destination", "padding-bt", "font-rg"],
        linkData.target_url ? linkData.target_url : linkData.uuid
      );
      const titleHref = createElement("a", "link-title", linkData.title);
      titleHref.href = `/links/${linkData.uuid}`;
      shortKey.href = shortLink;
      // shortKey.target = "_blank";
      destination.href = linkData.target_url;
      destination.target = "_blank";
      title.appendChild(titleHref);
      linkInfoWrapper.appendChild(title);
      linkInfoWrapper.appendChild(shortKey);
      linkInfoWrapper.appendChild(destination);
      calanderWrapper.appendChild(calander);
      calanderWrapper.appendChild(date);
      linkInfo.appendChild(linkInfoWrapper);
      btnCopy.appendChild(copyImg);
      btnCopy.appendChild(copyText);
      linkInfo.appendChild(btnCopy);
      linkCard.appendChild(linkInfo);
      linkCard.appendChild(line);
      linkCard.appendChild(calanderWrapper);
      linkCardContainer.appendChild(linkCard);
      addCopyEvent(btnCopy, copyText, shortLink);
    });
  } else {
  }
}

getLinks();
