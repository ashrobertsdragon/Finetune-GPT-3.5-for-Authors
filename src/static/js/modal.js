document.addEventListener("DOMContentLoaded", () => {
  const closeIcon = document.querySelector('.close-icon');
  const flashModal = document.querySelector('.flash-modal');
  const errorModal = document.querySelector('.error-modal');
  const messageModal = document.querySelector('.message-modal');

  let modal = flashModal || errorModal || messageModal;

  if (closeIcon && modal) {
    closeIcon.addEventListener('click', () => {
      modal.classList.remove("shown");
      modal.classList.add("hidden");
    });
  };
});

function displayMessage(message, type) {
  const messageModal = document.getElementById("modal-container")
  const messageContainer = document.getElementById("message-container")
  messageContainer.textContent = message;
  messageContainer.classList.remove("error", "warning", "success");
  messageContainer.classList.add(type);
  messageModal.classList.remove("hidden")
  messageModal.classList.add("shown")
}

function handleAPIResponse(data) {
  messageContainer.innerHTML = "";
  displayMessage(data.message, data.status);
}

window.displayMessage = displayMessage
window.handleAPIResponse = handleAPIResponse