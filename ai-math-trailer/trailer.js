// ------------------------------------------------------------
// 재능스스로AI수학 12월 리뉴얼 — 영화 예고편 스타일 (45초)
// 이야기: 하루의 학습 → 별 하나 → 별자리 보상 → 새로워진 UI/UX → 타이틀 → 2026년 12월
// 3D(별·별자리·떠 있는 앱 화면)는 three.js, 글자·레터박스·플레어·필름 입자는 2D 로 얹음
// 컷 시각은 timeline.js (음악 tools/make_audio.py 도 같은 파일을 읽음), 문구·색은 content.js
// index.html(재생·렌더)과 editor.html(편집기)이 이 파일을 같이 씀. 페이지에 <canvas id="c"> 가 있어야 함
// ------------------------------------------------------------
const W = 1920, H = 1080, TL = window.TL, DURATION = TL.duration;
const out = document.getElementById('c'), ctx = out.getContext('2d');
const KR = "'Noto Sans KR', sans-serif", EN = "'Inter', 'Noto Sans KR', sans-serif";
const DEFAULT_CONTENT = JSON.parse(JSON.stringify(window.CONTENT));   // 편집 전 기본값 (content.js)
let C = window.CONTENT;                                               // 지금 쓰는 문구·색 (editor 가 apply() 로 바꿈)
function rgba(hex, a) { const n = parseInt(hex.slice(1), 16); return `rgba(${n >> 16 & 255},${n >> 8 & 255},${n & 255},${a})`; }
// 별빛·플레어·글자색은 content.js 의 colors 에서 옴 (채도 낮은 샴페인 화이트 기본)
let GOLD, ICE, RED, ACC, DIM, APP_GOLD;
function readColors() { const k = C.colors; GOLD = k.star; ICE = k.flare; RED = k.brand; ACC = rgba(k.accent, .92); DIM = rgba(k.dim, .55); APP_GOLD = k.app; }
readColors();
const BAR = 138;                                     // 2.39:1 시네마스코프 레터박스

const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, k) => a + (b - a) * k;
const p = (t, s, d) => clamp((t - s) / d);
const eOut = x => 1 - Math.pow(1 - x, 3);
const eIn = x => x * x * x;
const eIO = x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
const env = (t, s, e, fi = .8, fo = .8) => Math.min(eOut(p(t, s, fi)), 1 - eIn(p(t, e - fo, fo)));
function rng(seed) { return () => (seed = (seed * 16807) % 2147483647) / 2147483647; }
const D2R = Math.PI / 180;
function sky(raH, decD, r = 1) { const ra = raH * 15 * D2R, dec = decD * D2R; return new THREE.Vector3(Math.cos(dec) * Math.cos(ra) * r, Math.sin(dec) * r, -Math.cos(dec) * Math.sin(ra) * r); }

// ---------- three.js ----------
const glCanvas = document.createElement('canvas'); glCanvas.width = W; glCanvas.height = H;
const renderer = new THREE.WebGLRenderer({ canvas: glCanvas, antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H, false); renderer.outputColorSpace = THREE.SRGBColorSpace;
const scene = new THREE.Scene(); scene.background = new THREE.Color('#02030A');
const camera = new THREE.PerspectiveCamera(40, W / H, .01, 200);

function glowTex() {
  const c = document.createElement('canvas'); c.width = c.height = 128; const g = c.getContext('2d');
  const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(.12, 'rgba(255,255,255,.85)'); gr.addColorStop(.32, 'rgba(255,255,255,.22)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = gr; g.fillRect(0, 0, 128, 128); return new THREE.CanvasTexture(c);
}
const GLOW = glowTex();
const starMat = () => new THREE.ShaderMaterial({
  uniforms: { uTime: { value: 0 }, uTex: { value: GLOW }, uScale: { value: 1 }, uAlpha: { value: 1 } },
  vertexShader: `attribute float size; attribute vec3 color; attribute float phase; varying vec3 vC; varying float vT; uniform float uTime, uScale;
    void main() { vC = color; vT = .75 + .25 * sin(uTime * (1.2 + phase * 2.) + phase * 30.); vec4 mv = modelViewMatrix * vec4(position, 1.); gl_PointSize = size * uScale; gl_Position = projectionMatrix * mv; }`,
  fragmentShader: `uniform sampler2D uTex; uniform float uAlpha; varying vec3 vC; varying float vT; void main() { vec4 t = texture2D(uTex, gl_PointCoord); gl_FragColor = vec4(vC * t.rgb, t.a * vT * uAlpha); }`,
  transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
});
const R = 50, rr = rng(12);
{ // 배경 별 + 은하수 느낌의 띠
  const n = 14000, pos = new Float32Array(n * 3), col = new Float32Array(n * 3), size = new Float32Array(n), ph = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    let v;
    if (i < 9000) { const u = rr() * 2 - 1, th = rr() * Math.PI * 2, s = Math.sqrt(1 - u * u); v = new THREE.Vector3(s * Math.cos(th), u, s * Math.sin(th)); }
    else { const a = rr() * Math.PI * 2, b = (rr() + rr() + rr() - 1.5) * .18; v = new THREE.Vector3(Math.cos(a), b + Math.sin(a) * .35, Math.sin(a)).normalize(); }
    v.multiplyScalar(R); pos.set([v.x, v.y, v.z], i * 3);
    const c = new THREE.Color().setHSL(rr() < .25 ? .08 : .62 + rr() * .06, .45, .75 + rr() * .2); col.set([c.r, c.g, c.b], i * 3);
    size[i] = 2 + Math.pow(rr(), 6) * 14; ph[i] = rr();
  }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('color', new THREE.BufferAttribute(col, 3));
  g.setAttribute('size', new THREE.BufferAttribute(size, 1)); g.setAttribute('phase', new THREE.BufferAttribute(ph, 1));
  var bgStars = new THREE.Points(g, starMat()); scene.add(bgStars);
}
// 성운 빛 번짐
const neb = new THREE.Group(); scene.add(neb);
for (let i = 0; i < 90; i++) {
  const a = rr() * Math.PI * 2, b = (rr() - .5) * .5, v = new THREE.Vector3(Math.cos(a), b + Math.sin(a) * .35, Math.sin(a)).normalize().multiplyScalar(R * .95);
  const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: GLOW, color: new THREE.Color().setHSL(rr() < .5 ? .7 : .58, .7, .5), transparent: true, opacity: .07 + rr() * .08, blending: THREE.AdditiveBlending, depthWrite: false }));
  sp.position.copy(v); const s = 8 + rr() * 14; sp.scale.set(s, s, 1); neb.add(sp);
}
// 학습 별 7개 (북두칠성 모양) — 하루 학습마다 하나씩 켜짐
const DIPPER = [[11.062, 61.75], [11.031, 56.38], [11.897, 53.69], [12.257, 57.03], [12.900, 55.96], [13.399, 54.93], [13.792, 49.31]];
const LINES = [[0, 1], [1, 2], [2, 3], [3, 0], [3, 4], [4, 5], [5, 6]];
const lessonV = DIPPER.map(([ra, dec]) => sky(ra, dec, R * .9));
const lessonStars = lessonV.map(v => {
  const core = new THREE.Sprite(new THREE.SpriteMaterial({ map: GLOW, color: '#FFF4D8', transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false }));
  const halo = new THREE.Sprite(new THREE.SpriteMaterial({ map: GLOW, color: GOLD, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false }));
  core.position.copy(v); halo.position.copy(v); scene.add(core, halo); return { core, halo };
});
const lineObjs = LINES.map(([a, b]) => {
  const g = new THREE.BufferGeometry().setFromPoints([lessonV[a], lessonV[a]]);
  const l = new THREE.Line(g, new THREE.LineBasicMaterial({ color: GOLD, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false }));
  scene.add(l); return { l, a: lessonV[a], b: lessonV[b] };
});
const dipperC = lessonV.reduce((s, v) => s.add(v), new THREE.Vector3()).multiplyScalar(1 / 7);

// ---------- 새 앱 화면 (목업) : 캔버스로 그려 3D 판에 붙임 ----------
// 앱 목업 안의 강조색 APP_GOLD 는 colors.app (앱 디자인 요소)
const UIW = 1600, UIH = 1000;
function uiCanvas(draw) { const c = document.createElement('canvas'); c.width = UIW; c.height = UIH; const g = c.getContext('2d'); draw(g); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; t.userData = { g, draw }; return t; }
function gRect(g, x, y, w, h, r, f, s, lw = 3) { g.beginPath(); g.roundRect(x, y, w, h, r); if (f) { g.fillStyle = f; g.fill(); } if (s) { g.strokeStyle = s; g.lineWidth = lw; g.stroke(); } }
function gText(g, s, x, y, size, col, w = 700, al = 'left', fam = KR) { g.font = `${w} ${size}px ${fam}`; g.fillStyle = col; g.textAlign = al; g.textBaseline = 'middle'; g.fillText(s, x, y); }
function gStar(g, x, y, r, col) { g.beginPath(); for (let i = 0; i < 10; i++) { const a = i / 10 * Math.PI * 2 - Math.PI / 2, rr = i % 2 ? r * .45 : r; g.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr); } g.closePath(); g.fillStyle = col; g.fill(); }
function uiFrame(g, title) {
  const bgG = g.createLinearGradient(0, 0, UIW, UIH); bgG.addColorStop(0, '#171B45'); bgG.addColorStop(1, '#0C0F2A'); gRect(g, 0, 0, UIW, UIH, 60, bgG);
  const r = rng(title.length * 7); for (let i = 0; i < 70; i++) { g.globalAlpha = .3 + r() * .5; g.fillStyle = '#fff'; g.beginPath(); g.arc(r() * UIW, r() * UIH, r() * 2.2, 0, Math.PI * 2); g.fill(); } g.globalAlpha = 1;
  gText(g, C.app.name, 70, 70, 34, '#fff', 800); gRect(g, 1240, 40, 290, 60, 30, rgba(APP_GOLD, .15), APP_GOLD, 2); gStar(g, 1280, 70, 17, APP_GOLD); gText(g, C.app.stars, 1310, 71, 32, APP_GOLD, 800, 'left', EN);
  gText(g, title, 70, 150, 28, 'rgba(210,220,255,.7)', 500);
}
const UI = [
  uiCanvas(g => { // 홈
    uiFrame(g, '홈');
    gText(g, C.app.homeGreeting, 70, 240, 64, '#fff', 800);
    gRect(g, 70, 310, 700, 560, 44, 'rgba(255,255,255,.07)', 'rgba(255,255,255,.14)');
    gText(g, '오늘의 학습', 120, 380, 34, 'rgba(255,255,255,.8)', 600);
    g.lineWidth = 34; g.lineCap = 'round'; g.strokeStyle = 'rgba(255,255,255,.1)'; g.beginPath(); g.arc(420, 620, 160, 0, Math.PI * 2); g.stroke();
    g.strokeStyle = APP_GOLD; g.beginPath(); g.arc(420, 620, 160, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * .6); g.stroke();
    gText(g, C.app.homeProgress, 420, 610, 76, '#fff', 800, 'center', EN); gText(g, '단계 완료', 420, 680, 30, 'rgba(255,255,255,.6)', 500, 'center');
    ['#5EE0B5', '#FF8FB1', '#7CA8FF'].map((c, i) => [C.app.lessons[i] || '', c]).forEach(([s, c], i) => {
      gRect(g, 830, 310 + i * 190, 700, 160, 36, 'rgba(255,255,255,.07)', 'rgba(255,255,255,.14)');
      gRect(g, 870, 350 + i * 190, 80, 80, 24, c); gText(g, s, 990, 390 + i * 190, 42, '#fff', 700); gText(g, i < 2 ? '완료' : '시작하기 →', 1480, 390 + i * 190, 30, i < 2 ? c : APP_GOLD, 700, 'right');
    });
  }),
  uiCanvas(g => { // 문제 + AI 힌트
    uiFrame(g, '문제 풀기');
    gRect(g, 70, 200, 900, 690, 44, 'rgba(255,255,255,.07)', 'rgba(255,255,255,.14)');
    gText(g, C.app.problem, 520, 430, 150, '#fff', 800, 'center', EN);
    [0, 1].forEach(i => gRect(g, 380 + i * 150, 560, 120, 150, 26, 'rgba(255,255,255,.1)', i ? APP_GOLD : 'rgba(255,255,255,.3)', 4));
    gText(g, '4', 440, 636, 90, '#fff', 800, 'center', EN);
    for (let i = 0; i < 10; i++) { const x = 1030 + (i % 3) * 170, y = 230 + Math.floor(i / 3) * 150; if (i === 9) { gRect(g, 1200, y, 150, 120, 30, 'rgba(255,255,255,.1)'); gText(g, '0', 1275, y + 60, 56, '#fff', 700, 'center', EN); } else { gRect(g, x, y, 150, 120, 30, 'rgba(255,255,255,.1)'); gText(g, String(i + 1), x + 75, y + 60, 56, '#fff', 700, 'center', EN); } }
    gRect(g, 120, 760, 800, 100, 50, 'rgba(124,168,255,.22)', '#7CA8FF', 3); gStar(g, 175, 810, 24, APP_GOLD);
    gText(g, C.app.hint, 215, 811, 32, '#fff', 600);
  }),
  uiCanvas(g => { // 별자리 도감
    uiFrame(g, '별자리 도감');
    gText(g, C.app.dexTitle, 70, 240, 60, '#fff', 800);
    const names = [...C.app.dexNames.slice(0, 4), '???', '???', '???', '???'];
    const shapes = [[[.1, .3], [.3, .25], [.45, .4], [.35, .55], [.6, .6], [.78, .65], [.92, .8]], [[.1, .4], [.3, .7], [.5, .45], [.7, .7], [.9, .35]], [[.3, .15], [.7, .2], [.45, .5], [.55, .5], [.3, .85], [.72, .8]], [[.5, .1], [.5, .9], [.15, .45], [.85, .45], [.5, .45]]];
    names.forEach((s, i) => {
      const x = 70 + (i % 4) * 370, y = 300 + Math.floor(i / 4) * 320, lit = i < 4;
      gRect(g, x, y, 340, 290, 36, lit ? rgba(APP_GOLD, .1) : 'rgba(255,255,255,.04)', lit ? rgba(APP_GOLD, .6) : 'rgba(255,255,255,.1)', 3);
      if (lit) { const pts = shapes[i].map(([u, v]) => [x + 40 + u * 260, y + 30 + v * 170]); g.strokeStyle = rgba(APP_GOLD, .7); g.lineWidth = 3; g.beginPath(); pts.forEach(([a, b], k) => k ? g.lineTo(a, b) : g.moveTo(a, b)); g.stroke(); pts.forEach(([a, b]) => gStar(g, a, b, 11, '#FFF3CF')); }
      else gText(g, '?', x + 170, y + 120, 90, 'rgba(255,255,255,.18)', 800, 'center', EN);
      gText(g, s, x + 170, y + 250, 34, lit ? '#fff' : 'rgba(255,255,255,.35)', 700, 'center');
    });
  }),
  uiCanvas(g => { // 성장 리포트
    uiFrame(g, '나의 성장');
    gText(g, C.app.growthTitle, 70, 240, 60, '#fff', 800);
    gRect(g, 70, 300, 1460, 580, 44, 'rgba(255,255,255,.07)', 'rgba(255,255,255,.14)');
    const days = ['월', '화', '수', '목', '금', '토', '일'], v = [.45, .6, .55, .75, .7, .9, .82];
    days.forEach((d, i) => { const x = 180 + i * 190, h = v[i] * 380; const gr = g.createLinearGradient(0, 800 - h, 0, 800); gr.addColorStop(0, APP_GOLD); gr.addColorStop(1, '#FF8FB1'); gRect(g, x, 800 - h, 110, h, 24, gr); gText(g, d, x + 55, 845, 32, 'rgba(255,255,255,.7)', 600, 'center'); });
    gText(g, '예시 화면', 1480, 350, 24, 'rgba(255,255,255,.4)', 500, 'right');
  }),
];
// 앱 화면 판 4장 — 별이 가득한 공간에 떠 있음
const UI_DIRS = [sky(3.0, 12), sky(7.5, -8), sky(16.0, 20), sky(21.0, -15)];
const panels = UI.map((tex, i) => {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(1.6, 1.0), new THREE.MeshBasicMaterial({ map: tex, transparent: true, opacity: 1, side: THREE.DoubleSide }));
  const glow = new THREE.Mesh(new THREE.PlaneGeometry(2.1, 1.5), new THREE.MeshBasicMaterial({ map: GLOW, color: i % 2 ? '#7CA8FF' : GOLD, transparent: true, opacity: .35, blending: THREE.AdditiveBlending, depthWrite: false }));
  const g = new THREE.Group(); g.add(glow, m); glow.position.z = -.02;
  g.position.copy(UI_DIRS[i]).multiplyScalar(4); g.lookAt(0, 0, 0); scene.add(g); return g;
});

// ---------- 카메라 샷 ----------
function lookFrom(pos, target, roll = 0, fov = 40) { camera.position.copy(pos); camera.up.set(0, 1, 0); camera.lookAt(target); camera.rotateZ(roll); camera.fov = fov; camera.updateProjectionMatrix(); }
function shot(t) {
  const O = new THREE.Vector3();
  if (t < 17) {                                          // 별 → 별자리
    const k = clamp((t - 4.5) / 12.5);
    const dir = dipperC.clone().normalize(), side = new THREE.Vector3().crossVectors(dir, new THREE.Vector3(0, 1, 0)).normalize();
    const pos = side.clone().multiplyScalar(Math.sin(k * 1.2) * 2.5).add(dir.clone().multiplyScalar(lerp(-2, 6, eIO(k))));
    lookFrom(pos, dipperC, Math.sin(k * 2) * .03, lerp(46, 30, eIO(k)));
  } else if (t < 28) {                                   // 앱 화면 4장
    const i = clamp(Math.floor((t - TL.ui[0]) / 2.2 + 1e-6), 0, 3), s = TL.ui[i], k = clamp((t - s) / 2.2);
    const d = UI_DIRS[i].clone(), side = new THREE.Vector3().crossVectors(d, new THREE.Vector3(0, 1, 0)).normalize();
    const pos = d.clone().multiplyScalar(lerp(.6, 2.0, eOut(k))).add(side.clone().multiplyScalar(lerp(.9, -.5, eIO(k)))).add(new THREE.Vector3(0, lerp(.25, -.1, k), 0));
    lookFrom(pos, d.clone().multiplyScalar(4), lerp(.06, -.03, k) * (i % 2 ? -1 : 1), 42);
  } else if (t < 33) {                                   // 몽타주: 빠르게 교차
    const idx = TL.montage.filter(m => t >= m).length, i = idx % 5;
    if (i < 4) { const d = UI_DIRS[i]; lookFrom(d.clone().multiplyScalar(2.3 + (idx % 3) * .2), d.clone().multiplyScalar(4), (idx % 2 ? .08 : -.08), 36 + (idx % 3) * 6); }
    else lookFrom(O, dipperC, 0, 28);
  } else {                                               // 타이틀: 별 사이로 뒤로 빠짐
    const k = clamp((t - 33) / 12);
    const dir = dipperC.clone().normalize();
    lookFrom(dir.clone().multiplyScalar(lerp(4, -14, eOut(k))), dipperC, .02, lerp(34, 60, eOut(k)));
  }
}

// ---------- 2D 글자·효과 ----------
function text(str, x, y, { size = 60, color = '#fff', weight = 200, family = KR, align = 'center', alpha = 1, spacing = 0, glow = 0, scale = 1 } = {}) {
  if (alpha <= 0) return; ctx.save(); ctx.globalAlpha = alpha; ctx.translate(x, y); ctx.scale(scale, scale);
  ctx.font = `${weight} ${size}px ${family}`; ctx.fillStyle = color; ctx.textAlign = align; ctx.textBaseline = 'middle'; ctx.letterSpacing = spacing + 'px';
  if (glow) { ctx.shadowColor = color; ctx.shadowBlur = glow; } ctx.fillText(str, 0, 0); ctx.restore();
}
function measureT(str, size, weight = 200, family = KR) { ctx.save(); ctx.font = `${weight} ${size}px ${family}`; const w = ctx.measureText(str).width; ctx.restore(); return w; }
function card(str, t, s, e, o = {}) { const a = env(t, s, e, o.fi || .7, o.fo || .6); text(str, W / 2, o.y || H / 2, { size: 64, weight: 200, spacing: 14, ...o, alpha: a, scale: 1 + (t - s) * .012 }); }
function flare(x, y, k, col = ICE, size = 1) {
  if (k <= 0) return; ctx.save(); ctx.globalCompositeOperation = 'lighter';
  const g = ctx.createRadialGradient(x, y, 0, x, y, 260 * size); g.addColorStop(0, `rgba(255,255,255,${.9 * k})`); g.addColorStop(.1, `rgba(255,236,200,${.5 * k})`); g.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = g; ctx.fillRect(x - 300 * size, y - 300 * size, 600 * size, 600 * size);
  const s = ctx.createLinearGradient(x - 900 * size, 0, x + 900 * size, 0); s.addColorStop(0, 'rgba(120,170,255,0)'); s.addColorStop(.5, `rgba(150,190,255,${.55 * k})`); s.addColorStop(1, 'rgba(120,170,255,0)');
  ctx.fillStyle = s; ctx.fillRect(x - 900 * size, y - 3 * size, 1800 * size, 6 * size);
  [.35, .6, 1.3].forEach((d, i) => { const gx = lerp(x, W / 2, d * 2), gy = lerp(y, H / 2, d * 2); ctx.beginPath(); ctx.arc(gx, gy, (20 + i * 26) * size, 0, Math.PI * 2); ctx.fillStyle = `rgba(${i ? 140 : 255},${170},255,${.08 * k})`; ctx.fill(); });
  ctx.restore();
}
function project(v) { const q = v.clone().project(camera); return { x: (q.x + 1) / 2 * W, y: (1 - q.y) / 2 * H, ok: q.z < 1 && Math.abs(q.x) < 1.2 && Math.abs(q.y) < 1.2 }; }
function lessonCard(t, s, i) {                         // 별이 켜질 때 별 옆에 가는 선과 DAY 표기
  const a = env(t, s + .05, s + 1.1, .25, .45); if (a <= 0) return;
  const q = project(lessonV[i]); if (!q.ok) return;
  const k = eOut(p(t, s + .05, .45)), dx = 70, dy = 70;
  ctx.save(); ctx.globalAlpha = a; ctx.strokeStyle = rgba(C.colors.accent, .6); ctx.lineWidth = 1.2;
  ctx.beginPath(); ctx.moveTo(q.x + 14, q.y + 12); ctx.lineTo(q.x + 14 + (dx - 14) * k, q.y + 12 + (dy - 12) * k); ctx.lineTo(q.x + dx + 90 * k, q.y + dy); ctx.stroke(); ctx.restore();
  text(`${C.lesson.day} ${String(i + 1).padStart(2, '0')}`, q.x + dx + 4, q.y + dy - 22, { size: 18, weight: 600, family: EN, align: 'left', spacing: 6, color: ACC, alpha: a * k });
  text(C.lesson.done, q.x + dx + 4, q.y + dy + 20, { size: 20, weight: 300, align: 'left', spacing: 4, color: DIM, alpha: a * k });
}
// ---------- 그리기 ----------
function draw(t) {
  shot(t);
  const tt = t;
  bgStars.material.uniforms.uTime.value = tt; bgStars.material.uniforms.uScale.value = 40 / camera.fov;
  bgStars.material.uniforms.uAlpha.value = t < 4.5 ? 0 : t < 17 ? eOut(p(t, 4.5, 2)) : t < 19 ? 0 : 1;
  neb.visible = t >= 4.5 && !(t >= 17 && t < 19);
  // 학습 별: 하나씩 켜짐
  lessonStars.forEach((s, i) => {
    const on = TL.ignite[i], k = p(t, on, .25), burstK = Math.exp(-Math.max(0, t - on) * 3);
    const visible = t >= 4.5 && !(t >= 17 && t < 19) && !(t >= 19 && t < 33 && !(t >= 28 && t < 33));
    const base = k > 0 ? 1 : .0;
    s.core.material.opacity = visible ? base * (.9 + burstK * .1) : 0;
    s.halo.material.opacity = visible ? base * (.35 + burstK * .9) : 0;
    const sz = (1.4 + burstK * 3.5) * (t > TL.reward ? 1.25 : 1);
    s.core.scale.set(sz * .5, sz * .5, 1); s.halo.scale.set(sz * 1.6, sz * 1.6, 1);
  });
  lineObjs.forEach((L, i) => {
    const per = (TL.connect[1] - TL.connect[0]) / LINES.length, k = eIO(p(t, TL.connect[0] + i * per, per * 1.3));
    L.l.geometry.setFromPoints([L.a, L.a.clone().lerp(L.b, Math.max(k, .0001))]);
    L.l.material.opacity = ((t >= 17 && t < 28) ? 0 : k > 0 ? .85 : 0) * (1 - eIn(p(t, 39.4, .6))) * (t >= TL.title ? .3 : 1);
  });
  panels.forEach((g, i) => { g.visible = t >= 19 && t < 33; g.children[0].material.opacity = .35; });
  renderer.render(scene, camera);

  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
  ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  // 컷 사이 암전 (예고편식 블랙)
  const black = (t < 4.5) || (t >= 17 && t < 19) || (t >= TL.silence[0] && t < TL.silence[1]);
  let flash = 0;
  if (t >= 28 && t < 32.6) { const idx = TL.montage.filter(m => t >= m).length; const last = TL.montage[idx - 1] || 28; flash = Math.exp(-(t - last) * 22); if ((t - last) > .12 && idx % 3 === 0) { /* 짧은 블랙 */ } }
  if (!black) {
    const fade = t < 17 ? eOut(p(t, 4.5, 1.2)) * (1 - eIn(p(t, 16.4, .6))) : t < 28 ? eOut(p(t, 19, .25)) : t < 33 ? 1 : eOut(p(t, 33, .15)) * (1 - eIn(p(t, 44, 1)));
    ctx.globalAlpha = fade; ctx.drawImage(glCanvas, 0, 0); ctx.globalAlpha = 1;
  }
  // 학습 별 플레어 + 알림 카드
  TL.ignite.forEach((s, i) => {
    if (t < 4.5 || t >= 17) return;
    const q = project(lessonV[i]); const k = Math.exp(-Math.max(0, t - s) * 2.2) * (t >= s ? 1 : 0);
    if (q.ok) flare(q.x, q.y, k, ICE, .8);
    lessonCard(t, s, i);
  });
  // 별자리 완성 플레어
  if (t >= TL.connect[1] && t < 17) { const q = project(dipperC); flare(q.x, q.y, Math.exp(-(t - TL.connect[1]) * 1.5) * .8, GOLD, 1.4); }

  // ---- 글자 ----
  C.cards.forEach(c => card(c.text, t, c.start, c.end, { y: c.y, size: c.size, weight: c.weight, spacing: c.spacing }));
  // 보상 표기: 양옆 가는 선 + 작은 영문 + 별자리 이름
  { const a = env(t, TL.reward, 16.5, .6, .6); if (a > 0) {
    const k = eOut(p(t, TL.reward, .9));
    ctx.save(); ctx.globalAlpha = a; ctx.strokeStyle = rgba(C.colors.accent, .5); ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(W / 2 - 180 - 160 * k, 812); ctx.lineTo(W / 2 - 180, 812); ctx.moveTo(W / 2 + 180, 812); ctx.lineTo(W / 2 + 180 + 160 * k, 812); ctx.stroke(); ctx.restore();
    text(C.reward.label, W / 2, 812, { size: 18, weight: 600, family: EN, spacing: 8, color: ACC, alpha: a });
    text(C.reward.name, W / 2, 862, { size: 36, weight: 300, spacing: 14, alpha: a }); } }
  const uiCopy = C.ui.map(u => u.copy), uiSub = C.ui.map(u => u.sub);
  TL.ui.forEach((s, i) => {
    const e = s + 2.15;
    text(uiSub[i], 160, 822, { size: 18, weight: 600, family: EN, align: 'left', spacing: 9, color: DIM, alpha: env(t, s + .15, e, .3, .3) });
    ctx.save(); ctx.globalAlpha = env(t, s + .15, e, .3, .3); ctx.fillStyle = rgba(C.colors.accent, .6); ctx.fillRect(160, 846, 36 * eOut(p(t, s + .15, .5)), 1.5); ctx.restore();
    text(uiCopy[i], 160, 892, { size: 56, weight: 300, align: 'left', spacing: 3, alpha: env(t, s + .25, e, .35, .3) });
  });
  // 몽타주 단어
  const words = C.montage.length ? C.montage : [''];
  if (t >= 28 && t < 32.6) {
    const idx = TL.montage.filter(m => t >= m).length - 1;
    if (idx >= 0 && idx % 2 === 1) { const wa = 1 - p(t, TL.montage[idx] + .15, .12); ctx.fillStyle = `rgba(0,0,6,${.7 * wa})`; ctx.fillRect(0, 0, W, H); }
    if (idx >= 0 && idx % 2 === 1) text(words[Math.floor(idx / 2) % words.length], W / 2, H / 2, { size: 150 - Math.min(40, idx * 3), weight: 900, spacing: 10, alpha: 1 - p(t, TL.montage[idx] + .15, .12) });
  }
  if (flash > 0) { ctx.fillStyle = `rgba(255,255,255,${flash * .3})`; ctx.fillRect(0, 0, W, H); }
  // 타이틀
  if (t >= TL.title) {
    const k = p(t, TL.title, 1.2), ft = 1 - eIn(p(t, 39.6, .5));
    if (t < 40) flare(W / 2, 470, Math.exp(-(t - TL.title) * 1.2) * .8, ICE, 1.8);
    ctx.save(); ctx.globalAlpha = ft;
    { const s1 = 140, w1 = measureT(C.title.light, s1, 200), w2 = measureT(C.title.bold, s1, 800), gap = C.title.light && C.title.bold ? 26 : 0, x0 = W / 2 - (w1 + gap + w2) / 2;
      text(C.title.light, x0, 480, { size: s1, weight: 200, align: 'left', spacing: 0, alpha: eOut(k) * ft, glow: 18 * (1 - k) });
      text(C.title.bold, x0 + w1 + gap, 480, { size: s1, weight: 800, align: 'left', spacing: 0, alpha: eOut(p(t, TL.title + .35, 1)) * ft, glow: 14 * (1 - p(t, TL.title + .35, 1)) }); }
    // 빛이 글자를 훑고 지나감
    const sx = lerp(-200, W + 200, eIO(p(t, TL.title + .6, 1.4)));
    ctx.globalCompositeOperation = 'lighter'; const sg = ctx.createLinearGradient(sx - 160, 0, sx + 160, 0); sg.addColorStop(0, 'rgba(255,255,255,0)'); sg.addColorStop(.5, 'rgba(255,255,255,.18)'); sg.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.globalAlpha = ft; ctx.fillStyle = sg; ctx.fillRect(sx - 160, 380, 320, 200); ctx.globalCompositeOperation = 'source-over';
    text(C.title.sub, W / 2, 606, { size: 22, weight: 500, family: EN, spacing: 22, color: DIM, alpha: eOut(p(t, TL.title + 1.4, .8)) * ft });
    ctx.restore();
  }
  // 개봉일
  if (t >= TL.date) {
    const a = 1 - eIn(p(t, 44, .9));
    text(C.date.main, W / 2, 470, { size: 170, weight: 100, family: EN, spacing: 24, alpha: eOut(p(t, TL.date, .9)) * a, glow: 20 });
    text(C.date.sub, W / 2, 640, { size: 44, weight: 300, spacing: 26, color: ACC, alpha: eOut(p(t, TL.sting, .6)) * a });
    ctx.save(); ctx.globalAlpha = eOut(p(t, 41.8, .6)) * a; const bw = measureT(C.date.brand, 30, 700), bx = W / 2 - (bw + 40) / 2;
    ctx.fillStyle = RED; ctx.fillRect(bx, 790, 22, 22); ctx.restore();
    text(C.date.brand, bx + 40, 802, { align: 'left', size: 30, weight: 700, alpha: eOut(p(t, 41.8, .6)) * a });
  }
  // 레터박스 + 비네트 + 필름 입자
  const vg = ctx.createRadialGradient(W / 2, H / 2, H * .35, W / 2, H / 2, H * .95); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,.55)'); ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
  const r = rng(1 + Math.floor(t * 24));
  for (let i = 0; i < 1600; i++) { ctx.fillStyle = r() < .5 ? 'rgba(255,255,255,.035)' : 'rgba(0,0,0,.07)'; ctx.fillRect(r() * W, r() * H, 1.6, 1.6); }
  ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, BAR); ctx.fillRect(0, H - BAR, W, BAR);
}

// 편집기에서 고친 내용 적용: { content } (content.js 와 같은 구조). 빠진 칸은 기본값으로 채움
function merge(base, over) {
  if (Array.isArray(base)) return Array.isArray(over) ? over.map((v, i) => base[i] !== undefined ? merge(base[i], v) : v) : base;
  if (base && typeof base === 'object') { const o = {}; for (const k in base) o[k] = over && k in over ? merge(base[k], over[k]) : base[k]; return o; }
  return over === undefined || over === null ? base : over;
}
function redrawUI() { UI.forEach(tx => { const { g, draw } = tx.userData; g.clearRect(0, 0, UIW, UIH); draw(g); tx.needsUpdate = true; }); }
function apply(project) {
  C = window.CONTENT = merge(DEFAULT_CONTENT, project && project.content);
  readColors();
  lessonStars.forEach(s => s.halo.material.color.set(GOLD)); lineObjs.forEach(L => L.l.material.color.set(GOLD));
  panels.forEach((g, i) => { if (!(i % 2)) g.children[0].material.color.set(GOLD); });
  redrawUI();
}

window.draw = draw;
window.DURATION = DURATION;
window.ready = Promise.all([document.fonts.load(`900 100px 'Noto Sans KR'`, '가'), document.fonts.load(`200 100px 'Noto Sans KR'`, '가'), document.fonts.load(`600 100px 'Inter'`, 'A')]).then(r => {
  if (r.some(fs => !fs.length)) throw new Error('폰트를 불러오지 못했습니다 (fonts/ 폴더 확인)');
}).then(() => document.fonts.ready).then(() => { redrawUI(); return true; });   // 폰트가 준비된 뒤 앱 화면 텍스처를 다시 그림
window.VIDEO = { schema: window.SCHEMA, defaults: DEFAULT_CONTENT, get content() { return C; }, apply(content) { apply({ content }); }, canvas: out };   // 영상 편집기 연결 (../editor/PROTOCOL.md)
window.Trailer = { draw, apply, get content() { return C; }, DEFAULT_CONTENT, TL, W, H, DURATION, canvas: out, ready: window.ready };
