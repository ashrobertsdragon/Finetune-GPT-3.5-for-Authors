document.addEventListener("headerUpdated", initializeDarkMode);

function initializeDarkMode() {
  const toggleSwitch = document.getElementById("darkModeToggle");
  if (!toggleSwitch) return;

  function isDarkMode() {
    if (isCheckbox) {
      return toggleSwitch.checked;
    } else {
      return toggleSwitch.textContent === "dark_mode";
    };
  };

  const isCheckbox = toggleSwitch instanceof HTMLInputElement;
  const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)");
  if (prefersDarkScheme.matches) {
    if (isCheckbox) {
      toggleSwitch.checked = true;
    } else {
      updateIcon(true);
    };
    toggleDarkMode(true);
  };

  toggleSwitch.addEventListener("click", () => {
    toggleDarkMode(isDarkMode);
  });
}

function toggleDarkMode(enable) {
  document.body.classList.toggle("dark-mode", enable);
  document.body.classList.toggle("light-mode", !enable);
  updateModeElements(enable);
}

function updateIcon(isDarkMode) {
  const toggleSwitch = document.getElementById("darkModeToggle");
  if (toggleSwitch && toggleSwitch.textContent) {
    toggleSwitch.textContent = isDarkMode ? "dark_mode" : "light_mode";
  }
}

function updateModeElements(isDarkMode) {
  const logo = document.getElementById("logo");
  const toggleLabel = document.getElementById("toggleLabel");
  const endError = document.getElementById("endError");

  if (logo) {
    logo.src = isDarkMode ? "/static/images/logo-dark.png" : "/static/images/logo.png";
  };
  if (toggleLabel) {
    toggleLabel.textContent = isDarkMode ? "Dark mode" : "Light mode";
  };
  if (endError) {
    endError.src = isDarkMode ? "/static/images/alert-dark.png" : "/static/images/alert-light.png";
  };
  updateIcon(isDarkMode);
}
