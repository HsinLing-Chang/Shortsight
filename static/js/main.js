import SideBarController from "./navbar.js";
import CreateLink from "./createLinkForm.js";
import SignUp from "./signUp.js";
import SignIn from "./signIn.js";
import LinksAnalytics from "./linksAnalytics.js";
import EditLinks from "./editLinks.js";
import QrcodeCard from "./qrcodes.js";
import QrcodesAnalytics from "./qrcodesAnalytics.js";
import CreateQrcodeForm from "./createQrcodeForm.js";
window.addEventListener("DOMContentLoaded", () => {
  const path = window.location.pathname;
  console.log(path);
  const location = path.split("/")[1];
  console.log(location);
  new SideBarController({
    expandClass: "expend",
    iconOnlyClass: "icon-only",
  });
  // links
  if (path.startsWith("/links/create")) {
    new CreateLink();
  } else if (path.startsWith("/links/update")) {
    new EditLinks();
  } else if (path.startsWith("/links")) {
    const load = new LinksAnalytics();
    load.load();
  }
  // signin & signup
  if (path.startsWith("/signup")) {
    new SignUp();
  } else if (path.startsWith("/signin")) {
    new SignIn();
  }
  // Qr code
  if (path.startsWith("/qrcodes/create")) {
    new CreateQrcodeForm();
  } else if (path.startsWith("/qrcodes")) {
    new QrcodeCard();
  } else if (path.startsWith("/qrcodes/")) {
    new QrcodesAnalytics();
  }
});
