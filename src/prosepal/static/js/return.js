function getSearchParameter(name) {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(name);
}

async function getDomain() {
  const response = await fetch('/get-domain');
  const data = await response.json();
  return data.domain;
}

async function getCreditsAvailable() {
  const response = await fetch("/get-available-credits");
  const data = await response.json();
  return data.credits_available
}

async function initialize() {
  const sessionId = getSearchParameter("session_id");
  if (!sessionId) {
      const domain = await getDomain();
      window.location.replace(`${domain}/checkout.html`);
      return;
  }

  const response = await fetch(`/session-status?session_id=${sessionId}`);
  const session = await response.json();

  if (session.error || session.status === 'open') {
    const domain = await getDomain();
    window.location.replace(`${domain}/checkout.html`);
  } else if (session.status === 'complete') {
    const creditsAvailable = await getCreditsAvailable()
    document.getElementById('customer-email').textContent = session.customer_email;
    document.getElementById('credits-available').textContent = creditsAvailable;
    document.getElementById('success').classList.remove('hidden');
  }
}

initialize();