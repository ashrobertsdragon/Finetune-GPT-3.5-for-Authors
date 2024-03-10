document.addEventListener('DOMContentLoaded', (event) => {
  const form = document.getElementById('conversionForm');
  const loadingMessage = document.getElementById('loadingMessage');
  const titleField = form.querySelector('input[name="title"]');
  const fileUploader = form.querySelector('input[name="ebook"]');

  form.addEventListener('submit', (e) => {
    loadingMessage.style.display = 'block';

    // Clear specific fields after a short delay to allow form submission
    setTimeout(() => {
      titleField.value = '';
      fileUploader.value = '';
      loadingMessage.style.display = 'none';
    }, 100); // Adjust the delay as needed
  });
});
fetch('/convert-ebook', {
  method: 'POST',
  body: formData
})
.then(response => {
  if (!response.ok) {
    throw response.json();
  }
  return response.json();
})
.then(data => {
})
.catch(async (errorPromise) => {
  const error = await errorPromise;
  console.error('Error:', error);
  alert(error.error);
});