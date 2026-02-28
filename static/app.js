const API_BASE = '';

const questionInput = document.getElementById('questionInput');
const submitBtn = document.getElementById('submitBtn');
const schemaToggle = document.getElementById('schemaToggle');
const schemaSection = document.getElementById('schemaSection');
const schemaContent = document.getElementById('schemaContent');
const sqlBlock = document.getElementById('sqlBlock');
const sqlContent = document.getElementById('sqlContent');
const tableBlock = document.getElementById('tableBlock');
const resultTable = document.getElementById('resultTable');
const loadingBlock = document.getElementById('loadingBlock');
const errorBlock = document.getElementById('errorBlock');
const errorText = document.getElementById('errorText');

function hideAllResults() {
  sqlBlock.classList.add('hidden');
  tableBlock.classList.add('hidden');
  loadingBlock.classList.add('hidden');
  errorBlock.classList.add('hidden');
}

function showError(message) {
  hideAllResults();
  errorText.textContent = message;
  errorBlock.classList.remove('hidden');
}

function showResult(data) {
  hideAllResults();

  if (data.sql) {
    sqlContent.textContent = data.sql;
    sqlBlock.classList.remove('hidden');
  }

  if (data.columns && data.rows) {
    resultTable.innerHTML = '';
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    data.columns.forEach(col => {
      const th = document.createElement('th');
      th.textContent = col;
      headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    resultTable.appendChild(thead);

    const tbody = document.createElement('tbody');
    data.rows.forEach(row => {
      const tr = document.createElement('tr');
      row.forEach(cell => {
        const td = document.createElement('td');
        td.textContent = cell ?? '';
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
    resultTable.appendChild(tbody);
    tableBlock.classList.remove('hidden');
  }
}

async function submitQuery() {
  const question = questionInput.value.trim();
  if (!question) {
    showError('Please enter a question');
    questionInput.focus();
    return;
  }

  submitBtn.disabled = true;
  submitBtn.classList.add('loading');
  hideAllResults();
  loadingBlock.classList.remove('hidden');

  try {
    const res = await fetch(`${API_BASE}/api/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });

    let data;
    try {
      data = await res.json();
    } catch (e) {
      showError('The server returned an abnormal format, please check if the backend is running normally');
      return;
    }

    if (!res.ok) {
      showError(data.error || 'Request failed');
      return;
    }

    if (data.success) {
      showResult(data);
    } else {
      showError(data.error || 'Unknown error');
    }
  } catch (err) {
    const msg = err.message || String(err);
    if (msg.includes('Failed to fetch') || msg.includes('NetworkError')) {
      showError('Network error: Please ensure you access through http://127.0.0.1:5001 and have run python app.py');
    } else {
      showError('Request failed: ' + msg);
    }
  } finally {
    submitBtn.disabled = false;
    submitBtn.classList.remove('loading');
    loadingBlock.classList.add('hidden');
  }
}

async function loadSchema() {
  if (schemaContent.textContent) {
    schemaSection.classList.toggle('hidden');
    return;
  }
  try {
    const res = await fetch(`${API_BASE}/api/schema`);
    const data = await res.json();
    if (data.success) {
      schemaContent.textContent = data.schema;
      schemaSection.classList.remove('hidden');
    }
  } catch {
    schemaContent.textContent = 'Failed to load schema';
    schemaSection.classList.remove('hidden');
  }
}

submitBtn.addEventListener('click', submitQuery);
questionInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    submitQuery();
  }
});
schemaToggle.addEventListener('click', loadSchema);
