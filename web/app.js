const query = document.querySelector('#query');
const runButton = document.querySelector('#runButton');
const trace = document.querySelector('#trace');
const resultSection = document.querySelector('#resultSection');
let selectedMode = 'auto';
let latestLatex = '';

document.querySelectorAll('.mode').forEach(button => button.addEventListener('click', () => {
  document.querySelector('.mode.active').classList.remove('active'); button.classList.add('active'); selectedMode = button.dataset.mode;
}));

function renderTrace(steps) {
  trace.innerHTML = steps.map((step, index) => `<div class="trace-step"><div class="step-number">0${index + 1}</div><div><div class="step-title">${step.label}</div><div class="step-detail">${step.detail}</div></div><div class="step-time">${step.duration_ms}ms</div></div>`).join('');
}
function renderSources(sources) {
  document.querySelector('#sourceCount').textContent = String(sources.length).padStart(2, '0');
  document.querySelector('#sources').innerHTML = sources.length ? sources.map(source => `<article class="source"><div class="source-title">${source.title}</div><div class="source-meta">${source.kind} · ${Math.round(source.relevance * 100)}% match</div><div class="source-excerpt">${source.excerpt}</div></article>`).join('') : '<div class="source"><div class="source-excerpt">No matching local evidence. Add a document or configure a remote index.</div></div>';
}
async function run() {
  const text = query.value.trim(); if (text.length < 3) return;
  runButton.disabled = true; runButton.querySelector('span').textContent = 'Thinking…';
  try {
    const response = await fetch('/api/solve', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({query:text, mode:selectedMode})});
    if (!response.ok) throw new Error('The graph returned an error.');
    const data = await response.json(); renderTrace(data.steps); document.querySelector('#duration').textContent = `${data.duration_ms}ms total`;
    document.querySelector('#answer').textContent = data.answer; latestLatex = data.latex;
    const badge = document.querySelector('#verificationBadge'); badge.textContent = data.verification.status; badge.className = `badge ${data.verification.status === 'verified' ? '' : 'partial'}`;
    document.querySelector('#modelLabel').textContent = data.model; renderSources(data.sources); resultSection.classList.remove('hidden');
  } catch (error) { trace.innerHTML = `<div class="empty-trace">${error.message}</div>`; } finally { runButton.disabled = false; runButton.querySelector('span').textContent = 'Run graph'; }
}
runButton.addEventListener('click', run);
query.addEventListener('keydown', event => { if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') run(); });
document.querySelector('#copyLatex').addEventListener('click', async () => { await navigator.clipboard.writeText(latestLatex); document.querySelector('#copyLatex').textContent = 'Copied'; setTimeout(() => document.querySelector('#copyLatex').textContent = 'Copy LaTeX', 1400); });
document.querySelector('#downloadLatex').addEventListener('click', () => { const blob = new Blob([latestLatex], {type:'application/x-tex'}); const link = document.createElement('a'); link.href = URL.createObjectURL(blob); link.download = 'eulergraph-derivation.tex'; link.click(); URL.revokeObjectURL(link.href); });
fetch('/api/health').then(response => response.json()).then(data => { document.querySelector('#healthText').textContent = `${data.documents} sources indexed · ${data.llm}`; }).catch(() => { document.querySelector('#healthText').textContent = 'api unavailable'; });
