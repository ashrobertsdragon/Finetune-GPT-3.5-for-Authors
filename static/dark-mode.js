document.addEventListener('DOMContentLoaded', (event) => {
  const toggleSwitch = document.getElementById('darkModeToggle');
  const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)");

  function updateModeElements() {
    logo.src = document.body.classList.contains("dark-mode") ? 'static/logo-dark.png' : 'static/logo.png';
    toggleLabel.textContent = document.body.classList.contains("dark-mode") ? "Light mode" : "Dark mode";
    const endError = document.getElementById('endError');
    if (endError) {
      endError.src = document.body.classList.contains("dark-mode") ? "static/alert-dark.png" : "static/alert-light.png";
    }
  }

  // Set the initial mode
  if (prefersDarkScheme.matches) {
    toggleSwitch.checked = true;
    document.body.classList.add("dark-mode");
    document.body.classList.remove("light-mode");
  } else {
    document.body.classList.add("light-mode");
    document.body.classList.remove("dark-mode");
  }
  updateModeElements();

  // Listen for toggle switch
  toggleSwitch.addEventListener('change', () => {
    document.body.classList.toggle("dark-mode");
    document.body.classList.toggle("light-mode");
    updateModeElements();
  });
})