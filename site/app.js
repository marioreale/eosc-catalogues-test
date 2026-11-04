// Renders results.json, written by `catalogue-check report` in the CI run.
(function () {
  // One colour per node, stable across runs (keyed by node id).
  const NODE_COLORS = {
    'bbmri-eric': '#f472b6', 'cern': '#60a5fa', 'eosc-cz': '#f97316', 'eosc-dto': '#2dd4bf',
    'data-terra': '#a3e635', 'eosc-fi': '#38bdf8', 'panosc': '#e879f9', 'eudat': '#facc15',
    'egi': '#fb7185', 'geant': '#818cf8', 'eosc-pl': '#f43f5e', 'eosc-it': '#4ade80',
    'eosc-sk': '#c084fc', 'ebrains-ri': '#fdba74', 'life-sciences-connect': '#5eead4',
    'eosc-de': '#fcd34d',
  };
  const colorOf = (id) => NODE_COLORS[id] || '#94a3b8';
  // Node logos from https://eosc.eu/building-the-eosc-federation (EOSC Nodes tab).
  const LOGOS = new Set(['bbmri-eric', 'cern', 'eosc-cz', 'eosc-dto', 'data-terra', 'eosc-fi', 'panosc',
    'eudat', 'egi', 'geant', 'eosc-pl', 'eosc-it', 'eosc-sk']);
  const $ = (s) => document.querySelector(s);
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const initials = (name) => name.replace(/^EOSC (Node )?/, '').replace(/[()]/g, '').split(/[\s-]+/).filter(Boolean).slice(0, 2).map((w) => w[0]).join('').toUpperCase();

  const SOURCE_LABEL = { production: 'Production sheet' };

  function verdict(row) {
    const cfgOk = row.checks.every((c) => c.passed);
    const p = row.probe;
    if (!cfgOk) return { cls: 'v-fail', text: 'Config fails' };
    if (!p) return { cls: 'v-none', text: 'Not probed' };
    if (p.outcome === 'pass') return (p.observations || []).length ? { cls: 'v-warn', text: 'Up · note' } : { cls: 'v-pass', text: 'Up' };
    if (p.outcome === 'timeout') return { cls: 'v-warn', text: 'Timeout' };
    return { cls: 'v-fail', text: 'Down' };
  }

  function card(row) {
    const v = verdict(row);
    const p = row.probe;
    const checks = row.checks.map((c) =>
      `<span class="ck ${c.passed ? 'ok' : 'ko'}" title="${esc(c.label)}${c.detail ? ': ' + esc(c.detail) : ''} — ${c.passed ? 'pass' : 'FAIL'}" aria-label="${esc(c.label)}: ${c.passed ? 'pass' : 'fail'}">${c.passed ? '✓' : '✕'}</span>`).join('');
    const passed = row.checks.filter((c) => c.passed).length;

    let probe = '<span class="probe-line">Not probed in this run</span>';
    if (p) {
      const facts = Object.entries(p.facts || {}).filter(([k]) => k !== 'baseURL')
        .map(([k, val]) => `<span class="fact">${esc(k)} <b>${esc(val)}</b></span>`).join('');
      const obs = (p.observations || []).map((o) => `<div class="obs">⚠ ${esc(o)}</div>`).join('');
      probe = `<div><span class="probe-line">${esc(p.summary)}</span> <span class="t">· ${p.http_status ? 'HTTP ' + p.http_status + ' · ' : ''}${p.seconds}s</span>
        ${facts ? `<div class="facts">${facts}</div>` : ''}${obs}</div>`;
    }

    const quoted = [];
    String(row.source).split(',').map((s) => s.trim()).forEach((s) =>
      quoted.push(`<span class="q">${esc(SOURCE_LABEL[s] || s)}</span>`));
    const L = row.listed || {};
    if (L.comment) quoted.push(`<span class="q st">Comment: “${esc(L.comment)}”</span>`);
    if (L.evaluation_eosc_a) quoted.push(`<span class="q st">EOSC-A evaluation: “${esc(L.evaluation_eosc_a)}”</span>`);
    if (!L.comment && !L.evaluation_eosc_a) quoted.push('<span class="q none">No comment in the sheet</span>');

    return `<article class="card" data-node="${esc(row.node)}" style="--node:${colorOf(row.node)}">
      <div class="card-top">
        <div>
          ${LOGOS.has(row.node)
            ? `<div class="node-logo"><img src="logos/${esc(row.node)}.png" alt="${esc(row.node_name)}" loading="lazy" onerror="this.parentNode.outerHTML='<div class=&quot;node-badge&quot;>${esc(row.node_name)}</div>'"></div>`
            : `<div class="node-badge"><span class="sw" aria-hidden="true">${esc(initials(row.node_name))}</span>${esc(row.node_name)}</div>`}
          <h3>${esc(row.name)}</h3>
        </div>
        <span class="verdict ${v.cls}">${v.text}</span>
      </div>
      <div class="endpoint">${row.display_endpoint
        ? `<a href="${esc(row.display_endpoint)}" rel="noopener" target="_blank">${esc(row.display_endpoint)}</a>`
        : `<a href="${esc(p ? p.url : row.endpoint)}" rel="noopener" target="_blank">${esc(row.endpoint)}</a>`}</div>
      <div class="row"><span>Config ${passed}/${row.checks.length}</span><div class="checks">${checks}</div></div>
      <div class="row"><span>Probe</span>${probe}</div>
      <div class="row"><span>Source</span><div class="quote">${quoted.join('')}</div></div>
      ${row.note ? `<details class="note"><summary>Note</summary><p>${esc(row.note)}</p></details>` : ''}
    </article>`;
  }

  function kpi(cls, value, label, bar) {
    return `<div class="kpi ${cls}"><div class="v">${value}</div><div class="l">${label}</div>${bar || ''}</div>`;
  }

  function render(data) {
    const rows = data.catalogues;
    const svc = rows.filter((r) => r.type === 'service-catalogue');
    const rp = rows.filter((r) => r.type === 'research-product-catalogue');
    const nodes = [...new Map(rows.map((r) => [r.node, r.node_name])).entries()].sort((a, b) => a[1].localeCompare(b[1]));
    const up = rows.filter((r) => r.probe && r.probe.outcome === 'pass').length;
    const probed = rows.filter((r) => r.probe).length;
    const cfgFail = rows.filter((r) => !r.checks.every((c) => c.passed)).length;
    const t = data.tests;

    const when = new Date(data.generated);
    const whenTxt = isNaN(when) ? data.generated : when.toLocaleString('en-GB', { dateStyle: 'long', timeStyle: 'short', timeZone: 'UTC' }) + ' UTC';
    const run = data.run_url ? ` · <a href="${esc(data.run_url)}">CI run</a>` : '';
    const commit = data.commit ? ` · commit <a href="https://github.com/marioreale/eosc-catalogues-test/commit/${esc(data.commit)}"><code>${esc(data.commit.slice(0, 7))}</code></a>` : '';
    $('#meta').innerHTML = `Generated ${esc(whenTxt)}${commit}${run}`;
    $('#foot-run').innerHTML = `generated ${esc(whenTxt)}`;

    const nodeBar = '<div class="bar-mini">' + nodes.map(([id]) => `<i style="background:${colorOf(id)};width:${100 * rows.filter((r) => r.node === id).length / rows.length}%"></i>`).join('') + '</div>';
    $('#kpis').innerHTML = [
      kpi('k-svc', svc.length, 'Service Catalogues'),
      kpi('k-rp', rp.length, 'Research Product Catalogues'),
      kpi('', nodes.length, 'contributing nodes', nodeBar),
      kpi(probed && up === probed ? 'k-pass' : 'k-fail', probed ? `${up}/${probed}` : '–', 'endpoints answered the probe'),
      t ? kpi(t.failed ? 'k-fail' : 'k-pass', `${t.passed}/${t.total}`, 'tests passed' + (cfgFail ? ` · ${cfgFail} config failures` : ''))
        : kpi('', '–', 'test suite not included'),
    ].join('');
    $('#n-svc').textContent = svc.length;
    $('#n-rp').textContent = rp.length;

    $('#cards-svc').innerHTML = svc.map(card).join('') || '<p class="empty">No Service Catalogues configured.</p>';
    $('#cards-rp').innerHTML = rp.map(card).join('') || '<p class="empty">No Research Product Catalogues configured.</p>';

    // node filter
    const filter = $('#node-filter');
    filter.innerHTML = `<button class="chip all" aria-pressed="true" data-node="*">All nodes</button>` +
      nodes.map(([id, name]) => `<button class="chip" aria-pressed="true" data-node="${esc(id)}" style="--node:${colorOf(id)}">${esc(name)}</button>`).join('');
    let active = null;
    filter.addEventListener('click', (e) => {
      const b = e.target.closest('button');
      if (!b) return;
      active = b.dataset.node === '*' || active === b.dataset.node ? null : b.dataset.node;
      filter.querySelectorAll('button').forEach((x) => x.setAttribute('aria-pressed', String(!active || x.dataset.node === active || (x.dataset.node === '*' && !active))));
      document.querySelectorAll('.card').forEach((c) => { c.hidden = !!active && c.dataset.node !== active; });
      $('#n-svc').textContent = svc.filter((r) => !active || r.node === active).length;
      $('#n-rp').textContent = rp.filter((r) => !active || r.node === active).length;
    });

    // suite
    if (t) {
      $('#suite-sum').textContent = `${t.passed} passed, ${t.failed} failed, ${t.skipped} skipped, out of ${t.total} tests (pytest, same run).`;
      $('#suite-list').innerHTML = t.cases.map((c) => `<li class="${c.outcome}"><i aria-hidden="true"></i><span>${esc(c.file.replace(/^tests\./, ''))} · ${esc(c.name)}</span></li>`).join('');
    } else {
      $('#suite-sum').textContent = 'The test suite results were not included in this run.';
    }
  }

  fetch('results.json', { cache: 'no-store' })
    .then((r) => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
    .then(render)
    .catch((e) => {
      $('#meta').textContent = 'Could not load results.json (' + e.message + ').';
      $('#cards-svc').innerHTML = $('#cards-rp').innerHTML = '<p class="empty">No results available.</p>';
    });
})();
