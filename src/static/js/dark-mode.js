document.addEventListener("headerUpdated", initializeDarkMode);

function initializeDarkMode() {
  const toggleSwitch = document.getElementById("darkModeToggle");
  if (!toggleSwitch) return;

  function currentDarkMode() {
    if (isCheckbox) {
      return toggleSwitch.checked;
    } else {
      return toggleSwitch.textContent === "light_mode";
    };
  };

  const isCheckbox = toggleSwitch instanceof HTMLInputElement;
  const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)");
  if (prefersDarkScheme.matches) {
    if (isCheckbox) {
      toggleSwitch.checked = true;
    };
    toggleDarkMode(true);
  };

  toggleSwitch.addEventListener("click", () => {
    toggleDarkMode(!currentDarkMode());
  });
}

function toggleDarkMode(enable) {
  document.body.classList.toggle("dark-mode", enable);
  document.body.classList.toggle("light-mode", !enable);
  updateModeElements(enable);
}

function updateIcon(darkMode) {
  const toggleSwitch = document.getElementById("darkModeToggle");
  if (toggleSwitch && toggleSwitch.textContent) {
    toggleSwitch.textContent = darkMode ? "light_mode" : "dark_mode";
  }
}

function updateModeElements(darkMode) {
  const logo = document.getElementById("logo");
  const toggleLabel = document.getElementById("toggleLabel");
  const endError = document.getElementById("endError");

  if (logo) {
    logo.src = darkMode ? "/static/images/logo.png" : "/static/images/logo-dark.png";
  };
  if (toggleLabel) {
    toggleLabel.textContent = darkMode ? "Light mode" : "Dark mode";
  };
  if (endError) {
    endError.src = darkMode ? "/static/images/alert-light.png" : "/static/images/alert-dark.png";
  };
  updateIcon(darkMode);
}

// Commit 4999700 has working version in case it gets fubar again