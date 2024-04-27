document.addEventListener("DOMContentLoaded", () => {
  var isFirstPersonCheckbox = document.getElementById("is-first-person");
  var narratorFieldContainer = document.getElementById("narrator-container");

  // Toggle narrator name field based on checkbox
  function toggleNarratorField() {
    showNarratorField = isFirstPersonCheckbox.checked;
    narratorFieldContainer.style.display = showNarratorField ? "flex" : "none";

  };
  isFirstPersonCheckbox.addEventListener("change", toggleNarratorField);
  toggleNarratorField();

  // Function to handle multi-value inputs for attributes
  function handleMultiValueInput(inputFieldId, tagDisplayContainerId) {
    const inputField = document.getElementById(inputFieldId);
    const tagDisplayContainer = document.getElementById(tagDisplayContainerId);
    const messageContainer = document.getElementById("message-container")

    const tempSpan = document.createElement('span');
    tempSpan.classList.add("temp-span");
    tagDisplayContainer.appendChild(tempSpan);

    inputField.addEventListener("keyup", function(e) {
      if (e.key === "Enter") {
        e.key = ",";
      };

      const inputValue = inputField.value;
      const lastCommaIndex = inputValue.lastIndexOf(",", inputValue.length - 2) + 1;
      const currentInput = inputValue.slice(lastCommaIndex).trim();

      if (validateCharacterInput(currentInput)) {
        const existingTags = tagDisplayContainer.querySelectorAll(".tag");
        if (existingTags.length >= 6) {
          displayMessage("Maximum number of tags reached.", "error");
        } else if (e.key === "," && currentInput) {
          const tagElement = createTag(currentInput);
          tempSpan.textContent = "";
          tagDisplayContainer.insertBefore(tagElement, tempSpan);
          if (existingTags.length < 6) {
            inputField.value = inputValue + " ";
          } else {
            inputField.value.slice(0, -1);
          }
          messageContainer.textContent = "";
        } else {
          tempSpan.textContent = currentInput;
          messageContainer.textContent = "";
        }
      } else {
        displayMessage("Invalid input. Please enter valid characters.", "error");
        inputField.value = inputValue.slice(0, -1);
      };
    });

    function createTag(tag) {
      const tagElement = document.createElement("span");
      tag = tag.replace(/,$/, '').trim();
      tagElement.classList.add("tag");
      tagElement.textContent = tag;

      const closeButton = document.createElement("span");
      closeButton.classList.add("remove-tag", "material-symbols-outlined");
      closeButton.innerHTML = "close";
      closeButton.addEventListener("click", () => removeTag(tagElement));

      tagElement.appendChild(closeButton);
      return tagElement;
    };

    function removeTag(tagElement) {
      const tagText = tagElement.textContent.replace("close", "").trim();

      const tags = inputField.value.split(",").map(tag => tag.trim());
      const indexToRemove = tags.indexOf(tagText);

      if (indexToRemove > -1) {
        tags.splice(indexToRemove, 1);
        inputField.value = tags.join(",");
      };
      
      tagElement.remove();
    };
  };

  handleMultiValueInput("character-attributes", "character-attributes-tags");
  handleMultiValueInput("other-attributes", "other-attributes-tags");
});
