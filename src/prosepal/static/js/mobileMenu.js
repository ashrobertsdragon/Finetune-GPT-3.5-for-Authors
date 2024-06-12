function initialize() {
  const dropMenu = document.getElementById("dropdown");
  const account = document.getElementById("account-menu");

  function toggleMenu() {
    dropMenu.classList.toggle("hidden");
    dropMenu.classList.toggle("shown");
  };

  if (account && dropMenu) {
    account.addEventListener("tap", toggleMenu);
    account.addEventListener("click", toggleMenu);
  }
};

if (document.readyState !== "loading") {
  initialize();
} else {
  document.addEventListener("DOMContentLoaded", initialize);
}
