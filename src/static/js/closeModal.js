const closeIcon = document.querySelector('.close-icon');
const flashModal = document.querySelector('.flash-modal');
const errorModal = document.querySelector('.error-modal');

const modal = flashModal || errorModal;

closeIcon.addEventListener('click', () => {
  modal.style.display = 'none';
});