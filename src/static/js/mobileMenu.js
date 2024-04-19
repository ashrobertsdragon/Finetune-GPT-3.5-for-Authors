function initialize() {
  const menuToggle = document.getElementById("header-nav-toggle");
  const headerMenu = document.getElementById("mobile-menu");

  function toggleMenu() {
    headerMenu.classList.toggle("hidden");
    headerMenu.classList.toggle("shown");
    menuToggle.innerText = menuToggle.innerText === "menu" ? "menu_open" : "menu";
  };
  
  if (menuToggle && headerMenu) {
    menuToggle.addEventListener("click", toggleMenu);
  }
};

if (document.readyState !== "loading") {
  initialize();
} else {
  document.addEventListener("DOMContentLoaded", initialize);
}