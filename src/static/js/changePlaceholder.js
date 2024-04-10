    document.addEventListener("DOMContentLoaded", function() {
      var selectElement = document.getElementById('id_chunk_type');
      selectElement.addEventListener('change', function() {
        // Check if the current value is not the placeholder
        if(this.value !== '') {
          // Disable or remove the placeholder option
          this.options[0].disabled = true;
        }
      });
    });