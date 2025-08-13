function getCsrfToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  return meta ? meta.getAttribute('content') : '';
}

async function postJson(url, payload) {
  const resp = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken(),
    },
    body: JSON.stringify(payload),
    credentials: 'same-origin',
  });
  if (!resp.ok) {
    let errText = 'Request failed';
    try { const data = await resp.json(); errText = data.error || errText; } catch {}
    throw new Error(errText);
  }
  return resp.json();
}

function scrollChatToBottom() {
  const w = document.getElementById('chatWindow');
  if (w) { w.scrollTop = w.scrollHeight; }
}

// Simple newline-to-<br> utility when rendering strings
function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function nl2br(str) {
  return escapeHtml(str).replace(/\n/g, '<br>');
}