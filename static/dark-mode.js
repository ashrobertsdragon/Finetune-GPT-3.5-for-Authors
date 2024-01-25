document.addEventListener('DOMContentLoaded', (event) => {
  const toggleSwitch = document.getElementById('darkModeToggle');
  const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)");

  function updateLogo() {
    if (document.body.classList.contains("dark-mode")) {
      logo.src = 'static/logo-dark.png';
    } else {
      logo.src = 'static/logo.png';
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
  updateLogo();

  // Listen for toggle switch
  toggleSwitch.addEventListener('change', () => {
    document.body.classList.toggle("dark-mode");
    document.body.classList.toggle("light-mode");
    updateLogo();
  });
})