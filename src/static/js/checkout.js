// This is your test publishable API key.
const stripe = Stripe("pk_test_51Nyon4L0Xe7lwg06F5bQuuCa3GunHhGCFSNCyeYQbOVEcX8sItCXZHSk1cfUHsea9U9T8c4RnNEAgzVgmQ6RrjsF00bLEwcaux");

initialize();

// Create a Checkout Session as soon as the page loads
async function initialize() {
    const response = await fetch("/create-checkout-session", {
        method: "POST",
    });

    const { clientSecret } = await response.json();

    const checkout = await stripe.initEmbeddedCheckout({
        clientSecret,
    });

    // Mount Checkout
    checkout.mount('#checkout');
}