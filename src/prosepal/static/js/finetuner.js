    var continuePolling = true;
    function fetchStatusUpdate() {
      if (!continuePolling) {
        return; // Stop the function from running if polling should not continue
      }
      const userFolder = sessionStorage.getItem('userFolder');
      fetch('/status', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_folder: userFolder }),
      })
      .then(response => response.json())
      .then(data => {
        document.getElementById("statusMessage").innerHTML = data.status;
        if (!data.status.includes("Download")) { // Check if the status is not the final one
          setTimeout(fetchStatusUpdate, 1000);
        }
      })
      .catch(error => console.error('Error fetching status:', error));
    }
    function showErrorModal() {
      var modal = document.getElementById("errorModal");
      modal.style.display = "block";
    }

    document.addEventListener("DOMContentLoaded", function() {
      var form = document.querySelector("form.box");
      form.onsubmit = function(e) {
        e.preventDefault();  // Prevent the normal form submission

        var formData = new FormData(form);

        fetch("/finetune", {
          method: "POST",
          body: formData
        })
        .then(response => {
          const contentType = response.headers.get("Content-Type");
          if (!contentType || !contentType.includes("application/json")) {
            throw new Error("Received non-JSON response from server");
          }
          return response.json().then(data => {
            if (!response.ok) {
              throw new Error(data.error || `Server responded with status ${response.status}`);
            }
            return data;  // Proceed with normal processing for successful response
          });
        })
        .then(data => {
          sessionStorage.setItem('userFolder', data.user_folder);
          var statusContainer = document.getElementById("status"); // Get the existing "status" element
          document.querySelector(".form-container form.box").style.display = "none"; // Hide the form
          statusContainer.style.display = "block"; // Show the status container
          var statusMessageElement = statusContainer.querySelector("p#statusMessage");
          statusMessageElement.innerHTML = "Processing...";
          fetchStatusUpdate();
        })
        .catch(error => {
          console.error('Error:', error);
          document.getElementById("errorMessage").innerText = error.message;
          showErrorModal();
        });
      };
    });
