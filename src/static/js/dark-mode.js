document.addEventListener("headerUpdated", initializeDarkMode);

function initializeDarkMode() {
  const toggleSwitch = document.getElementById("darkModeToggle");
  if (!toggleSwitch) return;

  function isDarkMode() {
    return document.body.classList.contains("dark-mode");
  }

  const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)");
  const initialDarkMode = prefersDarkScheme.matches;
  const isCheckbox = toggleSwitch instanceof HTMLInputElement;
  if (isCheckbox) {
    toggleSwitch.checked = initialDarkMode;
  }
  toggleDarkMode(initialDarkMode);


  toggleSwitch.addEventListener("click", () => {
    const newMode = !isDarkMode();
    toggleDarkMode(newMode);
  }); 
}

function toggleDarkMode(isDark) {
  document.body.className = isDark ? "dark-mode" : "light-mode";
  updateModeElements(isDark);
}

function updateIcon(isDark) {
  const toggleSwitch = document.getElementById("darkModeToggle");
  if (toggleSwitch && toggleSwitch.textContent) {
    toggleSwitch.textContent = isDark ? "dark_mode" : "light_mode";
  }
}

function updateModeElements(isDark) {
  const logo = document.getElementById("logo");
  const endError = document.getElementById("endError");
  const toggleLabel = document.getElementById("toggleLabel");
  const toggleSwitch = document.getElementById("darkModeToggle");
  const isCheckbox = toggleSwitch instanceof HTMLInputElement;
  const toggleLabelDark = document.getElementById("toggleLabelDark");

  if (logo) {
    logo.src = isDark ? "/static/images/logo-dark.png" : "/static/images/logo.png";
  };
  if (toggleLabel) {
    if (isCheckbox && toggleLabelDark) {
      toggleLabel.className = isDark ? "shown" : "hidden";
      toggleLabelDark.className = isDark ? "hidden" : "shown";
    } else {
      toggleLabel.textContent = isDark ? "Light mode" : "Dark mode";
    };
  };
  if (endError) {
    endError.src = isDark ? "/static/images/alert-dark.png" : "/static/images/alert--light.png";
  };
  updateIcon(isDark);
}

// Commit 4999700 has working version in case it gets fubar again