// Fetch publishable key
async function fetchPublishableKey() {
  const response = await fetch('/get_publishable_key');
  const data = await response.json();
  return data.publishable_key;
}

function getUrlParameter(name) {
  const searchParams = new URLSearchParams(window.location.search);
  const value = searchParams.get(name);
  return value ? parseInt(value, 10) : null; // Ensuring the value is treated as an integer
}

async function initialize() {
  const publishableKey = await fetchPublishableKey();
  const stripe = Stripe(publishableKey);

  let numCredits = getUrlParameter('num_credits');

  // Validation
  if (!numCredits || numCredits < 1 || numCredits > 10) {
    // Handle invalid input (e.g., display an error message)
    alert("Invalid number of credits. Please enter a value between 1 and 10.");
    return;
  }

  const response = await fetch("/create_checkout_session", {
      method: "POST",
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ num_credits: numCredits }),
  });

  const { clientSecret } = await response.json();

  const checkout = await stripe.initEmbeddedCheckout({
      clientSecret,
  });

  checkout.mount('#checkout');
}

initialize();