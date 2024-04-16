document.addEventListener("DOMContentLoaded", () => {
  const closeIcon = document.querySelector('.close-icon');
  const flashModal = document.querySelector('.flash-modal');
  const errorModal = document.querySelector('.error-modal');

  let modal = flashModal || errorModal;

  if (closeIcon && modal) {
    closeIcon.addEventListener('click', () => {
      modal.style.display = 'none';
    });
  };
});