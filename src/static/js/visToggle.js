function toggleVisibility() {
  var apiKeyInput = document.getElementById("user_key");
  var passwordInput = document.getElementById("id_password");

  var inputElement = apiKeyInput ? apiKeyInput : passwordInput;
  if (inputElement) {
    var currentType = inputElement.getAttribute("type");
    inputElement.setAttribute("type", currentType === "password" ? "text" : "password");
    
    var visibilitySpan = document.getElementById("eye");
    if (visibilitySpan) {
      visibilitySpan.textContent = currentType === "password" ? "visibility_off" : "visibility";
    }
  }
}
