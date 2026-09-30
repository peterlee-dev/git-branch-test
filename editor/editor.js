// ------------------------------------------------------------
// 재능교육 영상 편집기: 영상 폴더의 index.html 을 보이지 않는 iframe 으로 열고
// window.VIDEO(schema·apply·canvas) 와 window.draw(t) 로 편집·미리보기·MP4 내보내기
// 영상 쪽 약속은 editor/PROTOCOL.md
// ------------------------------------------------------------
(() => {
const $ = id => document.getElementById(id);
const esc = s => String(s ?? '').replace(/[&<>"]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[ch]);
const clone = o => JSON.parse(JSON.stringify(o));
const getP = (o, path) => path.split('.').reduce((a, k) => a == null ? a : a[k], o);
function setP(o, path, v) { const ks = path.split('.'); const last = ks.pop(); ks.reduce((a, k) => a[k], o)[last] = v; }
const sleep = ms => new Promise(r => setTimeout(r, ms));

// 지금 연 영상
let V = null, win = null, S = null, DUR = 1, FPS = 30, videoId = null, loadToken = 0;
let state = null, tCur = 0, playing = false, t0 = 0, sel = null, exporting = false;
let undoStack = [], lastSnap = '';
const view = $('view'), vctx = view.getContext('2d');

// ---------- 영상 고르기 ----------
$('video').innerHTML = window.VIDEOS.map(v => `<option value="${v.id}">${esc(v.title)}</option>`).join('');
const fromHash = location.hash.slice(1);
const first = window.VIDEOS.some(v => v.id === fromHash) ? fromHash : (() => { try { return localStorage.getItem('jei-editor-last'); } catch (e) { return null; } })();
$('video').value = window.VIDEOS.some(v => v.id === first) ? first : window.VIDEOS[0].id;
$('video').onchange = () => openVideo($('video').value);

function busy(msg) { $('busy').hidden = !msg; if (msg) $('busy').textContent = msg; }
function setControls(on) { ['undo', 'reset', 'load', 'saveJson', 'export', 'play'].forEach(id => { $(id).disabled = !on || (id === 'undo' && !undoStack.length); }); }

async function openVideo(id) {
  const token = ++loadToken;
  setPlaying(false); setControls(false); busy('영상을 불러오는 중…');
  V = null; win = null; S = null; videoId = id; sel = null;
  try { localStorage.setItem('jei-editor-last', id); } catch (e) {}
  try { history.replaceState(null, '', '#' + id); } catch (e) {}
  $('tabs').innerHTML = ''; $('panes').innerHTML = ''; $('tlNote').textContent = '';
  const frame = $('frame');
  await new Promise(res => { frame.onload = res; frame.src = `${id}/index.html?render`; });
  if (token !== loadToken) return;
  win = frame.contentWindow;
  try {
    const ok = await Promise.race([Promise.resolve(win.ready).then(() => true), sleep(60000).then(() => false)]);
    if (!ok) throw new Error('영상을 준비하는 데 너무 오래 걸려요.');
  } catch (e) { busy('영상을 열지 못했어요. ' + (e.message || '')); return; }
  if (token !== loadToken) return;
  DUR = win.DURATION;
  V = win.VIDEO || null; S = V && V.schema;
  if (!V || !S) {  // 아직 편집기에 연결 안 된 영상: 미리보기만
    FPS = 30; state = null; buildTimeline(); busy(''); setControls(false); $('play').disabled = false;
    $('panes').innerHTML = `<div class="pane"><div class="group"><p class="alert">이 영상은 아직 편집기에 연결되지 않았어요. 미리보기만 할 수 있어요.</p></div></div>`;
    show(0); return;
  }
  FPS = S.fps || 30;
  state = clone(V.defaults);
  const saved = loadLocal();
  if (saved) { V.apply(saved); state = clone(V.content); } else V.apply(state);
  undoStack = []; lastSnap = JSON.stringify(state);
  $('saveState').textContent = saved && !isDefault() ? '이 브라우저에 저장된 작업을 열었어요' : '기본값';
  setupAudio();
  buildTimeline(); buildPanels();
  busy(''); setControls(true);
  const g0 = S.groups && S.groups.find(g => g.at != null);
  show(S.timed ? itemAt(0) : g0 ? g0.at : Math.min(DUR / 2, 3));
}

// ---------- 저장 (브라우저 자동 저장은 편의 기능) ----------
const storeKey = () => 'jei-editor-v1:' + videoId;
function loadLocal() { try { const s = localStorage.getItem(storeKey()); return s ? JSON.parse(s).content : null; } catch (e) { return null; } }
function saveLocal() { try { localStorage.setItem(storeKey(), JSON.stringify({ content: state })); $('saveState').textContent = '이 브라우저에 저장됨'; } catch (e) { $('saveState').textContent = '자동 저장 안 됨 (작업 파일로 저장하세요)'; } }
const isDefault = () => JSON.stringify(state) === JSON.stringify(V.defaults);

// ---------- 바뀐 값 적용 (연속 입력은 한 프레임에 한 번) ----------
let applyQueued = false, saveTimer = 0, histTimer = 0;
function changed({ bars = true } = {}) {
  if (!applyQueued) { applyQueued = true; requestAnimationFrame(() => { applyQueued = false; if (!V) return; V.apply(state); show(tCur); if (bars) drawBars(); checkFits(); }); }
  clearTimeout(saveTimer); saveTimer = setTimeout(saveLocal, 400);
  clearTimeout(histTimer); histTimer = setTimeout(pushHistory, 350);
  $('saveState').textContent = '저장 중…';
}
function pushHistory() { const s = JSON.stringify(state); if (s !== lastSnap) { undoStack.push(lastSnap); if (undoStack.length > 100) undoStack.shift(); lastSnap = s; $('undo').disabled = false; } }
function replaceState(next) { V.apply(next); state = clone(V.content); buildPanels(); changed(); }
function undo() { if (!undoStack.length || !V) return; clearTimeout(histTimer); lastSnap = undoStack.pop(); state = JSON.parse(lastSnap); V.apply(state); buildPanels(); show(tCur); drawBars(); saveLocal(); $('undo').disabled = !undoStack.length; }
$('undo').onclick = undo;
let resetArmed = 0;
$('reset').onclick = () => {   // 확인 창을 쓸 수 없는 환경이라 두 번 눌러 확인
  if (!resetArmed) { resetArmed = setTimeout(() => { resetArmed = 0; $('reset').textContent = '기본값으로'; }, 3000); $('reset').textContent = '한 번 더 누르면 초기화'; return; }
  clearTimeout(resetArmed); resetArmed = 0; $('reset').textContent = '기본값으로'; replaceState(clone(V.defaults));
};

// ---------- 그리기·시간 ----------
const tc = t => { const f = Math.round(t * FPS), s = Math.floor(f / FPS), fr = f % FPS, m = Math.floor(s / 60); return `${String(m).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}:${String(fr).padStart(2, '0')}`; };
function render(t) { win.draw(t); const c = V ? V.canvas : win.document.getElementById('c'); vctx.drawImage(c, 0, 0, view.width, view.height); }
function show(t) {
  if (!win) return;
  tCur = Math.min(DUR, Math.max(0, t)); render(Math.min(tCur, DUR - 1e-3));
  $('tc').innerHTML = `${tc(tCur)}<small>/ ${tc(DUR)}</small>`;
  const ph = $('playhead'), box = $('timeline').getBoundingClientRect(), r = $('ruler').getBoundingClientRect();
  const lastRow = [...document.querySelectorAll('#timeline .tl-row')].filter(el => !el.hidden).pop().getBoundingClientRect();
  ph.hidden = false; ph.style.left = (r.left - box.left + tCur / DUR * r.width - 1) + 'px'; ph.style.top = (r.top - box.top) + 'px'; ph.style.height = (lastRow.bottom - r.top) + 'px';
  document.querySelectorAll('.scene').forEach(el => el.classList.toggle('on', tCur >= +el.dataset.s && tCur < +el.dataset.e));
}
function seek(t) { show(t); if (playing) { t0 = performance.now() - tCur * 1000; try { audio.currentTime = tCur; } catch (e) {} } }
window.addEventListener('resize', () => show(tCur));

// ---------- 소리 (미리보기) ----------
const audio = new Audio(); audio.preload = 'auto';
let audioSrcs = [], audioIdx = 0;
audio.onerror = () => { if (audio.src && ++audioIdx < audioSrcs.length) audio.src = audioSrcs[audioIdx]; };
function setupAudio() { audio.pause(); audioSrcs = (S.audio || []).map(a => `${videoId}/${a}`); audioIdx = 0; if (audioSrcs.length) audio.src = audioSrcs[0]; else audio.removeAttribute('src'); }
function loop(now) {
  if (!playing) return;
  const t = (now - t0) / 1000;
  if (t >= DUR) { setPlaying(false); show(DUR); return; }
  show(t); requestAnimationFrame(loop);
}
function setPlaying(on) {
  if (exporting || (on && !win)) return;
  playing = on; $('play').textContent = on ? '❚❚' : '▶'; $('play').setAttribute('aria-label', on ? '정지' : '재생');
  if (on) { if (tCur >= DUR - .01) tCur = 0; t0 = performance.now() - tCur * 1000; if (audioSrcs.length) { try { audio.currentTime = tCur; audio.play().catch(() => {}); } catch (e) {} } requestAnimationFrame(loop); }
  else audio.pause();
}
$('play').onclick = () => setPlaying(!playing);
document.addEventListener('keydown', e => {
  if (e.target.closest('input, select, textarea') || exporting || !win) return;
  if (e.code === 'Space') { e.preventDefault(); setPlaying(!playing); }
  if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { e.preventDefault(); const d = (e.shiftKey ? 1 : 1 / FPS) * (e.key === 'ArrowRight' ? 1 : -1); seek(Math.round((tCur + d) * FPS) / FPS); }
  if ((e.metaKey || e.ctrlKey) && e.key === 'z') { e.preventDefault(); undo(); }
});

// ---------- 타임라인 ----------
const pct = t => (t / DUR * 100) + '%';
function buildTimeline() {
  const step = DUR > 90 ? 10 : 5, tick = DUR > 90 ? 5 : 1;
  let h = '';
  for (let s = 0; s <= DUR; s += tick) h += `<i class="${s % step ? '' : 'major'}" style="left:${pct(s)}"></i>` + (s % step || DUR - s < step * .6 ? '' : `<b style="left:${pct(s)}">${s >= 60 ? Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0') : s}</b>`);
  $('ruler').innerHTML = h;
  const scenes = (S && S.scenes) || [{ start: 0, end: DUR, label: '전체' }];
  $('scenes').innerHTML = scenes.map(c => `<div class="scene${c.dark ? ' dark' : ''}" data-s="${c.start}" data-e="${c.end}" style="left:${pct(c.start)};width:calc(${pct(c.end - c.start)} - 2px)" title="${esc(c.label)} (${c.start}–${c.end}초)">${esc(c.label)}</div>`).join('');
  const snd = (S && S.sounds) || [];
  $('soundsRow').hidden = !snd.length;
  $('sounds').innerHTML = snd.map(s => `<i class="${s.big ? 'big' : ''}" style="left:${pct(s.t)}" title="${esc(s.label)} ${s.t}초"></i>`).join('');
  $('barsRow').hidden = !(S && S.timed);
  if (S && S.timed) $('barsLabel').textContent = S.timed.barLabel || '문구';
  $('tlNote').textContent = S && S.timed ? `${S.timed.label || '문구'} 막대를 끌어 나오는 시간을 옮기고, 양 끝을 끌어 길이를 바꿔요. 장면 길이는 소리와 묶여 있어서 고정이에요.` : '장면 길이는 소리와 묶여 있어서 고정이에요. 장면을 누르면 그 장면으로 이동해요.';
  drawBars();
}
$('scenes').onclick = e => { const el = e.target.closest('.scene'); if (el) seek(Math.min(+el.dataset.e - .05, +el.dataset.s + .6)); };
const items = () => S && S.timed ? getP(state, S.timed.path) || [] : [];
const tk = () => S.timed.startKey || 'start', ek = () => S.timed.endKey || 'end', xk = () => S.timed.textKey || 'text';
function itemAt(i) { const it = items()[i]; return it ? it[tk()] + Math.min(.8, (it[ek()] - it[tk()]) / 2) : 0; }
function lanes() {   // 겹치는 막대는 아래 줄로
  const list = items(), order = list.map((c, i) => i).sort((a, b) => list[a][tk()] - list[b][tk()]), end = [], lane = [];
  order.forEach(i => { const c = list[i]; let l = end.findIndex(e => c[tk()] >= e - 1e-6); if (l < 0) l = end.length; lane[i] = l; end[l] = c[ek()]; });
  return { lane, n: Math.max(1, end.length) };
}
function drawBars() {
  if (!S || !S.timed) { $('bars').innerHTML = ''; return; }
  const { lane, n } = lanes();
  $('bars').style.height = (n * 34 - 4) + 'px';
  $('bars').innerHTML = items().map((c, i) => `<div class="bar${sel === i ? ' sel' : ''}" data-i="${i}" style="left:${pct(c[tk()])};width:${pct(c[ek()] - c[tk()])};top:${lane[i] * 34}px" title="${esc(c[xk()])} (${(+c[tk()]).toFixed(2)}–${(+c[ek()]).toFixed(2)}초)"><span class="h l" data-edge="l"></span>${esc(c[xk()]) || '(빈 칸)'}<span class="h r" data-edge="r"></span></div>`).join('');
}
const snap = t => Math.round(t * 20) / 20;
function timeAt(x) { const r = $('ruler').getBoundingClientRect(); return Math.min(DUR, Math.max(0, (x - r.left) / r.width * DUR)); }
let drag = null;
$('ruler').addEventListener('pointerdown', e => { if (!win) return; drag = { kind: 'seek' }; $('ruler').setPointerCapture(e.pointerId); seek(timeAt(e.clientX)); });
$('bars').addEventListener('pointerdown', e => {
  if (!V) return;
  const bar = e.target.closest('.bar'); $('bars').setPointerCapture(e.pointerId);
  if (!bar) { drag = { kind: 'seek' }; seek(timeAt(e.clientX)); return; }
  const i = +bar.dataset.i, c = items()[i];
  drag = { kind: 'bar', i, edge: e.target.dataset.edge || 'move', t: timeAt(e.clientX), s: c[tk()], e: c[ek()], moved: false };
  select(i, false);
});
window.addEventListener('pointermove', e => {
  if (!drag) return;
  if (drag.kind === 'seek') return seek(timeAt(e.clientX));
  const c = items()[drag.i], d = timeAt(e.clientX) - drag.t, min = S.timed.minLen || .4; drag.moved = true;
  if (drag.edge === 'l') c[tk()] = snap(Math.min(drag.e - min, Math.max(0, drag.s + d)));
  else if (drag.edge === 'r') c[ek()] = snap(Math.max(drag.s + min, Math.min(DUR, drag.e + d)));
  else { const len = drag.e - drag.s; c[tk()] = snap(Math.min(DUR - len, Math.max(0, drag.s + d))); c[ek()] = snap(c[tk()] + len); }
  syncItemTimes(drag.i); changed();
  seek(drag.edge === 'r' ? c[ek()] - .2 : c[tk()] + Math.min(.8, (c[ek()] - c[tk()]) / 2));
});
window.addEventListener('pointerup', () => { if (drag && drag.kind === 'bar' && !drag.moved) seek(itemAt(drag.i)); drag = null; });
$('bars').addEventListener('dblclick', e => { const b = e.target.closest('.bar'); if (b) select(+b.dataset.i); });

// ---------- 속성 패널 ----------
function inputHTML(f, id, value, data) {
  const attrs = `id="${id}" ${data}`;
  if (f.type === 'color') return `<input type="color" ${attrs} value="${esc(value)}" aria-label="${esc(f.label)}">`;
  if (f.type === 'number') return `<input type="number" ${attrs} value="${esc(value)}"${f.step != null ? ` step="${f.step}"` : ''}${f.min != null ? ` min="${f.min}"` : ''}${f.max != null ? ` max="${f.max}"` : ''}>`;
  if (f.type === 'select') return `<select ${attrs}>${(f.options || []).map(o => { const [v, n] = Array.isArray(o) ? o : [o, o]; return `<option value="${esc(v)}"${String(v) === String(value) ? ' selected' : ''}>${esc(n)}</option>`; }).join('')}</select>`;
  if (f.type === 'textarea') return `<textarea ${attrs} rows="3">${esc(value)}</textarea>`;
  return `<input type="text" ${attrs} value="${esc(value)}">`;
}
let fieldSeq = 0;
function fieldHTML(f, g) {
  const id = 'f' + (fieldSeq++), at = f.at ?? g.at, data = `data-path="${esc(f.path)}" data-type="${f.type || 'text'}"${at != null ? ` data-at="${at}"` : ''}`;
  const val = getP(state, f.path);
  if (f.type === 'color') return `<div class="color">${inputHTML(f, id, val, data)}<div><span>${esc(f.label)}</span>${f.desc ? `<small>${esc(f.desc)}</small>` : ''}</div>${at != null ? `<button class="jump" data-at="${at}">▶ ${(+at).toFixed(1)}초</button>` : '<span></span>'}</div>`;
  return `<label class="field"><span>${esc(f.label)}</span>${inputHTML(f, id, val, data)}${f.fit ? `<span class="warn" data-fitfor="${id}" hidden></span>` : ''}</label>`;
}
function itemHTML(it, i) {
  const fs = S.timed.fields, main = fs.filter(f => f.type === 'text' || f.type === 'textarea'), rest = fs.filter(f => !main.includes(f));
  const one = f => { const id = `it${i}-${f.key}`; return `<label class="field"><span>${esc(f.key === xk() ? `${f.label} ${i + 1}` : f.label)}</span>${inputHTML(f, id, it[f.key], `data-item="${i}" data-key="${f.key}" data-type="${f.type || 'text'}"`)}${f.fitFrom || f.fit ? `<span class="warn" data-fitfor="${id}" hidden></span>` : ''}</label>`; };
  const rows = []; for (let k = 0; k < rest.length; k += 3) rows.push(`<div class="row">${rest.slice(k, k + 3).map(one).join('')}</div>`);
  return `<div class="item${sel === i ? ' sel' : ''}" id="item-${i}" data-item-block="${i}">${main.map(one).join('')}${rows.join('')}</div>`;
}
function buildPanels() {
  fieldSeq = 0;
  const tabs = S.tabs && S.tabs.length ? S.tabs : [{ id: 'text', label: '문구' }];
  const extra = [{ id: '__info', label: '도움말' }];
  $('tabs').innerHTML = [...tabs, ...extra].map((t, i) => `<button role="tab" data-tab="${t.id}" aria-selected="${i === 0}">${esc(t.label)}</button>`).join('');
  let html = '';
  tabs.forEach((t, ti) => {
    let inner = '';
    if (ti === 0 && S.warnings && S.warnings.length) inner += `<div class="group">${S.warnings.map(w => `<p class="alert">${esc(w)}</p>`).join('')}</div>`;
    if (ti === 0 && S.timed) inner += `<div class="group"><div class="group-head"><h2>${esc(S.timed.label || '문구')}</h2></div><p class="note">나오는 시간은 타임라인에서 끌어도 바뀌어요.</p>${items().map(itemHTML).join('')}</div>`;
    (S.groups || []).filter(g => (g.tab || tabs[0].id) === t.id).forEach(g => {
      const fields = g.fields.map(f => fieldHTML(f, g)).join('');
      inner += `<div class="group"><div class="group-head"><h2>${esc(g.title)}</h2>${g.at != null ? `<button class="jump" data-at="${g.at}">▶ ${(+g.at).toFixed(1)}초</button>` : ''}</div>${g.note ? `<p class="note">${esc(g.note)}</p>` : ''}${g.columns === 2 ? `<div class="cols2">${fields}</div>` : fields}</div>`;
    });
    html += `<div class="pane" data-pane="${t.id}" role="tabpanel"${ti ? ' hidden' : ''}>${inner || '<div class="group"><p class="note">고칠 수 있는 칸이 없어요.</p></div>'}</div>`;
  });
  html += `<div class="pane" data-pane="__info" role="tabpanel" hidden>
    <div class="group"><div class="group-head"><h2>이렇게 써요</h2></div>
      <p class="note">칸을 고치면 미리보기에 바로 반영돼요. 칸을 누르면 그 값이 보이는 순간으로 이동해요.</p>
      <p class="note">고친 내용은 영상마다 이 브라우저에 자동 저장돼요. 보관하거나 다른 사람에게 넘기려면 <b>작업 파일 저장</b>으로 JSON 파일을 받아 두고, <b>불러오기</b>로 다시 여세요.</p></div>
    <div class="group"><div class="group-head"><h2>MP4 만들기</h2></div>
      <p class="note"><b>MP4 내보내기</b>는 이 브라우저에서 ${Math.round(DUR * FPS)}장을 한 장씩 그려 1920×1080, ${FPS}fps 영상을 만들어요. 영상 길이와 그래픽 성능에 따라 몇 분 걸려요. 크롬이나 엣지 최신 버전에서 돼요.</p>
      <p class="note">가장 좋은 화질이 필요하면 작업 파일로 저장소에서 렌더링하세요.<br><code>cd ${esc(videoId)} && node render.mjs --project 작업파일.json</code></p></div>
    ${S.locked ? `<div class="group"><div class="group-head"><h2>이 영상에서 고칠 수 없는 것</h2></div><p class="note">${esc(S.locked)}</p></div>` : ''}
  </div>`;
  $('panes').innerHTML = html;
  checkFits();
}
function switchTab(id) { document.querySelectorAll('#tabs button').forEach(b => b.setAttribute('aria-selected', b.dataset.tab === id)); document.querySelectorAll('#panes .pane').forEach(p => p.hidden = p.dataset.pane !== id); }
$('tabs').onclick = e => { const b = e.target.closest('button'); if (b) switchTab(b.dataset.tab); };
function select(i, scroll = true) {
  sel = i; drawBars();
  document.querySelectorAll('[data-item-block]').forEach(b => b.classList.toggle('sel', +b.dataset.itemBlock === i));
  if (scroll) { switchTab((S.tabs && S.tabs[0] && S.tabs[0].id) || 'text'); $('item-' + i)?.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); }
}
function syncItemTimes(i) { [tk(), ek()].forEach(k => { const el = $(`it${i}-${k}`); if (el && document.activeElement !== el) el.value = items()[i][k]; }); }
const valueOf = el => el.dataset.type === 'number' ? parseFloat(el.value) : el.dataset.type === 'select' && el.value !== '' && !isNaN(el.value) && typeof getOriginal(el) === 'number' ? +el.value : el.value;
function getOriginal(el) { return el.dataset.path ? getP(state, el.dataset.path) : items()[+el.dataset.item]?.[el.dataset.key]; }
const panes = $('panes');
panes.addEventListener('input', e => {
  const el = e.target; if (!V) return;
  const v = valueOf(el); if (el.dataset.type === 'number' && !isFinite(v)) return;
  if (el.dataset.path) { setP(state, el.dataset.path, v); changed({ bars: false }); return; }
  if (el.dataset.item != null) {
    const i = +el.dataset.item, k = el.dataset.key, c = items()[i], min = S.timed.minLen || .4; c[k] = v;
    if (k === tk() || k === ek()) { c[tk()] = Math.max(0, Math.min(DUR - min, c[tk()])); c[ek()] = Math.max(c[tk()] + min, Math.min(DUR, c[ek()])); seek(k === ek() ? c[ek()] - .2 : c[tk()] + .5); }
    changed();
  }
});
panes.addEventListener('change', e => { const el = e.target; if (el.dataset.item != null && (el.dataset.key === tk() || el.dataset.key === ek())) { const i = +el.dataset.item; [tk(), ek()].forEach(k => { $(`it${i}-${k}`).value = items()[i][k]; }); } });
panes.addEventListener('focusin', e => {
  const el = e.target;
  if (el.dataset.at) seek(+el.dataset.at);
  if (el.dataset.item != null) { const i = +el.dataset.item; if (sel !== i) select(i, false); if (el.dataset.key !== tk() && el.dataset.key !== ek()) seek(itemAt(i)); }
});
panes.addEventListener('click', e => { const j = e.target.closest('.jump'); if (j) seek(+j.dataset.at); });

// 글자가 화면 밖으로 넘칠 것 같으면 알려 줌 (영상 페이지의 글꼴로 잼)
function measure(s, size, weight, family, spacing) { const m = win.document.createElement('canvas').getContext('2d'); m.font = `${weight || 400} ${size}px ${family || "'Noto Sans KR'"}`; return Math.max(...String(s).split('\n').map(line => m.measureText(line).width + (spacing || 0) * [...line].length)); }
function checkFits() {
  if (!V) return;
  document.querySelectorAll('[data-fitfor]').forEach(w => {
    const el = $(w.dataset.fitfor); if (!el) return;
    let fit;
    if (el.dataset.path) fit = findField(el.dataset.path)?.fit;
    else { const f = S.timed.fields.find(f => f.key === el.dataset.key), it = items()[+el.dataset.item]; fit = f.fit || (f.fitFrom && { size: it[f.fitFrom.size], weight: it[f.fitFrom.weight], spacing: it[f.fitFrom.spacing], family: f.family, max: f.max }); }
    if (!fit) return;
    const over = measure(el.value, fit.size, fit.weight, fit.family, fit.spacing) > fit.max;
    w.hidden = !over; w.textContent = over ? '글자가 길어 화면 밖으로 넘칠 수 있어요. 줄이거나 크기를 낮춰 주세요.' : '';
  });
}
function findField(path) { for (const g of S.groups || []) for (const f of g.fields) if (f.path === path) return f; return null; }

// ---------- 파일 저장·불러오기 ----------
let downloads = null;
const dlReady = window.claude?.use ? window.claude.use('downloads').then(d => (downloads = d)).catch(() => null) : Promise.resolve(null);
async function saveFile(filename, blob) {
  await dlReady;
  if (downloads) { await downloads.save({ filename, data: blob }); return; }
  if (window.claude?.use) throw { code: 'unavailable' };   // 아티팩트 안에서는 링크 다운로드가 막혀 있음
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = filename; a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 5000);
}
const saveMsg = e => e?.code === 'declined' ? '저장을 취소했어요.' : e?.code === 'rate_limited' ? '이미 열린 저장 창이 있어요. 잠시 뒤 다시 눌러 주세요.' : '이 화면에서는 파일을 저장할 수 없어요.';
$('saveJson').onclick = async () => {
  const blob = new Blob([JSON.stringify({ kind: 'jei-video-project', version: 1, video: videoId, content: state }, null, 1)], { type: 'application/json' });
  try { await saveFile(`${videoId}_project.json`, blob); $('saveState').textContent = '작업 파일을 저장했어요'; } catch (e) { $('saveState').textContent = saveMsg(e); }
};
$('load').onclick = () => $('fileIn').click();
$('fileIn').onchange = async () => {
  const f = $('fileIn').files[0]; $('fileIn').value = ''; if (!f) return;
  let j; try { j = JSON.parse(await f.text()); } catch (e) { $('saveState').textContent = 'JSON 파일을 읽지 못했어요.'; return; }
  if (!j || typeof j.content !== 'object') { $('saveState').textContent = '이 편집기에서 저장한 작업 파일이 아니에요.'; return; }
  const vid = j.video || (j.kind === 'ai-math-trailer' ? 'ai-math-trailer' : videoId);
  if (vid !== videoId) {
    if (!window.VIDEOS.some(v => v.id === vid)) { $('saveState').textContent = '이 편집기에 없는 영상의 작업 파일이에요.'; return; }
    try { localStorage.setItem('jei-editor-v1:' + vid, JSON.stringify({ content: j.content })); } catch (e) {}
    $('video').value = vid; await openVideo(vid); if (videoId === vid && V) { replaceState(j.content); $('saveState').textContent = `${f.name} 을(를) 불러왔어요`; } return;
  }
  replaceState(j.content); $('saveState').textContent = `${f.name} 을(를) 불러왔어요`;
};

// ---------- 브라우저에서 MP4 만들기 (WebCodecs + mp4-muxer) ----------
let cancelExport = false, exported = null;
async function pickVideoConfig() {   // H.264 우선, 안 되면 VP9 (MP4 안의 VP9: 크롬·엣지·VLC 재생, 맥 QuickTime 은 못 열 수 있음)
  for (const [codec, mux] of [['avc1.640028', 'avc'], ['avc1.4d0028', 'avc'], ['avc1.42003e', 'avc'], ['vp09.00.40.08', 'vp9']]) {
    const cfg = { codec, width: 1920, height: 1080, bitrate: 14e6, framerate: FPS, ...(mux === 'avc' ? { avc: { format: 'avc' } } : {}) };
    try { if ((await VideoEncoder.isConfigSupported(cfg)).supported) return { cfg, mux }; } catch (e) {}
  }
  return null;
}
async function loadAudioBuffer() {
  for (const src of audioSrcs) {
    try { const r = await fetch(src); if (!r.ok) continue; return await new OfflineAudioContext(2, 48000, 48000).decodeAudioData(await r.arrayBuffer()); } catch (e) {}
  }
  return null;
}
async function pickAudioConfig(buf) {
  for (const [codec, mux] of [['mp4a.40.2', 'aac'], ['opus', 'opus']]) {
    const cfg = { codec, sampleRate: buf.sampleRate, numberOfChannels: 2, bitrate: 192000 };
    try { if ((await AudioEncoder.isConfigSupported(cfg)).supported) return { cfg, mux }; } catch (e) {}
  }
  return null;
}
function dlg(title, msg) { $('dlgTitle').textContent = title; $('dlgMsg').textContent = msg; }
async function exportMp4() {
  if (!V && !win) return;
  $('dlgBar').style.width = '0'; $('dlgSave').hidden = true; $('dlgStat').textContent = '';
  if (!('VideoEncoder' in window) || !window.Mp4Muxer) { dlg('이 브라우저에서는 만들 수 없어요', '크롬이나 엣지 최신 버전에서 열어 주세요. 또는 작업 파일을 저장해 render.mjs 로 렌더링하세요.'); $('dlgCancel').textContent = '닫기'; $('dlg').showModal(); return; }
  setPlaying(false); exporting = true; cancelExport = false; exported = null; $('dlgCancel').textContent = '취소';
  dlg('MP4 만드는 중', '한 장면씩 그리고 있어요. 이 탭을 닫거나 다른 탭으로 옮기지 마세요.'); $('dlg').showModal();
  const keepT = tCur, LEN = window.__EXPORT_SECONDS__ || DUR;   // __EXPORT_SECONDS__: 시험할 때만 앞부분만 만듦
  const fade = (S && S.audioFade) || { in: 0, out: 0 };
  try {
    const vcfg = await pickVideoConfig(); if (!vcfg) throw new Error('이 브라우저는 영상 인코딩(H.264·VP9)을 지원하지 않아요.');
    const abuf = audioSrcs.length ? await loadAudioBuffer() : null, acfg = abuf && 'AudioEncoder' in window ? await pickAudioConfig(abuf) : null;
    const target = new Mp4Muxer.ArrayBufferTarget();
    const muxer = new Mp4Muxer.Muxer({ target, fastStart: 'in-memory', firstTimestampBehavior: 'offset',
      video: { codec: vcfg.mux, width: 1920, height: 1080, frameRate: FPS },
      ...(acfg ? { audio: { codec: acfg.mux, numberOfChannels: 2, sampleRate: abuf.sampleRate } } : {}) });
    let encErr = null;
    const venc = new VideoEncoder({ output: (c, m) => muxer.addVideoChunk(c, m), error: e => (encErr = e) }); venc.configure(vcfg.cfg);
    if (acfg) {   // render.mjs 와 같은 페이드
      const aenc = new AudioEncoder({ output: (c, m) => muxer.addAudioChunk(c, m), error: e => (encErr = e) }); aenc.configure(acfg.cfg);
      const sr = abuf.sampleRate, n = Math.min(abuf.length, Math.round(LEN * sr)), chs = [0, 1].map(c => abuf.getChannelData(Math.min(c, abuf.numberOfChannels - 1))), BLK = 4800;
      for (let o = 0; o < n; o += BLK) {
        const len = Math.min(BLK, n - o), data = new Float32Array(len * 2);
        for (let c = 0; c < 2; c++) for (let k = 0; k < len; k++) { const s = (o + k) / sr; let g = 1; if (fade.in) g = Math.min(g, s / fade.in); if (fade.out) g = Math.min(g, (LEN - s) / fade.out); data[c * len + k] = chs[c][o + k] * Math.max(0, g); }
        const ad = new AudioData({ format: 'f32-planar', sampleRate: sr, numberOfFrames: len, numberOfChannels: 2, timestamp: Math.round(o / sr * 1e6), data });
        aenc.encode(ad); ad.close();
      }
      await aenc.flush(); aenc.close();
    }
    const frames = Math.round(LEN * FPS), started = performance.now(), src = V ? V.canvas : win.document.getElementById('c');
    for (let i = 0; i < frames; i++) {
      if (cancelExport) throw 'cancel'; if (encErr) throw encErr;
      win.draw(i / FPS);
      const vf = new VideoFrame(src, { timestamp: Math.round(i * 1e6 / FPS), duration: Math.round(1e6 / FPS) });
      venc.encode(vf, { keyFrame: i % (FPS * 2) === 0 }); vf.close();
      while (venc.encodeQueueSize > 6) await sleep(4);
      if (i % 5 === 0) {
        const k = (i + 1) / frames, el = (performance.now() - started) / 1000, left = el / k - el;
        $('dlgBar').style.width = (k * 100).toFixed(1) + '%';
        $('dlgStat').textContent = `${i + 1} / ${frames} 장 · 남은 시간 약 ${left < 60 ? Math.ceil(left) + '초' : Math.ceil(left / 60) + '분'}`;
        if (i % 30 === 0) vctx.drawImage(src, 0, 0, view.width, view.height);
        await sleep(0);
      }
    }
    await venc.flush(); venc.close(); muxer.finalize();
    exported = new Blob([target.buffer], { type: 'video/mp4' });
    $('dlgBar').style.width = '100%';
    dlg('MP4를 만들었어요', `${(exported.size / 1048576).toFixed(1)} MB · 1920×1080 · ${FPS}fps${acfg ? '' : audioSrcs.length ? ' · 소리 없음 (음악 파일을 찾지 못했어요)' : ''}${vcfg.mux === 'vp9' ? ' · VP9 코덱 (맥 QuickTime 에서는 안 열릴 수 있어요)' : ''}`);
    $('dlgStat').textContent = ''; $('dlgSave').hidden = false; $('dlgCancel').textContent = '닫기';
  } catch (e) {
    if (e === 'cancel') $('dlg').close();
    else { dlg('MP4를 만들지 못했어요', (e && e.message) || String(e)); $('dlgStat').textContent = '작업 파일을 저장해 render.mjs 로 렌더링할 수 있어요.'; $('dlgCancel').textContent = '닫기'; }
  } finally { exporting = false; show(keepT); }
}
$('export').onclick = exportMp4;
$('dlgCancel').onclick = () => { if (exporting) cancelExport = true; else $('dlg').close(); };
$('dlg').addEventListener('cancel', e => { if (exporting) { e.preventDefault(); cancelExport = true; } });
$('dlgSave').onclick = async () => { try { await saveFile(`${videoId}_edit.mp4`, exported); $('dlgStat').textContent = '저장을 시작했어요.'; } catch (e) { $('dlgStat').textContent = saveMsg(e); } };

// 시험용 손잡이
window.EDITOR = { get state() { return state; }, get video() { return videoId; }, openVideo, seek, get ready() { return !!V; } };
openVideo($('video').value);
})();
