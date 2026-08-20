const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

const STATUS_LABEL = { ocioso: 'Ocioso', rodando: 'Rodando…', sucesso: 'Sucesso', erro: 'Erro' };

let intervaloAtual = null;

function fmtDuracao(segundos) {
  if (segundos === null || segundos === undefined) return '—';
  if (segundos < 60) return segundos.toFixed(1) + 's';
  const min = Math.floor(segundos / 60), seg = Math.round(segundos % 60);
  return `${min}m${seg}s`;
}

function renderRobos(robos) {
  $('#robo-grid').innerHTML = robos.map(r => `
    <div class="robo-card" data-id="${r.id}">
      <div class="robo-card-head">
        <div>
          <div class="robo-name">${r.nome}</div>
          <div class="robo-desc">${r.descricao}</div>
        </div>
        <div class="pill ${r.status}">${STATUS_LABEL[r.status] || r.status}</div>
      </div>

      <div class="robo-meta">
        <div><span class="k">Iniciado em</span><span class="v">${r.iniciado_em || '—'}</span></div>
        <div><span class="k">Duração</span><span class="v">${fmtDuracao(r.duracao_segundos)}</span></div>
        <div><span class="k">Código de saída</span><span class="v">${r.codigo_saida === null ? '—' : r.codigo_saida}</span></div>
        <div><span class="k">Saída (data/)</span><span class="v">${r.arquivo_existe ? r.arquivo_atualizado_em : 'ainda não gerada'}</span></div>
      </div>

      <button class="btn-rodar" data-id="${r.id}" ${r.status === 'rodando' ? 'disabled' : ''}>
        ${r.status === 'rodando' ? 'Rodando…' : 'Rodar agora'}
      </button>

      <div class="robo-log">${(r.log || []).map(escapeHtml).join('\n')}</div>
    </div>`).join('');

  $$('.btn-rodar').forEach(btn => btn.addEventListener('click', () => rodarRobo(btn.dataset.id)));
}

function escapeHtml(texto) {
  return texto.replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
}

async function carregarStatus() {
  const res = await fetch('/api/robo/status');
  const robos = await res.json();
  renderRobos(robos);

  const algumRodando = robos.some(r => r.status === 'rodando');
  ajustarPolling(algumRodando);
}

function ajustarPolling(rapido) {
  const intervalo = rapido ? 1500 : 8000;
  if (intervaloAtual && intervaloAtual.intervalo === intervalo) return;
  if (intervaloAtual) clearInterval(intervaloAtual.id);
  const id = setInterval(carregarStatus, intervalo);
  intervaloAtual = { id, intervalo };
}

async function rodarRobo(id) {
  const res = await fetch(`/api/robo/rodar/${id}`, { method: 'POST' });
  if (!res.ok) {
    const erro = await res.json().catch(() => ({}));
    alert(erro.erro || 'Não foi possível iniciar o robô.');
    return;
  }
  carregarStatus();
}

carregarStatus();
