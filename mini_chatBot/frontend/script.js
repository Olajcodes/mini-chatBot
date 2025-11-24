const modeToggle = document.getElementById('modeToggle');
const keyMode = document.getElementById('keyMode');
const passwordMode = document.getElementById('passwordMode');
const apiKey = document.getElementById('apiKey');
const adminPassword = document.getElementById('adminPassword');
const messages = document.getElementById('messages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');

modeToggle.addEventListener('change', () => {
  const usePassword = modeToggle.checked;
  keyMode.classList.toggle('hidden', usePassword);
  passwordMode.classList.toggle('hidden', !usePassword);
});

function formatTimestamp(ts) {
  const d = new Date(ts);
  const date = d.toISOString().slice(0, 10);     // YYYY-MM-DD
  const time = d.toTimeString().slice(0, 8);     // HH:MM:SS
  return `${date}: ${time}`;
}

function addMessage(role, text, ts) {
  const div = document.createElement('div');
  div.className = `msg ${role}`;

  const formatted = formatTimestamp(ts);

  div.innerHTML = `
    <div class="bubble">${escapeHtml(text)}</div>
    <div class="meta">${role === 'user' ? 'Sent' : 'Received'} at ${formatted}</div>
  `;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

function escapeHtml(s) {
  return s.replace(/[&<>"]/g, c => (
    {'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;'}[c]
  ));
}

// --------------------------
// Thinking Animation
// --------------------------
let thinkingDiv = null;

function showThinking() {
  thinkingDiv = document.createElement("div");
  thinkingDiv.className = "msg bot thinking";
  thinkingDiv.innerHTML = `
    <div class="bubble">
      <span class="dot"></span>
      <span class="dot"></span>
      <span class="dot"></span>
    </div>
    <div class="meta">Thinking...</div>
  `;
  messages.appendChild(thinkingDiv);
  messages.scrollTop = messages.scrollHeight;
}

function removeThinking() {
  if (thinkingDiv) thinkingDiv.remove();
  thinkingDiv = null;
}

// --------------------------
// Send Function
// --------------------------
async function send() {
  const text = messageInput.value.trim();
  if (!text) return;

  const usePasswordMode = modeToggle.checked;
  const body = { message: text };

  if (usePasswordMode) {
    const pwd = adminPassword.value.trim();
    if (!pwd) { alert('Enter admin password'); return; }
    body.use_password_mode = true;
    body.password = pwd;
  } else {
    const key = apiKey.value.trim();
    if (!key) { alert('Enter OpenAI API key'); return; }
    body.api_key = key;
  }

  sendBtn.disabled = true;
  messageInput.disabled = true;

  // Show "bot is thinking"
  showThinking();

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });

    const data = await res.json();

    // Remove thinking animation
    removeThinking();

    if (data.error) {
      alert(data.error);
    } else {
      addMessage('user', text, data.request_ts || new Date().toISOString());
      addMessage('bot', data.response, data.response_ts || new Date().toISOString());
      messageInput.value = '';
    }

  } catch (e) {
    removeThinking();
    alert('Network error');

  } finally {
    sendBtn.disabled = false;
    messageInput.disabled = false;
    messageInput.focus();
  }
}

sendBtn.addEventListener('click', send);
messageInput.addEventListener('keydown', e => {
  if (e.key === 'Enter') send();
});
