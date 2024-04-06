function getSearchParameter(name) {
  const urlParams = new URLSearchParams(window.location.search);
  const value = urlParams.get(name);
  return value
}

async function getDomain() {
    const response = await fetch('/get_domain');
    const data = await response.json();
    return data.domain;
}

async function initialize() {
    let sessionId = getSearchParameter("session_id");
    const response = await fetch(`/session-status?session_id=${sessionId}`);
    const session = await response.json();

    const domgain = await getDomain();
    const checkoutURL = `${domain}/checkout.html`

    if (!sessionId) {
        window.replace(checkoutURL)
    }
    if (session.status == 'open') {
        window.replace(checkoutURL)
    } else if (session.status == 'complete') {
        document.getElementById('success').classList.remove('hidden');
        document.getElementById('customer-email').textContent = session.customer_email;
    }
}

initialize();