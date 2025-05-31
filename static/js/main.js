import SideBarController from "./navbar.js";
import CreateLink from "./createLinkForm.js";
import SignUp from "./signUp.js";
import SignIn from "./signIn.js";
window.addEventListener("DOMContentLoaded", () => {
  new SideBarController({ expandClass: "expend", iconOnlyClass: "icon-only" });
  new CreateLink();
  new SignUp();
  new SignIn();
});
