document.addEventListener("headerUpdated", initializeDarkMode);

function initializeDarkMode() {
  const toggleSwitch = document.getElementById("darkModeToggle");
  if (!toggleSwitch) return;

  const isCheckbox = toggleSwitch instanceof HTMLInputElement;
  function controlSwitch(enable) {
    if (isCheckbox) {
      toggleSwitch.checked = enable;
    } else {
      updateIcon(enable);
    };
    toggleDarkMode(enable);
  };

  function isDarkMode() {
    if (isCheckbox) {
      return toggleSwitch.checked;
    } else {
      return toggleSwitch.textContent === "dark_mode";
    };
  };

  const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)");
  if (prefersDarkScheme.matches) {
    controlSwitch(true);
  };

  toggleSwitch.addEventListener("click", () => {
    toggleDarkMode(controlSwitch(isDarkMode));
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
    toggleSwitch.textContent = isDarkMode ? "light_mode" : "dark_mode";
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
    toggleLabel.textContent = isDarkMode ? "Light mode" : "Dark mode";
  };
  if (endError) {
    endError.src = isDarkMode ? "/static/images/alert-dark.png" : "/static/images/alert-light.png";
  };
  updateIcon(isDarkMode);
}
