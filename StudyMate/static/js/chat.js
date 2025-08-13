(function(){
  const uploadBtn = document.getElementById('uploadBtn');
  const pdfInput = document.getElementById('pdfInput');
  const uploadStatus = document.getElementById('uploadStatus');
  const chatWindow = document.getElementById('chatWindow');
  const userInput = document.getElementById('userInput');
  const sendBtn = document.getElementById('sendBtn');

  let currentFileId = null;
  let currentExam = 'GATE';

  if (uploadBtn && pdfInput) {
    uploadBtn.addEventListener('click', () => pdfInput.click());
    pdfInput.addEventListener('change', async () => {
      if (!pdfInput.files || pdfInput.files.length === 0) return;
      const file = pdfInput.files[0];
      if (file.type !== 'application/pdf') {
        alert('Please select a PDF file.');
        return;
      }
      try {
        uploadStatus.textContent = 'Uploading...';
        const formData = new FormData();
        formData.append('file', file);
        const resp = await fetch('/upload-pdf', {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCsrfToken(),
          },
          body: formData,
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.error || 'Upload failed');
        currentFileId = data.fileId;
        uploadStatus.textContent = `Uploaded: ${data.originalFilename}`;
      } catch (e) {
        uploadStatus.textContent = '';
        alert(e.message || 'Upload failed');
      } finally {
        pdfInput.value = '';
      }
    });
  }

  // Action buttons
  document.querySelectorAll('[data-action]').forEach(btn => {
    btn.addEventListener('click', () => handleAction(btn.getAttribute('data-action')));
  });

  // Competitive exam selection
  document.querySelectorAll('.exam-option').forEach(a => {
    a.addEventListener('click', (e) => {
      e.preventDefault();
      currentExam = a.getAttribute('data-exam') || 'GATE';
      handleAction('competitive');
    });
  });

  sendBtn.addEventListener('click', () => handleAction('custom'));
  userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') handleAction('custom');
  });

  async function handleAction(action) {
    const text = userInput.value.trim();
    if (action === 'custom' && !text) {
      userInput.focus();
      return;
    }

    // Render user message
    const userMsg = document.createElement('div');
    userMsg.className = 'chat-message user';
    userMsg.innerHTML = `<div class="bubble">${action === 'custom' ? escapeHtml(text) : labelForAction(action)}</div>`;
    chatWindow.appendChild(userMsg);
    scrollChatToBottom();

    // Placeholder AI bubble
    const aiMsg = document.createElement('div');
    aiMsg.className = 'chat-message ai';
    aiMsg.innerHTML = `<div class="bubble">Thinking...</div>`;
    chatWindow.appendChild(aiMsg);
    scrollChatToBottom();

    try {
      const payload = {
        action,
        text,
        fileId: currentFileId,
        exam: currentExam,
      };
      const data = await postJson('/process-request', payload);
      const contentHtml = nl2br(data.response || '');
      aiMsg.innerHTML = `<div class="bubble">${contentHtml}</div>
        <div class="download-links">
          <a href="/download/${data.aiMessageId}?format=txt" class="me-2"><i class="bi bi-file-text"></i> TXT</a>
          <a href="/download/${data.aiMessageId}?format=pdf"><i class="bi bi-file-earmark-pdf"></i> PDF</a>
        </div>`;
    } catch (e) {
      aiMsg.innerHTML = `<div class="bubble">Error: ${escapeHtml(e.message || 'Failed')} </div>`;
    } finally {
      if (action === 'custom') userInput.value = '';
      scrollChatToBottom();
    }
  }

  function labelForAction(action) {
    switch(action) {
      case 'summarize': return 'Please summarize the uploaded content';
      case 'flashcards': return 'Generate flashcards from the uploaded content';
      case 'competitive': return `Create ${currentExam} MCQs from the uploaded content`;
      default: return 'Request';
    }
  }
})();