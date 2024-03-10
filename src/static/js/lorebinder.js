document.addEventListener("DOMContentLoaded", function() {
  var isFirstPersonCheckbox = document.getElementById("is_first_person");
  var narratorFieldContainer = document.getElementById("narrator");

  // Toggle narrator name field based on checkbox
  function toggleNarratorField() {
    narratorFieldContainer.style.display = isFirstPersonCheckbox.checked ? "block" : "none";
  }
  isFirstPersonCheckbox.addEventListener("change", toggleNarratorField);
  toggleNarratorField();

  // Function to handle multi-value inputs for attributes
  function handleMultiValueInput(inputFieldId, storageFieldId) {
    var inputField = document.getElementById(inputFieldId);
    var storageField = document.getElementById(storageFieldId);
    var itemList = document.createElement("ul");
    itemList.classList.add("attributes-list");
    storageField.parentNode.insertBefore(itemList, storageField.nextSibling);
    inputField.addEventListener("keypress", function(e) {
      if (e.key === "Enter") {
        e.preventDefault(); // Prevent form submission on Enter
        var itemValue = inputField.value.trim();
        if (itemValue) {
          var item = document.createElement("li");
          item.textContent = itemValue;
          itemList.appendChild(item);
          // Update the hidden field to store the list as a JSON array
          var items = storageField.value ? JSON.parse(storageField.value) : [];
          items.push(itemValue);
          storageField.value = JSON.stringify(items);

          inputField.value = ""; // Clear input for next entry
        }
      }
    });
  }

  handleMultiValueInput("character_attributes_input", "character_attributes");
  handleMultiValueInput("other_attributes_input", "other_attributes");
});
