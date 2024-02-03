document.addEventListener('DOMContentLoaded', (event) => {
  const toggleSwitch = document.getElementById('darkModeToggle');
  const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)");

  function updateModeElements() {
    if (document.body.classList.contains("dark-mode")) {
      logo.src = 'static/logo-dark.png';
      endError.src = "static/alert-dark.png";
      toggleLabel.textContent = "Light mode";
    } else {
      logo.src = 'static/logo.png';
      endError.src = "static/alert-light.png"
      toggleLabel.textContent = "Dark mode";
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