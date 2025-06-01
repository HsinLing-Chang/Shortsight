async function getLinksInfo() {
  const path = window.location.pathname;
  const uuid = path.split("/")[2];
  if (!uuid) return;
  const token = localStorage.getItem("access_token");
  const response = await fetch(`/api/links/${uuid}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  const linkData = await response.json();
  if (linkData.data) {
    const title = document.querySelector(".title");
    const shortKey = document.querySelector(".short-key");
    const destination = document.querySelector(".destination");
    const createDate = document.querySelector(".created-at > span");
    title.textContent = linkData.data.title;

    const shortCode = linkData.data.short_key
      ? linkData.data.short_key
      : linkData.data.uuid;

    shortKey.textContent = `https://s.ppluchuli.com/s/${shortCode}`;
    destination.textContent = linkData.data.target_url;
    destination.href = linkData.data.target_url;
    destination.target = "_blank";
    createDate.textContent = linkData.data.created_at;
  }
}
getLinksInfo();
