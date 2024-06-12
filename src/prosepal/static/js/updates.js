const closeButton = document.getElementById("close");
const parentDiv = document.getElementById("parentDiv");

if (closeButton && parentDiv) {
  closeButton.addEventListener("click", function() {
    parentDiv.classList.remove("shown");
    parentDiv.classList.add("hidden");
  });
}
