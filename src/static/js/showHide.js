function showSection(sectionName) {
  const sections = document.querySelectorAll('[data-section]');
  sections.forEach(section => {
    if (section.dataset.section === sectionName) {
      section.classList.remove('hidden');
      section.classList.add('shown');
    } else {
      section.classList.add('hidden');
      section.classList.remove('shown');
    }
  });
}

document.addEventListener('DOMContentLoaded', () => {
  const urlParams = new URLSearchParams(window.location.search);
  // Immediately show the active section based on the URL, or default to the first
  const activeSection = urlParams.get('section') || document.querySelector('[data-section]').dataset.section;
  showSection(activeSection);

  document.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', (event) => {
      event.preventDefault();
      const sectionName = new URLSearchParams(event.currentTarget.search).get('section');
      showSection(sectionName);
      window.history.pushState({}, '', event.currentTarget.href);
    });
  });
});
