function validateCharacterInput(input) {
  const validCharactersRegex = /^[\w\s.,;:'"!?()\-\\\n\r]*$/;
  return validCharactersRegex.test(input);
}

function validateEmailInput(input) {
  const validEmailRegex = /^(([^<>()[\\]\\\\.,;:\s@"]+(\.[^<>()[\\]\\\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,3}))$/;
  return validEmailRegex.test(input);
}


window.validateCharacterInput = validateCharacterInput;
window.validateEmailInput = validateEmailInput
