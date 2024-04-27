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