window.addEventListener("DOMContentLoaded", function() {
  const headerElement = document.getElementById("header-container");
  const mobileBreakpoint = 1024;
  let lastLoadedHeader = null;

  function loadHeader() {
    const screenWidth = window.innerWidth;
  
    const shouldLoadMobile = screenWidth < mobileBreakpoint;

    if ((shouldLoadMobile && lastLoadedHeader !== "mobile" ) || (!shouldLoadMobile && lastLoadedHeader !== "desktop")) {
      lastLoadedHeader = shouldLoadMobile ? "mobile" : "desktop";
      const headerURL = shouldLoadMobile ? "/get-mobile-header" : "/get-header";

      fetch(headerURL)
        .then(response => response.text())
        .then(data => {
          headerElement.innerHTML = data;
          document.dispatchEvent(new CustomEvent("headerUpdated"));
        })
        .catch(error => console.error("Error fetching header:", error));
      }
  }

  loadHeader();

  window.addEventListener("resize", loadHeader);
});