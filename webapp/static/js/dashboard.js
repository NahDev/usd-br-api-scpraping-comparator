const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

function fmtMoney(n) { return 'R$ ' + Number(n).toLocaleString('pt-BR', { minimumFractionDigits: 4, maximumFractionDigits: 4 }); }
function fmtPct(n) { return (n >= 0 ? '+' : '') + Number(n).toLocaleString('pt-BR', { maximumFractionDigits: 2 }) + '%'; }

// ---------- tooltip ----------
const tt = $('#tt');
function showTip(evt, html) {
  tt.innerHTML = html;
  tt.classList.add('show');
  positionTip(evt);
}
function positionTip(evt) {
  const pad = 14;
  let left = evt.clientX + pad, top = evt.clientY + pad;
  if (left + 250 > window.innerWidth) left = evt.clientX - 250 - pad;
  if (top + 100 > window.innerHeight) top = evt.clientY - 100 - pad;
  tt.style.left = left + 'px';
  tt.style.top = top + 'px';
}
function hideTip() { tt.classList.remove('show'); }

let DATA = null;

async function init() {
  const res = await fetch('/api/dados');
  DATA = await res.json();

  renderKpis();
  renderFontes();
  renderDiasImpactantes();
}

function renderKpis() {
  const { scraping, api, diferenca_percentual } = DATA.cotacoes;
  const kpis = [];

  if (scraping) {
    kpis.push({ label: 'Scraping · melhorcambio.com', value: fmtMoney(scraping.valor_compra), sub: 'dólar comercial', accent: false });
  }
  if (api) {
    kpis.push({ label: 'API · AwesomeAPI (compra)', value: fmtMoney(api.valor_compra), sub: `venda ${fmtMoney(api.valor_venda)}`, accent: false });
  }
  if (diferenca_percentual !== null && diferenca_percentual !== undefined) {
    kpis.push({ label: 'Diferença entre fontes', value: fmtPct(diferenca_percentual), sub: 'scraping vs. média da API', accent: true });
  }
  kpis.push({ label: 'Dias analisados', value: String(DATA.dias_impactantes.length), sub: 'maior variação no período', accent: true });

  $('#kpis').innerHTML = kpis.map(k => `
    <div class="kpi">
      <div class="label">${k.label}</div>
      <div class="value${k.accent ? ' accent' : ''}">${k.value}</div>
      <div class="sub">${k.sub}</div>
    </div>`).join('');
}

function renderFontes() {
  const linhas = [DATA.cotacoes.scraping, DATA.cotacoes.api].filter(Boolean);
  $('#tabela-fontes-body').innerHTML = linhas.map(l => `
    <tr>
      <td>${l.fonte}</td>
      <td>${fmtMoney(l.valor_compra)}</td>
      <td>${fmtMoney(l.valor_venda)}</td>
      <td>${l.valor_alta ? fmtMoney(l.valor_alta) : '—'}</td>
      <td>${l.valor_baixa ? fmtMoney(l.valor_baixa) : '—'}</td>
      <td>${l.variacao_percentual ? fmtPct(parseFloat(l.variacao_percentual)) : '—'}</td>
      <td>${l.coletado_em}</td>
    </tr>`).join('');
}

function renderDiasImpactantes() {
  const dias = DATA.dias_impactantes;
  if (!dias.length) {
    $('#rank-list').innerHTML = '<div class="loading">nenhum dado ainda — rode o script de correlação de notícias</div>';
    return;
  }

  $('#rank-list').innerHTML = dias.map(dia => {
    const direcaoLabel = dia.direcao === 'alta' ? 'ALTA' : 'QUEDA';
    const news = dia.noticias.length
      ? dia.noticias.map(n => `
          <div class="dia-news-item">
            <span>·</span>
            <a href="${n.link}" target="_blank" rel="noopener">${n.titulo}</a>
            <span class="dia-news-fonte">${n.fonte}</span>
          </div>`).join('')
      : '<div class="dia-sem-noticia">nenhuma notícia encontrada para esta data</div>';

    return `
      <div class="dia-card">
        <div class="dia-head">
          <span class="dia-badge">${direcaoLabel} ${fmtPct(dia.variacao_percentual)}</span>
          <span class="dia-data">${dia.data}</span>
          <span class="dia-valor">fechamento ${fmtMoney(dia.valor_fechamento)}</span>
        </div>
        <div class="dia-news">${news}</div>
      </div>`;
  }).join('');
}

init();
