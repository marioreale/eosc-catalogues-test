// Renders results.json, written by `catalogue-check report` in the CI run.
(function () {
  // Palette: lively green for Service Catalogues, mild pink for Research Product
  // Catalogues, white for neutral elements. Nodes are told apart by their logos.
  const TYPE_COLORS = { 'service-catalogue': '#008691', 'research-product-catalogue': '#ff5b7f' };
  const BAR_COLORS = ['#008691', '#ff5b7f', '#ffffff'];
  // Node logos from https://eosc.eu/building-the-eosc-federation (EOSC Nodes tab).
  // A self-contained copy of the page (results/index.html) embeds the logos as data URIs.
  const logoSrc = (node) => (window.EMBEDDED_LOGOS || {})[node] || `logos/${node}.png`;
  const LOGOS = new Set(['bbmri-eric', 'cern', 'eosc-cz', 'eosc-dto', 'data-terra', 'eosc-fi', 'panosc',
    'eudat', 'egi', 'geant', 'eosc-pl', 'eosc-it', 'eosc-sk']);
  const $ = (s) => document.querySelector(s);
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const initials = (name) => name.replace(/^EOSC (Node )?/, '').replace(/[()]/g, '').split(/[\s-]+/).filter(Boolean).slice(0, 2).map((w) => w[0]).join('').toUpperCase();

  const SOURCE_LABEL = { production: 'Production sheet', 'resource-hub': 'Resource Hub' };

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
    const checks = row.checks.map((c, i) =>
      `<button type="button" class="ck ${c.passed ? 'ok' : 'ko'}" data-id="${esc(row.id)}" data-k="${i}" aria-haspopup="dialog" title="${esc(c.label)} — select for details" aria-label="${esc(c.label)}: ${c.passed ? 'pass' : 'fail'}. Show details">${c.passed ? '✓' : '✕'}</button>`).join('');
    const passed = row.checks.filter((c) => c.passed).length;

    let probe = '<span class="probe-line">Not probed in this run</span>';
    if (p) {
      const facts = Object.entries(p.facts || {}).filter(([k]) => k !== 'baseURL')
        .map(([k, val]) => `<span class="fact">${esc(k)} <b>${esc(val)}</b></span>`).join('');
      probe = `<div><span class="probe-line">${esc(p.summary)}</span> <span class="t">· ${p.http_status ? 'HTTP ' + p.http_status + ' · ' : ''}${p.seconds}s</span>
        ${facts ? `<div class="facts">${facts}</div>` : ''}</div>`;
    }

    const quoted = [];
    String(row.source).split(',').map((s) => s.trim()).forEach((s) =>
      quoted.push(`<span class="q ${s === 'resource-hub' ? 'hub' : ''}">${esc(SOURCE_LABEL[s] || s)}</span>`));
    // The sheet's comments (row.listed) stay in results.json but are not shown on the cards.

    return `<article class="card" data-node="${esc(row.node)}" style="--node:${TYPE_COLORS[row.type] || '#ffffff'}">
      <div class="card-top">
        <div>
          ${LOGOS.has(row.node)
            ? `<div class="node-logo"><img src="${esc(logoSrc(row.node))}" alt="${esc(row.node_name)}" loading="lazy" onerror="this.parentNode.outerHTML='<div class=&quot;node-badge&quot;>${esc(row.node_name)}</div>'"></div>`
            : `<div class="node-badge"><span class="sw" aria-hidden="true">${esc(initials(row.node_name))}</span>${esc(row.node_name)}</div>`}
          <h3>${esc(row.name)}</h3>
        </div>
        ${p && (p.observations || []).length
          ? `<button type="button" class="verdict verdict-btn ${v.cls}" data-note="${esc(row.id)}" aria-haspopup="dialog" title="Select to read the note">${v.text}</button>`
          : `<span class="verdict ${v.cls}">${v.text}</span>`}
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
    $('#meta').innerHTML = `Generated ${esc(whenTxt)}`;
    $('#foot-run').innerHTML = `generated ${esc(whenTxt)}${commit}${run}`;

    const nodeBar = '<div class="bar-mini">' + nodes.map(([id], i) => `<i style="background:${BAR_COLORS[i % 3]};width:${100 * rows.filter((r) => r.node === id).length / rows.length}%"></i>`).join('') + '</div>';
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

    rowsById = new Map(rows.map((r) => [r.id, r]));
    $('#cards-svc').innerHTML = svc.map(card).join('') || '<p class="empty">No Service Catalogues configured.</p>';
    $('#cards-rp').innerHTML = rp.map(card).join('') || '<p class="empty">No Research Product Catalogues configured.</p>';

    // node filter
    const filter = $('#node-filter');
    filter.innerHTML = `<button class="chip all" aria-pressed="true" data-node="*">All nodes</button>` +
      nodes.map(([id, name]) => `<button class="chip" aria-pressed="true" data-node="${esc(id)}" style="--node:#ffffff">${esc(name)}</button>`).join('');
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
      $('#suite-list').innerHTML = t.cases.map((c, i) => `<li class="${c.outcome}"><button type="button" class="test-btn" data-i="${i}" aria-haspopup="dialog" title="What this test checks"><i aria-hidden="true"></i><span>${esc(c.file.replace(/^tests\./, ''))} · ${esc(c.name)}</span><b class="info" aria-hidden="true">i</b></button></li>`).join('');
      loadDescriptions().then((d) => {
        $('#suite-list').addEventListener('click', (ev) => {
          const b = ev.target.closest('.test-btn');
          if (b) openTest(t.cases[Number(b.dataset.i)], d, b);
        });
      });
    } else {
      $('#suite-sum').textContent = 'The test suite results were not included in this run.';
    }
  }

  // Probe notes: opened from the "Up · note" badge, not shown on the card.
  function openNote(row, opener) {
    const p = row.probe || {};
    $('#nd-n').textContent = row.name;
    $('#nd-endpoint').textContent = row.endpoint;
    $('#nd-list').innerHTML = (p.observations || []).map((o) => `<li>${esc(o)}</li>`).join('');
    const declared = (p.facts || {}).baseURL;
    $('#nd-why-row').hidden = !declared;
    const dlg = $('#note-dialog');
    dlg.returnFocusTo = opener;
    dlg.showModal();
  }
  document.addEventListener('click', (ev) => {
    const b = ev.target.closest('button.verdict-btn');
    if (!b) return;
    const row = rowsById.get(b.dataset.note);
    if (row) openNote(row, b);
  });

  // Configuration-check descriptions (the ticks on each card).
  let rowsById = new Map();
  let checkInfo = null;
  function loadCheckInfo() {
    if (!checkInfo) {
      checkInfo = fetch('check-descriptions.json', { cache: 'no-store' })
        .then((r) => (r.ok ? r.json() : { checks: {} }))
        .catch(() => ({ checks: {} }));
    }
    return checkInfo;
  }
  function openCheck(row, k, d, opener) {
    const c = row.checks[k];
    const key = c.key === 'source' ? 'source:' + row.source : c.key;
    const info = (d.checks || {})[key];
    const dlg = $('#check-dialog');
    $('#cd-n').textContent = `Check ${k + 1} of ${row.checks.length} · ${row.name}`;
    $('#cd-name').textContent = c.label;
    const o = $('#cd-outcome');
    o.textContent = c.passed ? 'Passed' : 'Failed';
    o.className = 'td-outcome ' + (c.passed ? 'passed' : 'failed');
    $('#cd-value-row').hidden = !c.detail;
    $('#cd-value').textContent = c.detail || '';
    $('#cd-passes').textContent = info ? info.passes : 'No description available for this check yet.';
    $('#cd-why-row').hidden = !info;
    $('#cd-why').textContent = info ? info.why : '';
    $('#cd-caveat').hidden = !(info && info.caveat);
    $('#cd-caveat').textContent = (info && info.caveat) || '';
    const tests = (info && info.tests) || [];
    $('#cd-tests-row').hidden = !tests.length;
    $('#cd-tests').innerHTML = tests.map((n) => `<li><code>${esc(n)}</code></li>`).join('');
    dlg.returnFocusTo = opener;
    dlg.showModal();
  }
  document.addEventListener('click', (ev) => {
    const b = ev.target.closest('button.ck');
    if (!b) return;
    const row = rowsById.get(b.dataset.id);
    if (row) loadCheckInfo().then((d) => openCheck(row, Number(b.dataset.k), d, b));
  });

  // Test descriptions, the same as docs/README.md "The 19 tests".
  let descriptions = null;
  function loadDescriptions() {
    if (!descriptions) {
      descriptions = fetch('test-descriptions.json', { cache: 'no-store' })
        .then((r) => (r.ok ? r.json() : { tests: {} }))
        .catch(() => ({ tests: {} }));
    }
    return descriptions;
  }
  function describe(name, d) {
    const all = d.tests || {};
    if (all[name]) return all[name];
    const m = /^([^[]+)\[(.*)\]$/.exec(name); // parametrized: match the case by its message
    if (m) {
      const key = Object.keys(all).find((k) => k.startsWith(m[1] + '[') && m[2].endsWith(k.slice(m[1].length + 1, -1)));
      if (key) return all[key];
    }
    return null;
  }
  const OUTCOME = { passed: 'Passed', failed: 'Failed', skipped: 'Skipped' };
  function openTest(c, d, opener) {
    const dlg = $('#test-dialog');
    const info = describe(c.name, d);
    $('#td-n').textContent = info ? `Test ${info.n} of 19 · ${info.file}` : c.file.replace(/^tests\./, '') + '.py';
    $('#td-name').textContent = c.name;
    const o = $('#td-outcome');
    o.textContent = OUTCOME[c.outcome] || c.outcome;
    o.className = 'td-outcome ' + c.outcome;
    $('#td-asserts').textContent = info ? info.asserts : 'No description available for this test yet.';
    $('#td-why').textContent = info ? info.why : '';
    $('#td-why-row').hidden = !info;
    $('#td-param').hidden = !(info && /\[/.test(c.name));
    $('#td-param').textContent = d.note || '';
    dlg.returnFocusTo = opener;
    dlg.showModal();
  }
  ['test-dialog', 'check-dialog', 'note-dialog'].forEach((id) => {
    const dlg = document.getElementById(id);
    if (!dlg) return;
    dlg.addEventListener('click', (ev) => { if (ev.target === dlg) dlg.close(); });
    dlg.addEventListener('close', () => { if (dlg.returnFocusTo) dlg.returnFocusTo.focus(); });
  });

  fetch('results.json', { cache: 'no-store' })
    .then((r) => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
    .then(render)
    .catch((e) => {
      $('#meta').textContent = 'Could not load results.json (' + e.message + ').';
      $('#cards-svc').innerHTML = $('#cards-rp').innerHTML = '<p class="empty">No results available.</p>';
    });
})();
