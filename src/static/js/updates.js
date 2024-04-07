const closeButton = document.getElementById("close");
const parentDiv = closeButton.parentElement;

closeButton.addEventListener("click", function() {
  parentDiv.classList.remove("shown");
  parentDiv.classList.add("hidden");
});