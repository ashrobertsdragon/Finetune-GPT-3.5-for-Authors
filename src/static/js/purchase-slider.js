document.getElementById("credits").oninput = function() {
  var credits = this.value;
  var price = calculatePrice(credits);
  document.getElementById("credits-value").innerText = credits;
  document.getElementById("price").innerText = "Price: $" + price;
};

function calculatePrice(credits) {
  // Price structure
  switch(parseInt(credits)) {
    case 1: return 10;
    case 2: return 19;
    case 3: return 27;
    case 4: return 34;
    case 5: return 40;
    case 6: return 45;
    case 7: return 49;
    case 8: return 52;
    case 9: return 54;
    case 10: return 55;
    default: return 10; // Default to 1 credit if something goes wrong
  }
}