document.addEventListener("DOMContentLoaded", function() {
  var firstInvalidInput = document.querySelector("input:invalid");
  if (firstInvalidInput) {
    firstInvalidInput.focus();
  }
});
