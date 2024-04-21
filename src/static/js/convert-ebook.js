document.addEventListener("DOMContentLoaded", (event) => {
  const form = document.getElementById("conversionForm");
  const loadingMessage = document.getElementById("loadingMessage");
  const titleField = form.querySelector("input[name='title']");
  const fileUploader = form.querySelector("input[name='ebook']");
  const formActionUrl = form.action;

  form.addEventListener("submit", (e) => {
    loadingMessage.style.display = "block";

    const formData = new FormData(form);
    fetch(formActionUrl, {
      method: "POST",
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
      console.error("Error:", error);
      alert(error.error);
    })
    .finally(() => {
      titleField.value = "";
      fileUploader.value = "";
      loadingMessage.style.display = "none";
    })
  })
});






;