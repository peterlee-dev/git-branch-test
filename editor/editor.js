// ------------------------------------------------------------
// 재능교육 영상 편집기
// 편집본 = 장면(클립)을 이어 붙인 목록. 클립은 두 가지:
//   · 영상 장면: 어느 영상의 [in, out] 구간 (그 구간의 소리도 함께 따라감)
//   · 새 장면: 제목 카드 · 문구 카드 · 이미지 카드 · 암전 (편집기가 직접 그림, 소리 없음)
// 클립마다 들어오는 전환(컷 · 페이드 · 디졸브)을 고름
// 영상 쪽은 각 폴더 index.html 을 보이지 않는 iframe 으로 열어 window.VIDEO / draw(t) 로 그림 (editor/PROTOCOL.md)
// ------------------------------------------------------------
(() => {
const $ = id => document.getElementById(id);
const esc = s => String(s ?? '').replace(/[&<>"]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[ch]);
const clone = o => JSON.parse(JSON.stringify(o));
const getP = (o, path) => path.split('.').reduce((a, k) => a == null ? a : a[k], o);
function setP(o, path, v) { const ks = path.split('.'); const last = ks.pop(); ks.reduce((a, k) => a[k], o)[last] = v; }
const sleep = ms => new Promise(r => setTimeout(r, ms));
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const eOut = x => 1 - Math.pow(1 - clamp(x), 3);
const uid = () => Math.random().toString(36).slice(2, 9);
const W = 1920, H = 1080, FPS = 30, DECLICK = .012;
const RENDER_MODE = location.search.includes('render');
const STORE = 'jei-editor-project-v2';
const TITLE_OF = Object.fromEntries(window.VIDEOS.map(v => [v.id, v.title]));

// ---------- 새 장면 틀 ----------
const KR = "'Noto Sans KR', sans-serif";
const TEMPLATES = {
  title: { label: '제목 카드', dur: 3.5, props: { title: '새 제목', subtitle: '부제를 적어 주세요', bg: '#111111', fg: '#FFFFFF', accent: '#E60012', align: 'center', brand: '재능교육' },
    fields: [['title', '제목', 'text'], ['subtitle', '부제', 'text'], ['brand', '아래 회사 이름 (비우면 안 보임)', 'text'], ['align', '정렬', 'select', [['center', '가운데'], ['left', '왼쪽']]], ['bg', '배경', 'color'], ['fg', '글자', 'color'], ['accent', '강조색', 'color']] },
  text: { label: '문구 카드', dur: 4, props: { lines: '첫째 줄\n둘째 줄', size: 72, weight: 700, bg: '#F6F3F0', fg: '#1A1A1A', accent: '#E60012', align: 'center' },
    fields: [['lines', '문구 (줄마다 차례로 나와요)', 'textarea'], ['size', '크기', 'number', { min: 24, max: 180, step: 2 }], ['weight', '굵기', 'select', [100, 300, 400, 500, 700, 900]], ['align', '정렬', 'select', [['center', '가운데'], ['left', '왼쪽']]], ['bg', '배경', 'color'], ['fg', '글자', 'color'], ['accent', '첫 줄 강조색', 'color']] },
  image: { label: '이미지 카드', dur: 4, props: { image: '', caption: '설명을 적어 주세요', zoom: 8, bg: '#000000', fg: '#FFFFFF' },
    fields: [['image', '이미지', 'image'], ['caption', '설명 (비우면 안 보임)', 'text'], ['zoom', '천천히 확대 (%)', 'number', { min: 0, max: 30, step: 1 }], ['bg', '빈 곳 배경', 'color'], ['fg', '글자', 'color']] },
  black: { label: '암전', dur: 1.5, props: { bg: '#000000', text: '', fg: '#FFFFFF' },
    fields: [['text', '가운데 작은 글자 (선택)', 'text'], ['bg', '배경', 'color'], ['fg', '글자', 'color']] },
};
const TR_NAMES = [['cut', '컷'], ['fade', '페이드 (검은 화면)'], ['dissolve', '디졸브 (겹쳐 바뀜)']];

// ---------- 상태 ----------
let project = null;            // { kind, version: 2, clips: [...], sources: { id: content } }
let sel = null;                // 선택한 클립 id
let tCur = 0, playing = false, t0 = 0, exporting = false, peek = null;
let undoStack = [], lastSnap = '';
const sources = {};            // id -> { frame, win, V, S, audioBuf, loading }
const view = $('view'), vctx = view.getContext('2d');
const bufA = document.createElement('canvas'), bufB = document.createElement('canvas');
bufA.width = bufB.width = W; bufA.height = bufB.height = H;
const images = {};             // dataURL -> HTMLImageElement

// ---------- 영상 불러오기 (iframe) ----------
// 영상 페이지는 iframe srcdoc 으로 엶: 페이지를 받아 <script src> 를 본문으로 넣고, 글꼴은 받아 둔 파일로 등록
// (아티팩트처럼 자체 파일의 스크립트·글꼴·iframe 주소가 막힌 곳에서도 열리게)
const fontCache = {};
const fetchOK = async (url, kind) => { const r = await fetch(url); if (!r.ok) throw new Error(`${url} 을(를) 받지 못했어요 (${r.status})`); return kind === 'buf' ? r.arrayBuffer() : r.text(); };
const fontBuf = url => fontCache[url] || (fontCache[url] = fetchOK(url, 'buf'));
window.__JEI_FONTS = {};
async function buildSrcdoc(id) {
  const base = new URL(`${id}/`, location.href).href;
  let html = await fetchOK(`${id}/index.html`);
  const fonts = [];
  html = html.replace(/@font-face\s*\{[^}]*\}/g, rule => {
    const fam = /font-family:\s*['"]([^'"]+)['"]/.exec(rule), src = /url\(\s*['"]?([^'")]+)['"]?\s*\)/.exec(rule);
    if (!fam || !src) return rule;
    const w = /font-weight:\s*([^;}]+)/.exec(rule), st = /font-style:\s*([^;}]+)/.exec(rule);
    fonts.push({ family: fam[1], url: new URL(src[1], base).href, desc: { weight: w ? w[1].trim() : 'normal', style: st ? st[1].trim() : 'normal' } });
    return '';
  });
  const re = /<script\s+src="([^"]+)"\s*><\/script>/g, srcs = [...html.matchAll(re)].map(m => m[1]), code = {};
  await Promise.all(srcs.map(async u => { code[u] = await fetchOK(new URL(u, base).href); }));
  html = html.replace(re, (m, u) => `<script>${code[u].replace(/<\/script/gi, '<\\/script')}\n</script>`);
  const bufs = await Promise.all(fonts.map(f => fontBuf(f.url)));
  window.__JEI_FONTS[id] = fonts.map((f, i) => ({ ...f, buf: bufs[i] }));
  const boot = `<base href="${base}"><script>(function(){var F=(parent.__JEI_FONTS||{})[${JSON.stringify(id)}]||[];F.forEach(function(f){var ff=new FontFace(f.family,f.buf,f.desc);document.fonts.add(ff);ff.load();});})();</script>`;
  return /<head>/i.test(html) ? html.replace(/<head>/i, m => m + boot) : boot + html;
}
function ensureSource(id) {
  if (sources[id]) return sources[id].loading;
  const frame = document.createElement('iframe');
  frame.className = 'src-frame'; frame.title = '영상 그리기용 (보이지 않음)'; frame.setAttribute('aria-hidden', 'true'); frame.tabIndex = -1;
  const s = sources[id] = { frame, win: null, V: null, S: null, audioBuf: null, audioSrcs: [] };
  s.loading = (async () => {
    const name = TITLE_OF[id] || id;
    step(`${name} 파일을 받는 중…`);
    const html = await buildSrcdoc(id);
    step(`${name} 장면을 준비하는 중…`);
    const loaded = await Promise.race([new Promise(res => { frame.onload = () => res(true); frame.srcdoc = html; document.body.appendChild(frame); }), sleep(30000).then(() => false)]);
    if (!loaded) throw new Error(`${name} 페이지가 열리지 않아요.`);
    s.win = frame.contentWindow;
    if (!s.win || !s.win.ready) throw new Error(`${name} 페이지를 실행하지 못했어요.`);
    const ok = await Promise.race([Promise.resolve(s.win.ready).then(() => true), sleep(90000).then(() => false)]);
    if (!ok) throw new Error(`${name} 을(를) 준비하는 데 너무 오래 걸려요.`);
    s.V = s.win.VIDEO || null; s.S = s.V ? s.V.schema : null; s.dur = s.win.DURATION;
    s.canvas = s.V ? s.V.canvas : s.win.document.getElementById('c');
    if (s.V && project && project.sources[id]) s.V.apply(project.sources[id]);
    s.audioSrcs = ((s.S && s.S.audio) || []).map(a => `${id}/${a}`);
    s.audioReady = loadAudio(s);
    return s;
  })();
  s.loading.catch(() => { delete sources[id]; frame.remove(); });   // 다음에 다시 시도할 수 있게
  return s.loading;
}
function step(msg) { if (!$('busy').hidden) $('busy').textContent = msg; }
async function loadAudio(s) {
  for (const src of s.audioSrcs) {
    try { const r = await fetch(src); if (!r.ok) continue; s.audioBuf = await actx().decodeAudioData(await r.arrayBuffer()); mixDirty = true; if (playing) startAudio(tCur); return; } catch (e) {}
  }
}
let _actx = null;
const actx = () => _actx || (_actx = new (window.AudioContext || window.webkitAudioContext)());
const usedSources = () => [...new Set(project.clips.filter(c => c.type === 'video').map(c => c.src))];
async function ensureAll() { await Promise.all(usedSources().map(ensureSource)); }
function sourceContent(id) {   // 편집본에 저장된 이 영상의 문구·색 (없으면 기본값)
  if (!project.sources[id]) { const s = sources[id]; project.sources[id] = s && s.V ? clone(s.V.defaults) : {}; }
  return project.sources[id];
}

// ---------- 편집본 만들기 ----------
const scenesOf = s => (s.S && s.S.scenes && s.S.scenes.length ? s.S.scenes : [{ start: 0, end: s.dur, label: '전체' }]);
function videoClip(id, sc) { return { id: uid(), type: 'video', src: id, label: sc.label, in: +sc.start, out: +sc.end, tr: { type: 'cut', dur: .5 } }; }
function templateClip(kind) { const T = TEMPLATES[kind]; return { id: uid(), type: kind, label: T.label, dur: T.dur, props: clone(T.props), tr: { type: 'fade', dur: .4 } }; }
async function projectFromVideo(id, content) {
  const s = await ensureSource(id);
  let saved = null; try { saved = JSON.parse(localStorage.getItem('jei-editor-v1:' + id) || 'null'); } catch (e) {}
  const p = { kind: 'jei-video-project', version: 2, clips: scenesOf(s).map(sc => videoClip(id, sc)), sources: {} };
  if (s.V) p.sources[id] = clone(content || (saved && saved.content) || s.V.defaults);
  return p;
}
function fromV1(j) { return projectFromVideo(j.video || 'ai-math-trailer', j.content); }

// ---------- 배치 (디졸브는 앞 클립과 겹침) ----------
const clipLen = c => c.type === 'video' ? Math.max(.1, c.out - c.in) : Math.max(.2, +c.dur || 1);
let LAYOUT = [], TOTAL = 0;
function relayout() {
  let t = 0; LAYOUT = [];
  project.clips.forEach((c, i) => {
    const len = clipLen(c), prev = LAYOUT[i - 1];
    const d = i > 0 && c.tr && c.tr.type === 'dissolve' ? Math.min(+c.tr.dur || .5, len / 2, prev.len / 2) : 0;
    const start = Math.max(0, t - d);
    LAYOUT.push({ c, i, start, end: start + len, len, dis: d });
    t = start + len;
  });
  TOTAL = Math.max(.1, t);
}
const fadeLen = (c, other) => c.tr && c.tr.type === 'fade' ? Math.min(+c.tr.dur || .4, clipLen(c) / 2, other ? clipLen(other) / 2 : 9) : 0;
function edgeGains(e) {   // 이 클립이 들어올 때·나갈 때의 페이드 길이
  const next = LAYOUT[e.i + 1], prev = LAYOUT[e.i - 1];
  return { fin: e.dis || (prev ? fadeLen(e.c, prev.c) : 0), fout: next ? (next.dis || fadeLen(next.c, e.c)) : 0, disIn: e.dis > 0, disOut: next && next.dis > 0 };
}

// ---------- 그리기 ----------
function drawClip(ctx, c, local) {
  if (c.type === 'video') {
    const s = sources[c.src]; if (!s || !s.win) { ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); return; }
    s.win.draw(Math.min(Math.max(0, c.in + local), s.dur - 1e-3));
    ctx.drawImage(s.canvas, 0, 0, W, H);
  } else drawTemplate(ctx, c, local);
}
function renderFrame(T, ctx = vctx) {
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
  if (peek) { const s = sources[peek.src]; if (s && s.win) { s.win.draw(Math.min(peek.t, s.dur - 1e-3)); ctx.drawImage(s.canvas, 0, 0, W, H); } return; }
  const act = LAYOUT.filter(e => T >= e.start && T < e.end);
  if (!act.length) { ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); return; }
  const B = act[act.length - 1], A = act.length > 1 ? act[act.length - 2] : null;
  if (A && B.dis > 0) {   // 디졸브: 앞 장면 위에 새 장면이 서서히
    const ca = bufA.getContext('2d'), cb = bufB.getContext('2d');
    drawClip(ca, A.c, T - A.start); drawClip(cb, B.c, T - B.start);
    ctx.drawImage(bufA, 0, 0); ctx.globalAlpha = clamp((T - B.start) / B.dis); ctx.drawImage(bufB, 0, 0); ctx.globalAlpha = 1; return;
  }
  const e = B, local = T - e.start, g = edgeGains(e);
  drawClip(ctx, e.c, local);
  let dark = 0;
  if (g.fin && !g.disIn) dark = Math.max(dark, 1 - local / g.fin);
  if (g.fout && !g.disOut) dark = Math.max(dark, 1 - (e.len - local) / g.fout);
  if (dark > 0) { ctx.fillStyle = `rgba(0,0,0,${clamp(dark)})`; ctx.fillRect(0, 0, W, H); }
}
function wrapText(ctx, s, maxW) {
  const out = [];
  String(s).split('\n').forEach(par => { let line = ''; for (const ch of [...par]) { if (ctx.measureText(line + ch).width > maxW && line) { out.push(line); line = ch.trimStart(); } else line += ch; } out.push(line); });
  return out;
}
function drawTemplate(ctx, c, t) {
  const p = c.props || {};
  ctx.save(); ctx.fillStyle = p.bg || '#000'; ctx.fillRect(0, 0, W, H); ctx.textBaseline = 'middle';
  const left = p.align === 'left', x0 = left ? 200 : W / 2; ctx.textAlign = left ? 'left' : 'center';
  if (c.type === 'title') {
    const a = eOut((t - .15) / .7), b = eOut((t - .6) / .7), bar = eOut((t - .05) / .8);
    ctx.fillStyle = p.accent; const bw = 120 * bar; ctx.fillRect(left ? x0 : x0 - bw / 2, 380, bw, 10);
    ctx.globalAlpha = a; ctx.fillStyle = p.fg; ctx.font = `800 128px ${KR}`;
    const lines = wrapText(ctx, p.title, 1560).slice(0, 2); lines.forEach((l, i) => ctx.fillText(l, x0, 500 + i * 150 + 26 * (1 - a) - (lines.length - 1) * 75));
    ctx.globalAlpha = b; ctx.font = `400 46px ${KR}`; ctx.fillStyle = p.fg; ctx.globalAlpha = b * .8; ctx.fillText(p.subtitle || '', x0, 660 + (lines.length - 1) * 75 + 16 * (1 - b));
    if (p.brand) { const k = eOut((t - 1) / .6); ctx.globalAlpha = k; ctx.font = `700 34px ${KR}`; const w = ctx.measureText(p.brand).width; ctx.textAlign = 'left'; const bx = W - 140 - w; ctx.fillStyle = p.accent; ctx.fillRect(bx - 40, H - 150, 22, 22); ctx.fillStyle = p.fg; ctx.fillText(p.brand, bx, H - 139); }
  } else if (c.type === 'text') {
    const size = +p.size || 72; ctx.font = `${p.weight || 700} ${size}px ${KR}`;
    const lines = wrapText(ctx, p.lines, 1600).slice(0, 8), lh = size * 1.45, y0 = H / 2 - (lines.length - 1) * lh / 2;
    lines.forEach((l, i) => { const k = eOut((t - .2 - i * .45) / .6); ctx.globalAlpha = k; ctx.fillStyle = i === 0 && p.accent ? p.accent : p.fg; ctx.fillText(l, x0, y0 + i * lh + 24 * (1 - k)); });
  } else if (c.type === 'image') {
    const img = p.image && images[p.image];
    if (img && img.complete && img.naturalWidth) {
      const z = 1 + (+p.zoom || 0) / 100 * clamp(t / clipLen(c)), sc = Math.max(W / img.naturalWidth, H / img.naturalHeight) * z;
      const w = img.naturalWidth * sc, h = img.naturalHeight * sc; ctx.drawImage(img, (W - w) / 2, (H - h) / 2, w, h);
    } else { ctx.fillStyle = 'rgba(255,255,255,.35)'; ctx.font = `500 40px ${KR}`; ctx.textAlign = 'center'; ctx.fillText('이미지를 넣어 주세요', W / 2, H / 2); }
    if (p.caption) { const g = ctx.createLinearGradient(0, H - 360, 0, H); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,.65)'); ctx.globalAlpha = 1; ctx.fillStyle = g; ctx.fillRect(0, H - 360, W, 360); const k = eOut((t - .4) / .7); ctx.globalAlpha = k; ctx.textAlign = 'left'; ctx.fillStyle = p.fg; ctx.font = `600 52px ${KR}`; ctx.fillText(p.caption, 140, H - 150 + 16 * (1 - k)); }
  } else if (c.type === 'black') {
    if (p.text) { ctx.globalAlpha = eOut((t - .2) / .6); ctx.fillStyle = p.fg; ctx.font = `300 40px ${KR}`; ctx.textAlign = 'center'; ctx.letterSpacing = '8px'; ctx.fillText(p.text, W / 2, H / 2); }
  }
  ctx.restore();
}
function loadImage(url) { if (!url || images[url]) return; const im = new Image(); im.onload = () => show(tCur); im.src = url; images[url] = im; }

// ---------- 소리: 클립마다 원래 영상의 그 구간 소리를 이어 붙임 ----------
let MIX = null, mixDirty = true;
function buildMix() {
  const ctx = actx(), sr = ctx.sampleRate, N = Math.ceil(TOTAL * sr) + 1;
  const L = new Float32Array(N), R = new Float32Array(N);
  LAYOUT.forEach(e => {
    if (e.c.type !== 'video') return;
    const s = sources[e.c.src], buf = s && s.audioBuf; if (!buf) return;
    const g = edgeGains(e), fin = Math.max(DECLICK, g.fin), fout = g.fout || DECLICK, n = Math.floor(e.len * sr), o = Math.round(e.start * sr), si = Math.round(e.c.in * buf.sampleRate);
    const chL = buf.getChannelData(0), chR = buf.getChannelData(Math.min(1, buf.numberOfChannels - 1)), ratio = buf.sampleRate / sr;
    for (let k = 0; k < n && o + k < N; k++) {
      const j = Math.floor(si + k * ratio); if (j >= chL.length) break;
      const lt = k / sr, gain = Math.min(1, lt / fin, (e.len - lt) / fout);
      L[o + k] += chL[j] * gain; R[o + k] += chR[j] * gain;
    }
  });
  const last = LAYOUT[LAYOUT.length - 1];   // 끝은 부드럽게 닫음
  if (last && last.c.type === 'video') { const n = Math.min(N, Math.round(1.5 * sr)); for (let k = 0; k < n; k++) { const g = k / n; L[N - 1 - k] *= g; R[N - 1 - k] *= g; } }
  const b = ctx.createBuffer(2, N, sr); b.copyToChannel(L, 0); b.copyToChannel(R, 1);
  MIX = b; mixDirty = false; return b;
}
let node = null;
function stopAudio() { if (node) { try { node.stop(); } catch (e) {} node.disconnect(); node = null; } }
function startAudio(at) {
  stopAudio(); const ctx = actx(); if (ctx.state === 'suspended') ctx.resume();
  if (mixDirty || !MIX) buildMix();
  node = ctx.createBufferSource(); node.buffer = MIX; node.connect(ctx.destination); node.start(0, Math.min(at, MIX.duration - .01));
}

// ---------- 시간·재생 ----------
const tc = t => { const f = Math.round(t * FPS), s = Math.floor(f / FPS), fr = f % FPS, m = Math.floor(s / 60); return `${String(m).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}:${String(fr).padStart(2, '0')}`; };
function show(t) {
  if (!project) return;
  tCur = clamp(t, 0, TOTAL); renderFrame(Math.min(tCur, TOTAL - 1e-3));
  $('peekNote').hidden = !peek;
  $('tc').innerHTML = `${tc(tCur)}<small>/ ${tc(TOTAL)}</small>`;
  const ph = $('playhead'), box = $('timeline').getBoundingClientRect(), r = $('ruler').getBoundingClientRect();
  const rows = [...document.querySelectorAll('#timeline .tl-row')].filter(el => !el.hidden), lastRow = rows[rows.length - 1].getBoundingClientRect();
  ph.hidden = !!peek; ph.style.left = (r.left - box.left + tCur / TOTAL * r.width - 1) + 'px'; ph.style.top = (r.top - box.top) + 'px'; ph.style.height = (lastRow.bottom - r.top) + 'px';
}
function seek(t) { peek = null; show(t); if (playing) { t0 = performance.now() - tCur * 1000; startAudio(tCur); } }
function seekSource(src, st) {   // 영상의 그 시각이 편집본 어디에 있는지 찾아 이동, 없으면 원본을 잠깐 보여 줌
  const e = LAYOUT.find(e => e.c.type === 'video' && e.c.src === src && st >= e.c.in && st < e.c.out);
  if (e) return seek(e.start + (st - e.c.in));
  setPlaying(false); peek = { src, t: st }; show(tCur);
}
function loop(now) {
  if (!playing) return;
  const t = (now - t0) / 1000;
  if (t >= TOTAL) { setPlaying(false); show(TOTAL); return; }
  show(t); requestAnimationFrame(loop);
}
function setPlaying(on) {
  if (exporting || !project) return;
  playing = on; $('play').textContent = on ? '❚❚' : '▶'; $('play').setAttribute('aria-label', on ? '정지' : '재생');
  if (on) { peek = null; if (tCur >= TOTAL - .01) tCur = 0; t0 = performance.now() - tCur * 1000; startAudio(tCur); requestAnimationFrame(loop); }
  else stopAudio();
}
$('play').onclick = () => setPlaying(!playing);
window.addEventListener('resize', () => { drawTimeline(); show(tCur); });

// ---------- 바뀐 값 적용·저장·되돌리기 ----------
let saveTimer = 0, histTimer = 0, queued = false;
function changed({ audio = false, timeline = true, panel = false } = {}) {
  relayout(); if (audio) mixDirty = true;
  if (!queued) { queued = true; requestAnimationFrame(() => { queued = false; if (timeline) drawTimeline(); if (panel) buildPanels(); checkFits(); show(tCur); }); }
  clearTimeout(saveTimer); saveTimer = setTimeout(saveLocal, 500);
  clearTimeout(histTimer); histTimer = setTimeout(pushHistory, 350);
  $('saveState').textContent = '저장 중…';
  if (playing && audio) { clearTimeout(changed.re); changed.re = setTimeout(() => { if (playing) startAudio(tCur); }, 250); }
}
function saveLocal() {
  try { localStorage.setItem(STORE, JSON.stringify(project)); $('saveState').textContent = '이 브라우저에 저장됨'; }
  catch (e) { $('saveState').textContent = '자동 저장 안 됨 (이미지가 커서 그럴 수 있어요. 작업 파일로 저장하세요)'; }
}
function pushHistory() { const s = JSON.stringify(project); if (s !== lastSnap) { undoStack.push(lastSnap); if (undoStack.length > 80) undoStack.shift(); lastSnap = s; $('undo').disabled = false; } }
async function setProject(p, msg) {
  setPlaying(false); busy('장면을 불러오는 중…');
  project = p; peek = null;
  project.clips.forEach(c => { if (!c.tr) c.tr = { type: 'cut', dur: .5 }; if (c.type === 'image') loadImage(c.props.image); });
  try { await ensureAll(); } catch (e) { busy('영상을 열지 못했어요. ' + (e.message || '')); return; }
  usedSources().forEach(id => { const s = sources[id]; if (s.V) { s.V.apply(sourceContent(id)); project.sources[id] = clone(s.V.content); } });
  await Promise.all(usedSources().map(id => sources[id].audioReady));
  if (!project.clips.some(c => c.id === sel)) sel = project.clips[0] ? project.clips[0].id : null;
  relayout(); mixDirty = true; lastSnap = JSON.stringify(project);
  drawTimeline(); buildPanels(); busy(''); setControls(true); show(Math.min(tCur, TOTAL));
  if (msg) $('saveState').textContent = msg;
}
async function undo() {
  if (!undoStack.length) return; clearTimeout(histTimer);
  const prev = undoStack.pop(); lastSnap = prev; const keep = tCur;
  await setProject(JSON.parse(prev)); saveLocal(); tCur = keep; show(keep); $('undo').disabled = !undoStack.length;
}
$('undo').onclick = undo;

// ---------- 타임라인 ----------
const HUES = {}; window.VIDEOS.forEach((v, i) => { HUES[v.id] = Math.round(i * 360 / window.VIDEOS.length + 10) % 360; });
const pct = t => (t / TOTAL * 100) + '%';
function drawTimeline() {
  if (!project) return;
  const span = TOTAL, step = span > 240 ? 30 : span > 90 ? 10 : 5, tick = span > 240 ? 10 : span > 90 ? 5 : 1;
  let h = '';
  for (let s = 0; s <= span; s += tick) h += `<i class="${s % step ? '' : 'major'}" style="left:${pct(s)}"></i>` + (s % step || span - s < step * .6 ? '' : `<b style="left:${pct(s)}">${s >= 60 ? Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0') : s}</b>`);
  $('ruler').innerHTML = h;
  $('clips').innerHTML = LAYOUT.map(e => {
    const c = e.c, isV = c.type === 'video', hue = isV ? HUES[c.src] : 0;
    const name = isV ? `${esc(c.label || '장면')} · ${esc(TITLE_OF[c.src] || c.src)}` : esc(TEMPLATES[c.type].label + (clipText(c) ? ' · ' + clipText(c) : ''));
    const trMark = e.i > 0 && c.tr.type !== 'cut' ? `<em class="trm" title="${c.tr.type === 'fade' ? '페이드' : '디졸브'}">${c.tr.type === 'fade' ? '◐' : '⧉'}</em>` : '';
    return `<div class="clip${isV ? '' : ' tpl'}${sel === c.id ? ' sel' : ''}" data-id="${c.id}" style="left:${pct(e.start)};width:calc(${pct(e.len)} - 2px);${isV ? `--h:${hue}` : ''}" title="${name} (${e.len.toFixed(1)}초)">${trMark}<span class="h l" data-edge="l"></span><span class="nm">${name}</span><span class="h r" data-edge="r"></span></div>`;
  }).join('');
  drawBars();
  const snd = [];
  LAYOUT.forEach(e => { if (e.c.type !== 'video') return; const s = sources[e.c.src]; ((s && s.S && s.S.sounds) || []).forEach(x => { if (x.t >= e.c.in && x.t < e.c.out) snd.push({ t: e.start + x.t - e.c.in, label: x.label, big: x.big }); }); });
  $('soundsRow').hidden = !snd.length;
  $('sounds').innerHTML = snd.map(s => `<i class="${s.big ? 'big' : ''}" style="left:${pct(s.t)}" title="${esc(s.label)}"></i>`).join('');
}
const clipText = c => { const p = c.props || {}; return String(p.title || p.lines || p.caption || p.text || '').split('\n')[0].slice(0, 18); };
const selClip = () => project && project.clips.find(c => c.id === sel);
const selSrc = () => { const c = selClip(); return c && c.type === 'video' ? c.src : null; };

// 선택한 장면이 속한 영상의 '겹쳐 나오는 문구' 막대를 편집본 시간에 맞춰 보여 줌
function barItems() {
  const src = selSrc(), s = src && sources[src]; if (!s || !s.S || !s.S.timed) return null;
  const T = s.S.timed, list = getP(project.sources[src], T.path) || [], out = [];
  LAYOUT.forEach(e => { if (e.c.type !== 'video' || e.c.src !== src) return; list.forEach((it, i) => { const a = Math.max(it[T.startKey || 'start'], e.c.in), b = Math.min(it[T.endKey || 'end'], e.c.out); if (b > a) out.push({ i, it, x0: e.start + a - e.c.in, x1: e.start + b - e.c.in }); }); });
  return { T, list, out, src };
}
function drawBars() {
  const b = barItems(); $('barsRow').hidden = !b || !b.out.length; if (!b) return;
  const lane = [], ends = []; b.out.sort((p, q) => p.x0 - q.x0).forEach(o => { let l = ends.findIndex(x => o.x0 >= x - 1e-6); if (l < 0) l = ends.length; o.lane = l; ends[l] = o.x1; });
  $('bars').style.height = (Math.max(1, ends.length) * 34 - 4) + 'px';
  $('bars').innerHTML = b.out.map(o => `<div class="bar" data-i="${o.i}" style="left:${pct(o.x0)};width:${pct(o.x1 - o.x0)};top:${o.lane * 34}px" title="${esc(o.it[b.T.textKey || 'text'])}"><span class="h l" data-edge="l"></span>${esc(o.it[b.T.textKey || 'text']) || '(빈 칸)'}<span class="h r" data-edge="r"></span></div>`).join('');
}
const snap = t => Math.round(t * 20) / 20;
function timeAt(x) { const r = $('ruler').getBoundingClientRect(); return clamp((x - r.left) / r.width * TOTAL, 0, TOTAL); }
let drag = null;
$('ruler').addEventListener('pointerdown', e => { if (!project) return; drag = { kind: 'seek' }; $('ruler').setPointerCapture(e.pointerId); seek(timeAt(e.clientX)); });
$('clips').addEventListener('pointerdown', e => {
  if (!project || exporting) return;
  const el = e.target.closest('.clip'); $('clips').setPointerCapture(e.pointerId);
  if (!el) { drag = { kind: 'seek' }; seek(timeAt(e.clientX)); return; }
  const c = project.clips.find(c => c.id === el.dataset.id), L = LAYOUT.find(l => l.c === c);
  drag = { kind: 'clip', c, edge: e.target.dataset.edge || 'move', x: e.clientX, t: timeAt(e.clientX), in: c.in, out: c.out, dur: c.dur, start: L.start, moved: false };
  selectClip(c.id);
});
window.addEventListener('pointermove', e => {
  if (!drag) return;
  if (drag.kind === 'seek') return seek(timeAt(e.clientX));
  const d = timeAt(e.clientX) - drag.t;
  if (!drag.moved && Math.abs(e.clientX - drag.x) < 4) return; drag.moved = true;
  if (drag.kind === 'bar') return dragBar(d);
  const c = drag.c;
  if (drag.edge === 'l') {
    if (c.type === 'video') c.in = snap(clamp(drag.in + d, 0, c.out - .3)); else c.dur = snap(Math.max(.5, drag.dur - d));
    changed({ audio: true }); syncClipInputs(); peek = null; show(LAYOUT.find(l => l.c === c).start);
  } else if (drag.edge === 'r') {
    if (c.type === 'video') c.out = snap(clamp(drag.out + d, c.in + .3, sources[c.src].dur)); else c.dur = snap(Math.max(.5, drag.dur + d));
    changed({ audio: true }); syncClipInputs(); peek = null; const l = LAYOUT.find(l => l.c === c); show(l.end - .05);
  } else {   // 끌어서 순서 바꾸기
    const x = timeAt(e.clientX), others = LAYOUT.filter(l => l.c !== c);
    let idx = others.findIndex(l => x < (l.start + l.end) / 2); if (idx < 0) idx = others.length;
    const cur = project.clips.indexOf(c);
    if (idx !== cur) { project.clips.splice(cur, 1); project.clips.splice(idx, 0, c); changed({ audio: true }); }
    $('clips').classList.add('dragging');
  }
});
window.addEventListener('pointerup', () => {
  if (drag && drag.kind === 'clip') { $('clips').classList.remove('dragging'); if (!drag.moved) { const l = LAYOUT.find(l => l.c === drag.c); seek(l.start + Math.min(.6, l.len / 2)); } else show(tCur); }
  drag = null;
});
$('bars').addEventListener('pointerdown', e => {
  const el = e.target.closest('.bar'); if (!el) return; $('bars').setPointerCapture(e.pointerId);
  const b = barItems(), it = b.list[+el.dataset.i], T = b.T;
  drag = { kind: 'bar', b, it, edge: e.target.dataset.edge || 'move', x: e.clientX, t: timeAt(e.clientX), s: it[T.startKey || 'start'], e: it[T.endKey || 'end'], moved: false };
});
function dragBar(d) {
  const { b, it } = drag, T = b.T, sk = T.startKey || 'start', ek = T.endKey || 'end', min = T.minLen || .4, dur = sources[b.src].dur;
  if (drag.edge === 'l') it[sk] = snap(clamp(drag.s + d, 0, drag.e - min));
  else if (drag.edge === 'r') it[ek] = snap(clamp(drag.e + d, drag.s + min, dur));
  else { const len = drag.e - drag.s; it[sk] = snap(clamp(drag.s + d, 0, dur - len)); it[ek] = snap(it[sk] + len); }
  sources[b.src].V.apply(project.sources[b.src]); changed({ panel: false }); syncItemInputs();
  seekSource(b.src, drag.edge === 'r' ? it[ek] - .2 : it[sk] + .5);
}
document.addEventListener('keydown', e => {
  if (e.target.closest('input, select, textarea') || exporting || !project) return;
  if (e.code === 'Space') { e.preventDefault(); setPlaying(!playing); }
  if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { e.preventDefault(); const d = (e.shiftKey ? 1 : 1 / FPS) * (e.key === 'ArrowRight' ? 1 : -1); seek(Math.round((tCur + d) * FPS) / FPS); }
  if ((e.metaKey || e.ctrlKey) && e.key === 'z') { e.preventDefault(); undo(); }
  if ((e.key === 'Delete' || e.key === 'Backspace') && sel) { e.preventDefault(); removeClip(sel); }
});

// ---------- 클립 다루기 ----------
function selectClip(id, { tab } = {}) {
  const was = selSrc(); sel = id;
  document.querySelectorAll('.clip').forEach(el => el.classList.toggle('sel', el.dataset.id === id));
  drawBars(); const now = selSrc();
  if (was !== now || tab) buildPanels(tab || currentTab());
  else buildClipPane();
  show(tCur);
}
function insertClips(list, where = 'after') {
  const i = sel ? project.clips.findIndex(c => c.id === sel) : project.clips.length - 1;
  const at = where === 'end' ? project.clips.length : i + 1;
  project.clips.splice(at, 0, ...list); sel = list[0].id;
  changed({ audio: true, panel: true });
  requestAnimationFrame(() => requestAnimationFrame(() => { const l = LAYOUT.find(l => l.c === list[0]); if (l) seek(l.start + Math.min(.6, l.len / 2)); }));
}
function removeClip(id) {
  if (project.clips.length <= 1) { $('saveState').textContent = '장면이 하나는 있어야 해요.'; return; }
  const i = project.clips.findIndex(c => c.id === id); project.clips.splice(i, 1);
  sel = (project.clips[i] || project.clips[i - 1]).id; changed({ audio: true, panel: true });
}
function moveClip(id, dir) { const i = project.clips.findIndex(c => c.id === id), j = i + dir; if (j < 0 || j >= project.clips.length) return; const [c] = project.clips.splice(i, 1); project.clips.splice(j, 0, c); changed({ audio: true }); buildClipPane(); }
function duplicateClip(id) { const c = project.clips.find(c => c.id === id); insertClips([{ ...clone(c), id: uid() }]); }
function splitClip(id) {   // 재생 위치에서 둘로 나눔
  const c = project.clips.find(c => c.id === id), l = LAYOUT.find(l => l.c === c), local = tCur - l.start;
  if (local < .3 || l.len - local < .3) { $('saveState').textContent = '재생 위치를 이 장면 안쪽으로 옮긴 뒤 나눠 주세요.'; return; }
  const b = { ...clone(c), id: uid(), tr: { type: 'cut', dur: .5 } };
  if (c.type === 'video') { b.in = snap(c.in + local); c.out = b.in; } else { b.dur = snap(l.len - local); c.dur = snap(local); }
  project.clips.splice(project.clips.indexOf(c) + 1, 0, b); changed({ audio: true, panel: true });
}

// ---------- 오른쪽 패널 ----------
function currentTab() { const b = document.querySelector('#tabs button[aria-selected="true"]'); return b ? b.dataset.tab : '__clip'; }
function inputHTML(f, id, value, data) {
  const attrs = `id="${id}" ${data}`;
  if (f.type === 'color') return `<input type="color" ${attrs} value="${esc(value)}" aria-label="${esc(f.label)}">`;
  if (f.type === 'number') return `<input type="number" ${attrs} value="${esc(value)}"${f.step != null ? ` step="${f.step}"` : ''}${f.min != null ? ` min="${f.min}"` : ''}${f.max != null ? ` max="${f.max}"` : ''}>`;
  if (f.type === 'select') return `<select ${attrs}>${(f.options || []).map(o => { const [v, n] = Array.isArray(o) ? o : [o, o]; return `<option value="${esc(v)}"${String(v) === String(value) ? ' selected' : ''}>${esc(n)}</option>`; }).join('')}</select>`;
  if (f.type === 'textarea') return `<textarea ${attrs} rows="3">${esc(value)}</textarea>`;
  return `<input type="text" ${attrs} value="${esc(value)}">`;
}
let seq = 0;
function buildPanels(tab) {
  if (!project) return;
  const src = selSrc(), s = src && sources[src], S = s && s.S;
  const tabs = [{ id: '__add', label: '장면 추가' }, { id: '__clip', label: '선택한 장면' }, ...((S && S.tabs) || (S ? [{ id: 'text', label: '문구' }] : [])), { id: '__info', label: '도움말' }];
  const want = tab || currentTab(), active = tabs.some(t => t.id === want) ? want : '__clip';
  $('tabs').innerHTML = tabs.map(t => `<button role="tab" data-tab="${t.id}" aria-selected="${t.id === active}">${esc(t.label)}</button>`).join('');
  let html = `<div class="pane" data-pane="__add" hidden>${libraryHTML()}</div><div class="pane" data-pane="__clip" hidden id="clipPane"></div>`;
  if (S) (S.tabs || [{ id: 'text' }]).forEach((t, ti) => { html += `<div class="pane" data-pane="${t.id}" hidden>${sourcePaneHTML(src, t, ti)}</div>`; });
  html += `<div class="pane" data-pane="__info" hidden>${infoHTML()}</div>`;
  $('panes').innerHTML = html; buildClipPane(); switchTab(active); checkFits();
}
function libraryHTML() {
  return `<div class="group"><div class="group-head"><h2>새 장면</h2></div><p class="note">선택한 장면 바로 뒤에 들어가요.</p>
    <div class="tpl-grid">${Object.entries(TEMPLATES).map(([k, T]) => `<button class="tpl-btn" data-add-tpl="${k}"><b>${T.label}</b><small>${T.dur}초</small></button>`).join('')}</div></div>
    <div class="group"><div class="group-head"><h2>영상 장면</h2></div><p class="note">영상을 펼쳐 장면을 고르세요. 장면의 소리도 함께 들어가요.</p>
    ${window.VIDEOS.map(v => `<details class="lib" data-lib="${v.id}"><summary>${esc(v.title)}</summary><div class="lib-list" id="lib-${v.id}"><p class="note">불러오는 중…</p></div></details>`).join('')}</div>`;
}
async function fillLibrary(id) {
  const box = $('lib-' + id); if (!box || box.dataset.done) return; box.dataset.done = '1';
  let s; try { s = await ensureSource(id); } catch (e) { box.innerHTML = `<p class="note">영상을 열지 못했어요.</p>`; return; }
  const scs = scenesOf(s);
  box.innerHTML = `<button class="btn small" data-add-all="${id}">장면 ${scs.length}개 모두 넣기</button>` + scs.map((sc, i) => `<div class="lib-item"><canvas width="160" height="90" id="th-${id}-${i}"></canvas><div><b>${esc(sc.label)}</b><small>${(sc.end - sc.start).toFixed(1)}초</small></div><button class="btn small" data-add-scene="${id}" data-i="${i}">넣기</button></div>`).join('');
  for (let i = 0; i < scs.length; i++) {   // 장면 가운데 한 장을 작게
    await sleep(0); const cv = $(`th-${id}-${i}`); if (!cv) return;
    s.win.draw(Math.min((scs[i].start + scs[i].end) / 2, s.dur - 1e-3)); cv.getContext('2d').drawImage(s.canvas, 0, 0, 160, 90);
  }
  show(tCur);
}
function clipPaneHTML() {
  const c = selClip(); if (!c) return '<div class="group"><p class="note">타임라인에서 장면을 눌러 고르세요.</p></div>';
  const i = project.clips.indexOf(c), l = LAYOUT[i], isV = c.type === 'video', s = isV && sources[c.src];
  let h = `<div class="group"><div class="group-head"><h2>${isV ? esc(c.label || '장면') : TEMPLATES[c.type].label}</h2><button class="jump" data-seq="${l.start + Math.min(.6, l.len / 2)}">▶ ${tc(l.start)}</button></div>
    <p class="note">${isV ? `${esc(TITLE_OF[c.src])}의 ${c.in.toFixed(2)}–${c.out.toFixed(2)}초` : '편집기에서 그리는 새 장면이에요. 소리는 없어요.'} · 길이 ${l.len.toFixed(1)}초 · ${i + 1}번째</p>
    <div class="acts">
      <button class="btn small" data-act="up" ${i === 0 ? 'disabled' : ''}>◀ 앞으로</button>
      <button class="btn small" data-act="down" ${i === project.clips.length - 1 ? 'disabled' : ''}>뒤로 ▶</button>
      <button class="btn small" data-act="dup">복제</button>
      <button class="btn small" data-act="split">재생 위치에서 나누기</button>
      <button class="btn small danger" data-act="del">삭제</button>
    </div></div>
    <div class="group"><div class="group-head"><h2>길이</h2></div>`;
  if (isV) h += `<div class="row"><label class="field"><span>원본 시작(초)</span><input type="number" id="ci-in" data-clip="in" step="0.1" min="0" max="${s.dur}" value="${c.in}"></label><label class="field"><span>원본 끝(초)</span><input type="number" id="ci-out" data-clip="out" step="0.1" min="0" max="${s.dur}" value="${c.out}"></label></div><p class="note">타임라인에서 장면 양 끝을 끌어도 잘라져요. 원본 길이 ${s.dur.toFixed(1)}초.</p>`;
  else h += `<label class="field"><span>길이(초)</span><input type="number" id="ci-dur" data-clip="dur" step="0.5" min="0.5" max="60" value="${c.dur}"></label>`;
  h += `</div><div class="group"><div class="group-head"><h2>들어올 때 전환</h2></div>${i === 0 ? '<p class="note">첫 장면이라 전환이 없어요.</p>' : `<div class="row"><label class="field"><span>전환</span><select id="ci-tr" data-clip="tr.type">${TR_NAMES.map(([v, n]) => `<option value="${v}"${c.tr.type === v ? ' selected' : ''}>${n}</option>`).join('')}</select></label><label class="field"><span>전환 길이(초)</span><input type="number" id="ci-trd" data-clip="tr.dur" step="0.1" min="0.1" max="3" value="${c.tr.dur}"${c.tr.type === 'cut' ? ' disabled' : ''}></label></div><p class="note">소리도 같은 길이로 부드럽게 이어져요.</p>`}</div>`;
  if (!isV) h += `<div class="group"><div class="group-head"><h2>내용</h2></div>${TEMPLATES[c.type].fields.map(([k, label, type, opt]) => {
    const id = 'tp-' + k, v = c.props[k];
    if (type === 'image') return `<div class="field"><span>${label}</span><div class="row"><button class="btn small" data-pick-image>이미지 고르기</button>${v ? '<span class="note">넣은 이미지가 있어요</span>' : ''}</div></div>`;
    if (type === 'color') return `<div class="color"><input type="color" id="${id}" data-prop="${k}" value="${esc(v)}" aria-label="${label}"><div><span>${label}</span></div><span></span></div>`;
    const f = { type, label, ...(type === 'select' ? { options: opt } : opt || {}) };
    return `<label class="field"><span>${label}</span>${inputHTML(f, id, v, `data-prop="${k}" data-type="${type}"`)}</label>`;
  }).join('')}</div>`;
  else if (s && s.S) h += `<div class="group"><p class="note">이 장면의 문구·색은 위쪽 탭(${(s.S.tabs || []).map(t => esc(t.label)).join(', ')})에서 고쳐요. 같은 영상에서 온 장면에 모두 반영돼요.</p></div>`;
  return h;
}
function buildClipPane() { const p = $('clipPane'); if (p) p.innerHTML = clipPaneHTML(); }
function syncClipInputs() { const c = selClip(); if (!c) return; [['ci-in', c.in], ['ci-out', c.out], ['ci-dur', c.dur]].forEach(([id, v]) => { const el = $(id); if (el && document.activeElement !== el) el.value = v; }); }
function sourcePaneHTML(src, tab, ti) {
  const S = sources[src].S, content = project.sources[src]; let inner = `<div class="group"><p class="note src-title">${esc(TITLE_OF[src])}의 내용이에요. 이 영상에서 온 장면에 모두 반영돼요.</p></div>`;
  if (ti === 0 && S.warnings && S.warnings.length) inner += `<div class="group">${S.warnings.map(w => `<p class="alert">${esc(w)}</p>`).join('')}</div>`;
  if (ti === 0 && S.timed) inner += `<div class="group"><div class="group-head"><h2>${esc(S.timed.label || '문구')}</h2></div><p class="note">나오는 시간은 타임라인의 문구 막대를 끌어도 바뀌어요.</p>${(getP(content, S.timed.path) || []).map((it, i) => itemHTML(S, it, i)).join('')}</div>`;
  (S.groups || []).filter(g => (g.tab || (S.tabs && S.tabs[0].id)) === tab.id).forEach(g => {
    const fields = g.fields.map(f => fieldHTML(f, g, content)).join('');
    inner += `<div class="group"><div class="group-head"><h2>${esc(g.title)}</h2>${g.at != null ? `<button class="jump" data-at="${g.at}">▶ ${(+g.at).toFixed(1)}초</button>` : ''}</div>${g.note ? `<p class="note">${esc(g.note)}</p>` : ''}${g.columns === 2 ? `<div class="cols2">${fields}</div>` : fields}</div>`;
  });
  return inner;
}
function fieldHTML(f, g, content) {
  const id = 'f' + (seq++), at = f.at ?? g.at, data = `data-path="${esc(f.path)}" data-type="${f.type || 'text'}"${at != null ? ` data-at="${at}"` : ''}`, val = getP(content, f.path);
  if (f.type === 'color') return `<div class="color">${inputHTML(f, id, val, data)}<div><span>${esc(f.label)}</span>${f.desc ? `<small>${esc(f.desc)}</small>` : ''}</div>${at != null ? `<button class="jump" data-at="${at}">▶ ${(+at).toFixed(1)}초</button>` : '<span></span>'}</div>`;
  return `<label class="field"><span>${esc(f.label)}</span>${inputHTML(f, id, val, data)}${f.fit ? `<span class="warn" data-fitfor="${id}" hidden></span>` : ''}</label>`;
}
function itemHTML(S, it, i) {
  const T = S.timed, fs = T.fields, main = fs.filter(f => f.type === 'text' || f.type === 'textarea'), rest = fs.filter(f => !main.includes(f));
  const one = f => { const id = `it${i}-${f.key}`; return `<label class="field"><span>${esc(f.key === (T.textKey || 'text') ? `${f.label} ${i + 1}` : f.label)}</span>${inputHTML(f, id, it[f.key], `data-item="${i}" data-key="${f.key}" data-type="${f.type || 'text'}"`)}${f.fitFrom || f.fit ? `<span class="warn" data-fitfor="${id}" hidden></span>` : ''}</label>`; };
  const rows = []; for (let k = 0; k < rest.length; k += 3) rows.push(`<div class="row">${rest.slice(k, k + 3).map(one).join('')}</div>`);
  return `<div class="item" data-item-block="${i}">${main.map(one).join('')}${rows.join('')}</div>`;
}
function syncItemInputs() { const b = drag && drag.b; if (!b) return; const i = b.list.indexOf(drag.it), T = b.T; [T.startKey || 'start', T.endKey || 'end'].forEach(k => { const el = $(`it${i}-${k}`); if (el) el.value = drag.it[k]; }); }
function infoHTML() {
  return `<div class="group"><div class="group-head"><h2>편집본 만들기</h2></div>
    <p class="note"><b>장면 추가</b> 탭에서 새 장면(제목·문구·이미지·암전)이나 다른 영상의 장면을 넣어요. 선택한 장면 바로 뒤에 들어가요.</p>
    <p class="note">타임라인의 장면을 끌면 순서가 바뀌고, 양 끝을 끌면 앞뒤가 잘려요. 선택한 장면은 <kbd>Delete</kbd>로 지워요.</p>
    <p class="note">장면을 옮기면 그 장면의 소리도 같이 옮겨져서, 장면 안에서는 화면과 소리가 맞아요. 장면 사이에서는 음악이 바뀌니 <b>페이드</b>나 <b>디졸브</b> 전환을 쓰면 자연스러워요.</p></div>
    <div class="group"><div class="group-head"><h2>저장</h2></div>
    <p class="note">편집본은 이 브라우저에 자동 저장돼요. 보관하거나 넘기려면 <b>작업 파일 저장</b>으로 JSON 파일을 받아 두고 <b>불러오기</b>로 다시 여세요.</p></div>
    <div class="group"><div class="group-head"><h2>MP4 만들기</h2></div>
    <p class="note"><b>MP4 내보내기</b>는 이 브라우저에서 ${Math.round(TOTAL * FPS)}장을 한 장씩 그려 1920×1080, ${FPS}fps 영상을 만들어요. 크롬이나 엣지 최신 버전에서 돼요.</p>
    <p class="note">저장소에서 최고 화질로 만들려면 <code>node editor/render.mjs 작업파일.json</code></p></div>`;
}
function switchTab(id) {
  document.querySelectorAll('#tabs button').forEach(b => b.setAttribute('aria-selected', b.dataset.tab === id));
  document.querySelectorAll('#panes .pane').forEach(p => p.hidden = p.dataset.pane !== id);
}
$('tabs').onclick = e => { const b = e.target.closest('button'); if (b) switchTab(b.dataset.tab); };

const panes = $('panes');
panes.addEventListener('toggle', e => { const d = e.target.closest && e.target.closest('details[data-lib]'); if (d && d.open) fillLibrary(d.dataset.lib); }, true);
panes.addEventListener('click', async e => {
  const t = e.target.closest('button'); if (!t || !project) return;
  if (t.dataset.addTpl) { insertClips([templateClip(t.dataset.addTpl)]); return; }
  if (t.dataset.addScene) { const s = await ensureSource(t.dataset.addScene); addSourceIfNew(t.dataset.addScene); insertClips([videoClip(t.dataset.addScene, scenesOf(s)[+t.dataset.i])]); return; }
  if (t.dataset.addAll) { const s = await ensureSource(t.dataset.addAll); addSourceIfNew(t.dataset.addAll); insertClips(scenesOf(s).map(sc => videoClip(t.dataset.addAll, sc))); return; }
  if (t.dataset.act) { const id = sel; ({ up: () => moveClip(id, -1), down: () => moveClip(id, 1), dup: () => duplicateClip(id), del: () => removeClip(id), split: () => splitClip(id) })[t.dataset.act](); return; }
  if (t.dataset.pickImage != null) { $('imgIn').click(); return; }
  if (t.dataset.seq) { seek(+t.dataset.seq); return; }
  if (t.classList.contains('jump') && t.dataset.at) { seekSource(selSrc(), +t.dataset.at); }
});
function addSourceIfNew(id) { const s = sources[id]; if (s.V && !project.sources[id]) { project.sources[id] = clone(s.V.defaults); s.V.apply(project.sources[id]); } }
panes.addEventListener('input', e => {
  const el = e.target; if (!project) return;
  const c = selClip();
  if (el.dataset.clip && c) {
    const k = el.dataset.clip;
    if (k === 'tr.type') { c.tr.type = el.value; const d = $('ci-trd'); if (d) d.disabled = el.value === 'cut'; changed({ audio: true }); return; }
    const v = parseFloat(el.value); if (!isFinite(v)) return;
    if (k === 'tr.dur') c.tr.dur = clamp(v, .1, 3);
    else if (k === 'dur') c.dur = clamp(v, .5, 120);
    else if (k === 'in') c.in = clamp(v, 0, c.out - .3);
    else if (k === 'out') c.out = clamp(v, c.in + .3, sources[c.src].dur);
    changed({ audio: true }); return;
  }
  if (el.dataset.prop && c) { c.props[el.dataset.prop] = el.dataset.type === 'number' ? (parseFloat(el.value) || 0) : (el.dataset.type === 'select' && !isNaN(el.value) && typeof TEMPLATES[c.type].props[el.dataset.prop] === 'number' ? +el.value : el.value); changed(); return; }
  const src = selSrc(); if (!src) return;
  const S = sources[src].S, content = project.sources[src];
  const v = el.dataset.type === 'number' ? parseFloat(el.value) : (el.dataset.type === 'select' && !isNaN(el.value) && typeof origVal(el, content, S) === 'number' ? +el.value : el.value);
  if (el.dataset.type === 'number' && !isFinite(v)) return;
  if (el.dataset.path) setP(content, el.dataset.path, v);
  else if (el.dataset.item != null) {
    const T = S.timed, it = getP(content, T.path)[+el.dataset.item], sk = T.startKey || 'start', ek = T.endKey || 'end', min = T.minLen || .4; it[el.dataset.key] = v;
    if (el.dataset.key === sk || el.dataset.key === ek) { it[sk] = clamp(it[sk], 0, sources[src].dur - min); it[ek] = clamp(it[ek], it[sk] + min, sources[src].dur); }
  } else return;
  sources[src].V.apply(content); changed({ timeline: !!el.dataset.item || false });
  if (el.dataset.item != null) drawBars();
});
const origVal = (el, content, S) => el.dataset.path ? getP(content, el.dataset.path) : getP(content, S.timed.path)[+el.dataset.item]?.[el.dataset.key];
panes.addEventListener('focusin', e => {
  const el = e.target, src = selSrc(); if (!src) return;
  if (el.dataset.at) seekSource(src, +el.dataset.at);
  if (el.dataset.item != null) { const S = sources[src].S, it = getP(project.sources[src], S.timed.path)[+el.dataset.item]; if (it) seekSource(src, it[S.timed.startKey || 'start'] + .6); }
});
$('imgIn').onchange = async () => {   // 이미지는 1920px 이하 JPEG 로 줄여 작업 파일에 담음
  const f = $('imgIn').files[0]; $('imgIn').value = ''; const c = selClip(); if (!f || !c || c.type !== 'image') return;
  const url = URL.createObjectURL(f), im = new Image(); await new Promise((r, j) => { im.onload = r; im.onerror = j; im.src = url; }).catch(() => null);
  if (!im.naturalWidth) { $('saveState').textContent = '이미지를 읽지 못했어요.'; return; }
  const k = Math.min(1, 1920 / im.naturalWidth, 1920 / im.naturalHeight), cv = document.createElement('canvas'); cv.width = Math.round(im.naturalWidth * k); cv.height = Math.round(im.naturalHeight * k);
  cv.getContext('2d').drawImage(im, 0, 0, cv.width, cv.height); URL.revokeObjectURL(url);
  const data = cv.toDataURL('image/jpeg', .86); loadImage(data); c.props.image = data; images[data].onload = () => show(tCur); changed(); buildClipPane();
};

function measure(win, s, size, weight, family, spacing) { const m = win.document.createElement('canvas').getContext('2d'); m.font = `${weight || 400} ${size}px ${family || "'Noto Sans KR'"}`; return Math.max(...String(s).split('\n').map(line => m.measureText(line).width + (spacing || 0) * [...line].length)); }
function checkFits() {
  const src = selSrc(); if (!src) return; const s = sources[src], S = s.S, content = project.sources[src];
  document.querySelectorAll('[data-fitfor]').forEach(w => {
    const el = $(w.dataset.fitfor); if (!el) return; let fit;
    if (el.dataset.path) { for (const g of S.groups || []) for (const f of g.fields) if (f.path === el.dataset.path) fit = f.fit; }
    else { const f = S.timed.fields.find(f => f.key === el.dataset.key), it = getP(content, S.timed.path)[+el.dataset.item]; fit = f.fit || (f.fitFrom && it && { size: it[f.fitFrom.size], weight: it[f.fitFrom.weight], spacing: it[f.fitFrom.spacing], family: f.family, max: f.max }); }
    if (!fit) return;
    const over = measure(s.win, el.value, fit.size, fit.weight, fit.family, fit.spacing) > fit.max;
    w.hidden = !over; w.textContent = over ? '글자가 길어 화면 밖으로 넘칠 수 있어요. 줄이거나 크기를 낮춰 주세요.' : '';
  });
}

// ---------- 새로 만들기 ----------
$('newBtn').onclick = () => { $('newList').innerHTML = window.VIDEOS.map(v => `<button class="btn" data-new="${v.id}">${esc(v.title)}</button>`).join('') + `<button class="btn" data-new="__blank">빈 편집본 (제목 카드 하나)</button>`; $('newDlg').showModal(); };
$('newList').onclick = async e => {
  const b = e.target.closest('[data-new]'); if (!b) return; $('newDlg').close();
  const id = b.dataset.new; pushHistory();
  if (id === '__blank') await setProject({ kind: 'jei-video-project', version: 2, clips: [templateClip('title')], sources: {} }, '새 편집본을 만들었어요');
  else { busy('영상을 불러오는 중…'); await setProject(await projectFromVideo(id), `${TITLE_OF[id]}에서 시작했어요`); }
  tCur = 0; show(0); saveLocal(); undoStack.push(lastSnap);
};
$('newCancel').onclick = () => $('newDlg').close();

// ---------- 파일 저장·불러오기 ----------
let downloads = null;
const dlReady = window.claude?.use ? window.claude.use('downloads').then(d => (downloads = d)).catch(() => null) : Promise.resolve(null);
async function saveFile(filename, blob) {
  await dlReady;
  if (downloads) { await downloads.save({ filename, data: blob }); return; }
  if (window.claude?.use) throw { code: 'unavailable' };
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = filename; a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 5000);
}
const saveMsg = e => e?.code === 'declined' ? '저장을 취소했어요.' : e?.code === 'rate_limited' ? '이미 열린 저장 창이 있어요. 잠시 뒤 다시 눌러 주세요.' : '이 화면에서는 파일을 저장할 수 없어요.';
$('saveJson').onclick = async () => {
  try { await saveFile('jei_video_project.json', new Blob([JSON.stringify(project, null, 1)], { type: 'application/json' })); $('saveState').textContent = '작업 파일을 저장했어요'; } catch (e) { $('saveState').textContent = saveMsg(e); }
};
$('load').onclick = () => $('fileIn').click();
async function loadProjectJSON(j) {
  if (!j || typeof j !== 'object') throw new Error('bad');
  if (j.version === 2 && Array.isArray(j.clips)) return setProject(j);
  if (typeof j.content === 'object') return setProject(await fromV1(j));
  throw new Error('bad');
}
$('fileIn').onchange = async () => {
  const f = $('fileIn').files[0]; $('fileIn').value = ''; if (!f) return;
  try { pushHistory(); await loadProjectJSON(JSON.parse(await f.text())); $('saveState').textContent = `${f.name} 을(를) 불러왔어요`; saveLocal(); }
  catch (e) { $('saveState').textContent = '이 편집기에서 저장한 작업 파일이 아니에요.'; }
};

// ---------- MP4 내보내기 (WebCodecs + mp4-muxer) ----------
let cancelExport = false, exported = null;
async function pickVideoConfig() {
  for (const [codec, mux] of [['avc1.640028', 'avc'], ['avc1.4d0028', 'avc'], ['avc1.42003e', 'avc'], ['vp09.00.40.08', 'vp9']]) {
    const cfg = { codec, width: W, height: H, bitrate: 14e6, framerate: FPS, ...(mux === 'avc' ? { avc: { format: 'avc' } } : {}) };
    try { if ((await VideoEncoder.isConfigSupported(cfg)).supported) return { cfg, mux }; } catch (e) {}
  }
  return null;
}
async function pickAudioConfig(sr) {
  for (const [codec, mux] of [['mp4a.40.2', 'aac'], ['opus', 'opus']]) {
    const cfg = { codec, sampleRate: sr, numberOfChannels: 2, bitrate: 192000 };
    try { if ((await AudioEncoder.isConfigSupported(cfg)).supported) return { cfg, mux }; } catch (e) {}
  }
  return null;
}
function dlg(title, msg) { $('dlgTitle').textContent = title; $('dlgMsg').textContent = msg; }
async function exportMp4() {
  if (!project) return;
  $('dlgBar').style.width = '0'; $('dlgSave').hidden = true; $('dlgStat').textContent = '';
  if (!('VideoEncoder' in window) || !window.Mp4Muxer) { dlg('이 브라우저에서는 만들 수 없어요', '크롬이나 엣지 최신 버전에서 열어 주세요.'); $('dlgCancel').textContent = '닫기'; $('dlg').showModal(); return; }
  setPlaying(false); peek = null; exporting = true; cancelExport = false; exported = null; $('dlgCancel').textContent = '취소';
  dlg('MP4 만드는 중', '한 장면씩 그리고 있어요. 이 탭을 닫거나 다른 탭으로 옮기지 마세요.'); $('dlg').showModal();
  const keepT = tCur, LEN = Math.min(TOTAL, window.__EXPORT_SECONDS__ || TOTAL);
  try {
    const vcfg = await pickVideoConfig(); if (!vcfg) throw new Error('이 브라우저는 영상 인코딩(H.264·VP9)을 지원하지 않아요.');
    const mix = buildMix(), hasSound = LAYOUT.some(e => e.c.type === 'video' && sources[e.c.src].audioBuf);
    const acfg = hasSound && 'AudioEncoder' in window ? await pickAudioConfig(mix.sampleRate) : null;
    const target = new Mp4Muxer.ArrayBufferTarget();
    const muxer = new Mp4Muxer.Muxer({ target, fastStart: 'in-memory', firstTimestampBehavior: 'offset', video: { codec: vcfg.mux, width: W, height: H, frameRate: FPS }, ...(acfg ? { audio: { codec: acfg.mux, numberOfChannels: 2, sampleRate: mix.sampleRate } } : {}) });
    let encErr = null;
    const venc = new VideoEncoder({ output: (c, m) => muxer.addVideoChunk(c, m), error: e => (encErr = e) }); venc.configure(vcfg.cfg);
    if (acfg) {
      const aenc = new AudioEncoder({ output: (c, m) => muxer.addAudioChunk(c, m), error: e => (encErr = e) }); aenc.configure(acfg.cfg);
      const sr = mix.sampleRate, n = Math.min(mix.length, Math.round(LEN * sr)), L = mix.getChannelData(0), R = mix.getChannelData(1), BLK = 4800;
      for (let o = 0; o < n; o += BLK) { const len = Math.min(BLK, n - o), data = new Float32Array(len * 2); data.set(L.subarray(o, o + len), 0); data.set(R.subarray(o, o + len), len); const ad = new AudioData({ format: 'f32-planar', sampleRate: sr, numberOfFrames: len, numberOfChannels: 2, timestamp: Math.round(o / sr * 1e6), data }); aenc.encode(ad); ad.close(); }
      await aenc.flush(); aenc.close();
    }
    const frames = Math.round(LEN * FPS), started = performance.now();
    for (let i = 0; i < frames; i++) {
      if (cancelExport) throw 'cancel'; if (encErr) throw encErr;
      renderFrame(i / FPS);
      const vf = new VideoFrame(view, { timestamp: Math.round(i * 1e6 / FPS), duration: Math.round(1e6 / FPS) });
      venc.encode(vf, { keyFrame: i % (FPS * 2) === 0 }); vf.close();
      while (venc.encodeQueueSize > 6) await sleep(4);
      if (i % 5 === 0) { const k = (i + 1) / frames, el = (performance.now() - started) / 1000, left = el / k - el; $('dlgBar').style.width = (k * 100).toFixed(1) + '%'; $('dlgStat').textContent = `${i + 1} / ${frames} 장 · 남은 시간 약 ${left < 60 ? Math.ceil(left) + '초' : Math.ceil(left / 60) + '분'}`; await sleep(0); }
    }
    await venc.flush(); venc.close(); muxer.finalize();
    exported = new Blob([target.buffer], { type: 'video/mp4' }); $('dlgBar').style.width = '100%';
    dlg('MP4를 만들었어요', `${(exported.size / 1048576).toFixed(1)} MB · 1920×1080 · ${FPS}fps · ${LEN.toFixed(1)}초${acfg ? '' : ' · 소리 없음'}${vcfg.mux === 'vp9' ? ' · VP9 코덱 (맥 QuickTime 에서는 안 열릴 수 있어요)' : ''}`);
    $('dlgSave').hidden = false; $('dlgCancel').textContent = '닫기'; $('dlgStat').textContent = '';
  } catch (e) {
    if (e === 'cancel') $('dlg').close();
    else { dlg('MP4를 만들지 못했어요', (e && e.message) || String(e)); $('dlgStat').textContent = '작업 파일을 저장해 저장소에서 렌더링할 수 있어요.'; $('dlgCancel').textContent = '닫기'; }
  } finally { exporting = false; show(keepT); }
}
$('export').onclick = exportMp4;
$('dlgCancel').onclick = () => { if (exporting) cancelExport = true; else $('dlg').close(); };
$('dlg').addEventListener('cancel', e => { if (exporting) { e.preventDefault(); cancelExport = true; } });
$('dlgSave').onclick = async () => { try { await saveFile('jei_video_edit.mp4', exported); $('dlgStat').textContent = '저장을 시작했어요.'; } catch (e) { $('dlgStat').textContent = saveMsg(e); } };

// ---------- 시작 ----------
function busy(msg) { $('busy').hidden = !msg; if (msg) $('busy').textContent = msg; }
function setControls(on) { ['newBtn', 'load', 'saveJson', 'export', 'play'].forEach(id => { $(id).disabled = !on; }); $('undo').disabled = !on || !undoStack.length; }
function wavBase64() {   // 저장소 렌더링용: 섞은 소리를 16비트 WAV 로
  const b = buildMix(), n = b.length, sr = b.sampleRate, L = b.getChannelData(0), R = b.getChannelData(1), buf = new ArrayBuffer(44 + n * 4), dv = new DataView(buf);
  const w = (o, s) => [...s].forEach((c, i) => dv.setUint8(o + i, c.charCodeAt(0)));
  w(0, 'RIFF'); dv.setUint32(4, 36 + n * 4, true); w(8, 'WAVEfmt '); dv.setUint32(16, 16, true); dv.setUint16(20, 1, true); dv.setUint16(22, 2, true); dv.setUint32(24, sr, true); dv.setUint32(28, sr * 4, true); dv.setUint16(32, 4, true); dv.setUint16(34, 16, true); w(36, 'data'); dv.setUint32(40, n * 4, true);
  for (let i = 0; i < n; i++) { dv.setInt16(44 + i * 4, clamp(L[i], -1, 1) * 32767, true); dv.setInt16(46 + i * 4, clamp(R[i], -1, 1) * 32767, true); }
  let s = ''; const u = new Uint8Array(buf); for (let i = 0; i < u.length; i += 32768) s += String.fromCharCode.apply(null, u.subarray(i, i + 32768)); return btoa(s);
}
window.addEventListener('error', e => { if (!$('busy').hidden) $('busy').textContent = '편집기에 문제가 생겼어요: ' + (e.message || ''); });
window.addEventListener('unhandledrejection', e => { if (!$('busy').hidden) $('busy').textContent = '편집기에 문제가 생겼어요: ' + ((e.reason && e.reason.message) || e.reason || ''); });
window.EDITOR = {
  get project() { return project; }, get total() { return TOTAL; }, get ready() { return !!project && $('busy').hidden; }, get sel() { return sel; },
  seek, selectClip, loadProject: async j => { await loadProjectJSON(j); }, fps: FPS,
  frame: t => { peek = null; renderFrame(t); return view.toDataURL('image/png'); }, wavBase64,
};
(async () => {
  setControls(false);
  step('글꼴을 받는 중…');
  for (const [fam, file] of [['Noto Sans KR', 'NotoSansKR.ttf'], ['Inter', 'Inter.ttf']]) {   // 편집기 글자·새 장면용 글꼴 (저장소와 게시본의 위치가 달라 차례로 시도)
    for (const dir of ['fonts/', 'ai-math-trailer/fonts/']) { try { const ff = new FontFace(fam, await fontBuf(new URL(dir + file, location.href).href), { weight: '100 900' }); document.fonts.add(await ff.load()); break; } catch (e) { delete fontCache[new URL(dir + file, location.href).href]; } }
  }
  if (RENDER_MODE) { busy(''); return; }   // 저장소 렌더링: loadProject 를 기다림
  let p = null; try { p = JSON.parse(localStorage.getItem(STORE) || 'null'); } catch (e) {}
  const want = location.hash.slice(1);
  try {
    if (p && p.version === 2 && p.clips && p.clips.length && !TITLE_OF[want]) await setProject(p, '이 브라우저에 저장된 편집본을 열었어요');
    else await setProject(await projectFromVideo(TITLE_OF[want] ? want : window.VIDEOS[0].id), '기본 편집본');
  } catch (e) { busy('편집기를 열지 못했어요. ' + (e.message || '')); }
})();
})();
