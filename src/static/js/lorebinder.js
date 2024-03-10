document.addEventListener("DOMContentLoaded", function() {
  var isFirstPersonCheckbox = document.getElementById("id_is_first_person");
  var narratorFieldContainer = document.getElementById("id_narrator_name").closest(".form-group");

  // Toggle narrator name field based on checkbox
  function toggleNarratorField() {
    narratorFieldContainer.style.display = isFirstPersonCheckbox.checked ? "" : "none";
  }
  isFirstPersonCheckbox.addEventListener("change", toggleNarratorField);
  toggleNarratorField();

  // Function to handle multi-value inputs for character attributes
  function handleMultiValueInput(inputFieldId, storageFieldId) {
    var inputField = document.getElementById(inputFieldId);
    var storageField = document.getElementById(storageFieldId);
    var itemList = document.createElement("ul");
    storageField.parentNode.insertBefore(itemList, storageField.nextSibling);
    inputField.addEventListener("keypress", function(e) {
      if (e.key === "Enter") {
        e.preventDefault(); // Prevent form submission on Enter
        var itemValue = inputField.value.trim();
        if (itemValue) {
          var item = document.createElement("li");
          item.textContent = itemValue;
          itemList.appendChild(item);
          storageField.value += itemValue + ","; // Store the item in a hidden field as a comma-separated list
          inputField.value = ""; // Clear input for next entry
        }
      }
    });
  }

  handleMultiValueInput("id_character_attributes", "storage_character_attributes");
});
