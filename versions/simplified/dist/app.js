/* Between Classes: the published timing model, without runtime dependencies. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
  const shortDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'];
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const svgNS = 'http://www.w3.org/2000/svg';
  let data;
  try { data = JSON.parse($('timing-data').textContent); }
  catch {
    $('results-status').textContent = 'Interactive data could not be read. Use the weekly plan or download the research note, then reload to try again.';
    $('results-status').setAttribute('role', 'alert');
    document.querySelectorAll('select,input,.day-tabs button').forEach(control => { control.disabled = true; });
    return;
  }
  const clock = minute => `${String(Math.floor(minute / 60)).padStart(2, '0')}:${String(minute % 60).padStart(2, '0')}`;
  const toMinute = text => { const parts = text.split(':').map(Number); return parts.length === 2 && parts.every(Number.isFinite) ? parts[0] * 60 + parts[1] : NaN; };
  const score = value => Number(value).toFixed(1);
  const byDay = new Map(days.map((_, i) => [i + 1, data.meetings.filter(row => row[1] === i + 1)]));
  const buckets = { incoming: [], outgoing: [] };
  const maxima = { incoming: 0, outgoing: 0 };
  for (const direction of ['incoming', 'outgoing']) {
    for (let day = 1; day <= 5; day++) for (let j = 0; j < 64; j++) {
      const samples = data.vectors.filter(v => v[0] === day && v[1] >= 360 + j * 15 && v[1] < 375 + j * 15);
      const value = samples.reduce((sum, v) => sum + v[direction === 'incoming' ? 2 : 3], 0) / Math.max(1, samples.length);
      buckets[direction].push({ day, minute: 360 + j * 15, value });
      maxima[direction] = Math.max(maxima[direction], value);
    }
  }
  const params = new URLSearchParams(location.search);
  const initialDay = Number(params.get('day'));
  const state = {
    day: initialDay >= 1 && initialDay <= 5 ? initialDay : 1,
    direction: params.get('direction') === 'outgoing' ? 'outgoing' : 'incoming',
    band: ['all', 'midday'].includes(params.get('band')) ? params.get('band') : 'daytime',
    minute: 563, limit: 8, inspected: false,
  };
  const initialMinute = toMinute(params.get('time') || '');
  if (initialMinute >= 360 && initialMinute <= 1320) { state.minute = initialMinute; state.inspected = true; }
  else if (state.direction === 'outgoing') state.minute = 920;

  function node(tag, attrs, content) {
    const el = document.createElement(tag);
    for (const [key, value] of Object.entries(attrs || {})) el.setAttribute(key, value);
    if (content !== undefined) el.textContent = content;
    return el;
  }
  function svgNode(tag, attrs, content) {
    const el = document.createElementNS(svgNS, tag);
    for (const [key, value] of Object.entries(attrs || {})) el.setAttribute(key, value);
    if (content !== undefined) el.textContent = content;
    return el;
  }
  function tri(x, left, peak, right) {
    if (x <= left || x >= right) return 0;
    return x <= peak ? (x - left) / (peak - left) : (right - x) / (right - peak);
  }
  function pressure(row, minute, direction, scenario) {
    const start = row[scenario === 0 ? 2 : 4], end = row[scenario === 0 ? 3 : 5];
    return row[6] * (direction === 'incoming' ? tri(start - minute, -10, 10, 35) : tri(minute - end, -5, 10, 40));
  }
  function compute() {
    let a = 0, b = 0;
    for (const row of byDay.get(state.day)) {
      a += pressure(row, state.minute, state.direction, 0);
      b += pressure(row, state.minute, state.direction, 1);
    }
    return { central: (a + b) / 2, low: Math.min(a, b), high: Math.max(a, b) };
  }
  function remember() {
    try {
      const url = new URL(location.href);
      for (const [key, value] of Object.entries({ day: state.day, direction: state.direction, band: state.band })) url.searchParams.set(key, String(value));
      if (state.inspected) url.searchParams.set('time', clock(state.minute));
      else url.searchParams.delete('time');
      history.replaceState(null, '', url);
    } catch { /* Embedded previews can disallow history changes; the page remains usable. */ }
  }
  function changeReading(el, value) {
    if (el.textContent === value) return;
    el.textContent = value;
    if (!reduceMotion.matches) {
      el.classList.remove('reading-changed');
      requestAnimationFrame(() => el.classList.add('reading-changed'));
    }
  }
  function updatePlan() {
    const plan = data.plans[state.day - 1];
    const fields = {
      'plan-in-route': plan.to_university_route, 'plan-in-departure': plan.htw_departure,
      'plan-in-arrival': plan.campus_arrival, 'plan-out-route': plan.return_route,
      'plan-out-departure': plan.campus_departure, 'plan-out-arrival': plan.htw_arrival,
    };
    for (const [id, value] of Object.entries(fields)) changeReading($(id), value);
    $('plan-in-source').href = plan.inbound_source;
    $('plan-out-source').href = plan.outbound_source;
    const lectureDays = plan.return_route === '112' || plan.to_university_route === '112';
    $('plan-note').hidden = !lectureDays;
    $('plan-note').textContent = lectureDays ? 'Lecture days only' : '';
    document.querySelectorAll('[data-day]').forEach(button => button.setAttribute('aria-pressed', String(Number(button.dataset.day) === state.day)));
  }
  function drawMap(direction, animate = false) {
    const box = $(`${direction}-map`);
    const width = Math.max(240, box.clientWidth), height = 220;
    const left = width < 430 ? 38 : 54, right = 10, top = 12, plotWidth = width - left - right, rowHeight = 32;
    const svg = svgNode('svg', { class: 'heatmap-svg', viewBox: `0 0 ${width} ${height}`, role: 'img', 'aria-label': `${direction === 'incoming' ? 'Campus arrival' : 'Campus departure'} class-pressure heatmap, Monday to Friday, 06:00 to 22:00` });
    svg.append(svgNode('title', {}, 'Scheduled class pressure; actual passenger loads are unknown.'));
    for (let day = 1; day <= 5; day++) {
      const group = svgNode('g', { class: 'heat-row', style: `--row:${day - 1}` });
      for (const cell of buckets[direction].filter(v => v.day === day)) {
        const j = (cell.minute - 360) / 15;
        const rect = svgNode('rect', { class: 'pressure-cell', x: left + j * plotWidth / 64, y: top + (day - 1) * rowHeight, width: Math.max(1, plotWidth / 64 - .8), height: rowHeight - 5, rx: 1, opacity: .045 + .955 * cell.value / maxima[direction], 'data-day': day, 'data-minute': cell.minute });
        rect.append(svgNode('title', {}, `${days[day - 1]}, ${clock(cell.minute)}: ${score(cell.value)} class-pressure index`));
        group.append(rect);
      }
      svg.append(group);
      svg.append(svgNode('text', { x: left - 8, y: top + (day - 1) * rowHeight + 18, 'text-anchor': 'end' }, shortDays[day - 1]));
    }
    const ticks = width < 430 ? [360, 840, 1320] : [360, 600, 840, 1080, 1320];
    for (const minute of ticks) svg.append(svgNode('text', { class: 'axis-time', x: left + (minute - 360) / 960 * plotWidth, y: 195, 'text-anchor': minute === 360 ? 'start' : minute === 1320 ? 'end' : 'middle' }, clock(minute)));
    box.replaceChildren(svg);
    box.classList.toggle('chart-draw', animate && !reduceMotion.matches);
    box.setAttribute('tabindex', '0');
    box.setAttribute('role', 'group');
    box.setAttribute('aria-label', `${direction === 'incoming' ? 'Arrival' : 'Departure'} heatmap. Arrow keys change time and weekday; Enter inspects.`);
    markSelection();
  }
  function markSelection() {
    document.querySelectorAll('.selection-outline').forEach(el => el.remove());
    const minute = Math.min(1305, 360 + Math.floor((state.minute - 360) / 15) * 15);
    const map = $(`${state.direction}-map`);
    const rect = map.querySelector(`rect[data-day="${state.day}"][data-minute="${minute}"]`);
    if (!rect) return;
    const outline = svgNode('rect', { class: 'selection-outline', x: rect.getAttribute('x'), y: rect.getAttribute('y'), width: rect.getAttribute('width'), height: rect.getAttribute('height'), rx: 1 });
    map.querySelector('svg').append(outline);
  }
  function renderDetails() {
    $('inspector').hidden = !state.inspected;
    if (!state.inspected) { $('contributor-list').replaceChildren(); return; }
    const result = compute();
    $('inspect-title').textContent = `${days[state.day - 1]}, ${clock(state.minute)} campus ${state.direction === 'incoming' ? 'arrival' : 'departure'}`;
    $('inspect-score').textContent = `Timing range ${score(result.low)} to ${score(result.high)}`;
    const list = $('contributor-list');
    list.replaceChildren();
    const contributors = byDay.get(state.day).map(row => ({ row, value: (pressure(row, state.minute, state.direction, 0) + pressure(row, state.minute, state.direction, 1)) / 2 })).filter(c => c.value > .001).sort((a, b) => b.value - a.value);
    $('inspect-announcement').textContent = `${$('inspect-title').textContent}. ${$('inspect-score').textContent}. ${contributors.length} contributing meeting patterns.`;
    $('inspect-status').textContent = contributors.length ? `${contributors.length} classes nearby in time.` : 'No nearby classes in the collected schedules.';
    for (const { row } of contributors.slice(0, 5)) {
      const course = data.courses[row[0]], li = node('li');
      const link = node('a', { href: course[1], target: '_blank', rel: 'noopener' }, course[0]);
      const context = node('span', {}, `${clock(row[2])} to ${clock(row[3])}${row[7] ? ', ' + row[7] : ''}`);
      li.append(link, context); list.append(li);
    }
  }
  function renderRanks() {
    const opts = data.buses.filter(bus => {
      if (bus[0] !== state.day || bus[1] !== state.direction) return false;
      if (state.band === 'all') return true;
      if (state.band === 'midday') return bus[5] >= 660 && bus[5] <= 900;
      return state.direction === 'incoming' ? bus[5] >= 480 && bus[5] <= 660 : bus[5] >= 900 && bus[5] <= 1170;
    }).sort((a, b) => a[10] - b[10] || a[5] - b[5] || String(a[2]).localeCompare(String(b[2])));
    $('ranking-head').replaceChildren(...['Bus', state.direction === 'incoming' ? 'Departs HTW/SWS' : 'Departs Campus', state.direction === 'incoming' ? 'Arrives Campus' : 'Arrives HTW/SWS'].map(text => node('th', { scope: 'col' }, text)));
    const tbody = $('ranking-body'); tbody.replaceChildren();
    $('results-status').textContent = `${opts.length} options, quietest estimates first.`;
    $('results-status').setAttribute('role', 'status');
    for (const bus of opts.slice(0, state.limit)) {
      const tr = node('tr');
      const routeCell = node('td'); routeCell.append(node('a', { href: bus[11], target: '_blank', rel: 'noopener', 'aria-label': `Bus ${bus[2]} official timetable` }, bus[2]));
      if (bus[6] !== 'Monday-Friday') routeCell.append(node('span', { class: 'service-condition' }, bus[6]));
      tr.append(routeCell);
      const departureCell = node('td');
      const departure = state.direction === 'incoming' ? bus[3] : clock(bus[5]);
      const inspect = node('button', { class: 'time-button', type: 'button', 'aria-label': `Inspect bus ${bus[2]}, departure ${departure}` }, departure);
      inspect.addEventListener('click', () => {
        state.minute = bus[5]; state.inspected = true; sync();
        $('inspector').focus({ preventScroll: true });
        $('inspector').scrollIntoView({ behavior: reduceMotion.matches ? 'instant' : 'smooth', block: 'center' });
      });
      departureCell.append(inspect); tr.append(departureCell);
      tr.append(node('td', { class: 'measured' }, state.direction === 'incoming' ? clock(bus[5]) : bus[3]));
      tbody.append(tr);
    }
    if (!opts.length) {
      const td = node('td', { colspan: '3' }, 'No trips in this window. ');
      const reset = node('button', { type: 'button', class: 'time-button' }, 'Show all hours');
      reset.addEventListener('click', () => { state.band = 'all'; sync(); });
      td.append(reset); const tr = node('tr'); tr.append(td); tbody.append(tr);
    }
    $('more-results').hidden = opts.length <= state.limit;
  }
  function sync(rememberState = true) {
    $('day').value = String(state.day); $('direction').value = state.direction;
    $('band').querySelector('[value="daytime"]').textContent = state.direction === 'incoming' ? '08:00 to 11:00' : '15:00 to 19:30';
    $('band').value = state.band; $('inspect-time').value = clock(state.minute);
    updatePlan(); renderRanks(); renderDetails(); markSelection();
    if (rememberState) remember();
  }
  document.querySelectorAll('[data-day]').forEach(button => button.addEventListener('click', () => { state.day = Number(button.dataset.day); state.limit = 8; sync(); }));
  $('day').addEventListener('change', () => { state.day = Number($('day').value); state.limit = 8; sync(); });
  $('direction').addEventListener('change', () => { state.direction = $('direction').value; state.minute = state.direction === 'incoming' ? 563 : 920; state.limit = 8; sync(); });
  $('band').addEventListener('change', () => { state.band = $('band').value; state.limit = 8; sync(); });
  $('inspect-time').addEventListener('input', () => {
    const minute = toMinute($('inspect-time').value);
    const valid = minute >= 360 && minute <= 1320;
    $('inspect-time').setAttribute('aria-invalid', String(!valid));
    if (!valid) {
      $('results-status').setAttribute('role', 'alert');
      $('results-status').textContent = 'Choose a campus time between 06:00 and 22:00.';
      return;
    }
    state.minute = minute; state.inspected = true; sync();
  });
  $('more-results').addEventListener('click', () => { state.limit += 8; renderRanks(); });
  $('close-inspector').addEventListener('click', () => {
    state.inspected = false; renderDetails(); remember();
    $(`${state.direction}-map`).focus({ preventScroll: true });
  });
  for (const direction of ['incoming', 'outgoing']) {
    const box = $(`${direction}-map`);
    box.addEventListener('click', event => {
      const cell = event.target.closest('rect[data-minute]');
      if (!cell) return;
      state.day = Number(cell.dataset.day); state.minute = Number(cell.dataset.minute) + 5;
      state.direction = direction; state.inspected = true; state.limit = 8; sync();
    });
    box.addEventListener('keydown', event => {
      if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Enter', ' '].includes(event.key)) return;
      event.preventDefault(); state.direction = direction;
      if (event.key === 'ArrowLeft') state.minute = Math.max(360, state.minute - 15);
      if (event.key === 'ArrowRight') state.minute = Math.min(1320, state.minute + 15);
      if (event.key === 'ArrowUp') state.day = Math.max(1, state.day - 1);
      if (event.key === 'ArrowDown') state.day = Math.min(5, state.day + 1);
      state.inspected = true; sync();
    });
    drawMap(direction, true);
  }
  let frame;
  const resize = new ResizeObserver(() => {
    cancelAnimationFrame(frame);
    frame = requestAnimationFrame(() => { drawMap('incoming'); drawMap('outgoing'); });
  });
  resize.observe($('incoming-map'));
  const sections = document.querySelectorAll('main>section[id]');
  function updateNavigation() {
    const reference = document.querySelector('.site-header').getBoundingClientRect().bottom + 40;
    const current = [...sections].find(section => {
      const bounds = section.getBoundingClientRect();
      return bounds.top <= reference && bounds.bottom > reference;
    });
    document.querySelectorAll('nav a').forEach(link => {
      if (current && link.hash === '#' + current.id) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
  }
  let navigationFrame;
  function queueNavigation() {
    if (navigationFrame) return;
    navigationFrame = requestAnimationFrame(() => { navigationFrame = null; updateNavigation(); });
  }
  addEventListener('scroll', queueNavigation, { passive: true });
  addEventListener('resize', queueNavigation);
  updateNavigation();
  sync(false);
})();
