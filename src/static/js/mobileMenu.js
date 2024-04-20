function initialize() {
  const dropMenu = document.getElementById("mobile-drowpdown");
  const account = document.getElementById("account-menu");

  function toggleMenu() {
    dropMenu.classList.toggle("hidden");
    dropMenu.classList.toggle("shown");
  };
  
  if (account & dropMenu) {
    account.addEventListener("tap", toggleMenu);
  }
};

if (document.readyState !== "loading") {
  initialize();
} else {
  document.addEventListener("DOMContentLoaded", initialize);
}