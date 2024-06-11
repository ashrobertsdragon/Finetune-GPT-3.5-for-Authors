    document.addEventListener("DOMContentLoaded", function() {
      var selectElement = document.getElementById('chunk_type');
      selectElement.addEventListener('placeholder', function() {
        // Check if the current value is not the placeholder
        if(this.value !== '') {
          // Disable or remove the placeholder option
          this.options[0].disabled = true;
        }
      });
    });