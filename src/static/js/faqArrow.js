document.addEventListener('DOMContentLoaded', (event) => {
  const faqQuestions = document.querySelectorAll('.faq-question');
  faqQuestions.forEach(question => {
    question.addEventListener('click', () => {
      const answer = question.nextElementSibling;
      const icon = question.querySelector('.material-symbols-outlined');

      if (answer && icon) {
        if (answer.style.maxHeight) {
          answer.style.maxHeight = null;
          icon.textContent = 'expand_more';
        } else {
          answer.style.maxHeight = answer.scrollHeight + "px";
          icon.textContent = 'expand_less'; 
        }
      };
      question.classList.toggle('active');
    });
  });
});