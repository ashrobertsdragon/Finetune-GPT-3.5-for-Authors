document.addEventListener('headerUpdated', initializeDarkMode);

function initializeDarkMode() {
  const toggleSwitch = document.getElementById('darkModeToggle');
  if (!toggleSwitch) return;

  const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)");
  if (prefersDarkScheme.matches) {
    toggleSwitch.checked = true;
    toggleDarkMode(true);
  } else {
    toggleSwitch.checked = false;
    toggleDarkMode(false);
  }

  toggleSwitch.addEventListener('change', () => {
    toggleDarkMode(toggleSwitch.checked);
  });
}

function toggleDarkMode(enable) {
  document.body.classList.toggle("dark-mode", enable);
  document.body.classList.toggle("light-mode", !enable);
  updateModeElements(enable);
}

function updateModeElements(isDarkMode) {
  const logo = document.getElementById('logo');
  const toggleLabel = document.getElementById('toggleLabel');
  const spanText = document.getElementById('darkModeToggle')
  const endError = document.getElementById('endError');

  if (logo) {
    logo.src = isDarkMode ? '/static/images/logo-dark.png' : '/static/images/logo.png';
  };
  if (spanText && spanText.textContent) {
    spanText.textContent = isDarkMode ? "light_mode" : "dark_mode";
  }
  if (toggleLabel) {
    toggleLabel.textContent = isDarkMode ? "Light mode" : "Dark mode";
  };
  if (endError) {
    endError.src = isDarkMode ? "/static/images/alert-dark.png" : "/static/images/alert-light.png";
  }
}
