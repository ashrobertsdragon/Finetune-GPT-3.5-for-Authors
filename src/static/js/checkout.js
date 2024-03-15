// Fetch publishable key
async function fetchPublishableKey() {
  const response = await fetch('/get_publishable_key');
  const data = await response.json();
  return data.publishable_key;
}

initialize();

async function initialize() {
    const publishableKey = await fetchPublishableKey();
    const stripe = Stripe(publishableKey);

    const response = await fetch("/create-checkout-session", {
        method: "POST",
    });

    const { clientSecret } = await response.json();

    const checkout = await stripe.initEmbeddedCheckout({
        clientSecret,
    });

    checkout.mount('#checkout');
}