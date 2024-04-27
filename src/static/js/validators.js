function validateCharacterInput(input) {
  const validCharactersRegex = /^[\w\s.,;:'"!?()\-\\\n\r]*$/;
  return validCharactersRegex.test(input);
}

function validateEmailInput(input) {
  const validEmailRegex = /^(([^<>()[\\]\\\\.,;:\s@"]+(\.[^<>()[\\]\\\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,3}))$/;
  return validEmailRegex.test(input);
}

function displayMessage(message, type) {
  const messageModal = document.getElementById("modal-container")
  const messageContainer = document.getElementById("message-container")
  messageContainer.textContent = message;
  messageContainer.classList.remove("error", "warning", "success");
  messageContainer.classList.add(type);
  messageModal.classList.remove("hidden")
  messageModal.classList.add("shown")
}

window.validateCharacterInput = validateCharacterInput;
window.validateEmailInput = validateEmailInput
window.displayMessage = displayMessage