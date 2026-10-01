// 영상 편집기(../video-editor.html)에 보여 줄 칸 설명. 규칙: ../editor/PROTOCOL.md
// 영상은 120BPM 격자(초)로 짜고 곡의 박 길이에 맞게 늘이므로(song.js) 여기 시각도 같은 비율로 바꿔서 씀
(() => {
const SONG = window.SONG || { beat: .5 }, TK = SONG.beat / .5;
const g = x => +(x * TK).toFixed(3);                       // 격자 시각 → 실제 시각(초)
const DISP = "'Black Han Sans'", KR = "'Noto Sans KR'", EN = "'Inter'";
const txt = (path, label, at, fit) => ({ path, label, type: 'text', ...(at != null ? { at: g(at) } : {}), ...(fit ? { fit } : {}) });
const col = (path, label, desc, at) => ({ path, label, desc, type: 'color', at: g(at) });
window.SCHEMA = {
 id: 'jei-promo-celebration',
 title: '재능교육 홍보 · CELEBRATION',
 duration: 34 * TK, fps: 30,
 audio: ['audio/mix.wav', 'audio/mix.mp3'],
 audioFade: { in: 0.3, out: 2 },
 scenes: [
  { start: 0, end: g(2), label: '드롭 전 · AI 시대에도', dark: true },
  { start: g(2), end: g(6), label: '드롭 · 결국, 스스로.' },
  { start: g(6), end: g(10), label: '교육 50년' },
  { start: g(10), end: g(16), label: '스스로학습시스템', dark: true },
  { start: g(16), end: g(22), label: '수상' },
  { start: g(22), end: g(27), label: '세계로', dark: true },
  { start: g(27), end: g(34), label: '엔딩' },
 ],
 sounds: [
  { t: g(2), label: '곡 드롭', big: true },
  { t: g(2.5), label: '스스로. 착지' },
  ...[5.5, 9.5, 15.5, 21.5, 26.5].map(s => ({ t: g(s), label: '장면 전환' })),
  { t: g(9.75), label: '연도 쾅' },
  ...[10.5, 11.5, 12.5].map(s => ({ t: g(s), label: '줄 착지' })),
  { t: g(17.25), label: '18 쾅', big: true }, { t: g(19.25), label: '13 쾅', big: true },
  ...[0, 1, 2, 3, 4, 5].map(i => ({ t: g(23.25 + i * .5), label: '나라' })),
  { t: g(27.5), label: '재능교육', big: true }, { t: g(31), label: '색종이' },
 ],
 tabs: [{ id: 'text', label: '문구' }, { id: 'color', label: '색' }],
 groups: [
  { tab: 'text', title: '첫 장면 · 드롭', at: g(4), note: '첫 줄은 드롭 전 4박 동안 한 글자씩 나와요. 글자 수가 많으면 박이 모자라요.', fields: [
   txt('hook.line1', '드롭 전 문구', 1.6, { size: 210, family: DISP, max: 1800 }),
   txt('hook.line2', '드롭 윗줄', 4),
   txt('hook.accent', '드롭 큰 글자', 4, { size: 330, family: DISP, max: 1800 }),
   txt('tickers.drop', '드롭 장면의 흐르는 띠', 4)] },
  { tab: 'text', title: '교육 50년', at: g(9.5), fields: [
   txt('history.label', '위쪽 스티커'),
   { path: 'history.yearFrom', label: '시작 연도', type: 'number', min: 0, max: 9999, step: 1, at: g(6.3) },
   { path: 'history.yearTo', label: '끝 연도', type: 'number', min: 0, max: 9999, step: 1 },
   txt('history.title1', '아래 첫 부분 (검은 글자)'),
   txt('history.title2', '아래 뒷부분 (빨간 글자)'),
   txt('history.sub', '노란 스티커', null, { size: 40, family: DISP, max: 1600 })] },
  { tab: 'text', title: '스스로학습시스템', at: g(15), note: '세 줄은 마디마다 하나씩 나와요. 뒷말이 길면 오른쪽 계단과 겹쳐요.', fields: [
   txt('system.label', '위쪽 스티커'),
   ...[0, 1, 2].flatMap(i => [
    txt(`system.rows.${i}.a`, `${i + 1}번째 줄 앞말`),
    txt(`system.rows.${i}.b`, `${i + 1}번째 줄 뒷말 (노란 형광펜)`, null, { size: 140, family: DISP, max: 620 })]),
   txt('system.sub', '아래 스티커', null, { size: 40, family: DISP, max: 1100 })] },
  { tab: 'text', title: '수상', at: g(21), fields: [txt('awards.label', '위쪽 스티커')] },
  ...[0, 1].map(i => ({ tab: 'text', title: `수상 ${i + 1} (${i ? '오른쪽' : '왼쪽'})`, at: g(21), fields: [
   { path: `awards.items.${i}.n`, label: '숫자', type: 'number', min: 0, max: 99, step: 1, desc: '16분음표마다 올라가다 마디 첫 박에 멈춰요' },
   txt(`awards.items.${i}.unit`, '숫자 옆 노란 스티커'),
   txt(`awards.items.${i}.title`, '상 이름', null, { size: 46, weight: 800, family: KR, max: 760 }),
   txt(`awards.items.${i}.brand`, '받은 브랜드 (검은 스티커)', null, { size: 38, family: DISP, max: 700 }),
   txt(`awards.items.${i}.org`, '주최', null, { size: 26, weight: 500, family: KR, max: 760 })] })),
  { tab: 'text', title: '세계로', at: g(26.4), fields: [
   txt('global.label', '위쪽 스티커'),
   txt('global.lead', '첫 줄', null, { size: 54, weight: 700, family: KR, max: 1600 }),
   txt('global.title', '큰 제목', null, { size: 130, family: DISP, max: 1600 }),
   txt('global.sub', '아래 설명', null, { size: 38, weight: 500, family: KR, max: 1600 })] },
  { tab: 'text', title: '나라 이름 (6개)', at: g(26.4), columns: 2, note: '나라는 박마다 하나씩 나와서 개수는 바꿀 수 없어요. 모두 합쳐 너무 길면 오른쪽으로 넘쳐요.',
   fields: [0, 1, 2, 3, 4, 5].map(i => txt(`global.countries.${i}`, `${i + 1}번째`)) },
  { tab: 'text', title: '엔딩', at: g(31.5), fields: [
   txt('ending.brand', '회사 이름', null, { size: 270, family: DISP, max: 1700 }),
   txt('ending.slogan1', '슬로건 앞부분'),
   txt('ending.slogan2', '슬로건 빨간 글자'),
   txt('ending.url', '홈페이지 주소'),
   txt('tickers.end', '아래 흐르는 띠')] },
  { tab: 'text', title: '화면 위 고정 표기', at: g(12), fields: [txt('hud.brand', '왼쪽 위'), txt('hud.since', '오른쪽 위')] },
  { tab: 'color', title: '브랜드', fields: [
   col('colors.red', '재능 레드', '드롭·수상 배경, 빨간 글자', 4),
   col('colors.yellow', '포인트 노랑', '형광펜, 스티커, 띠', 14)] },
  { tab: 'color', title: '배경·글자', fields: [
   col('colors.black', '검정', '드롭 전·스스로·세계로 배경', 14),
   col('colors.paper', '밝은 배경', '교육 50년·엔딩 배경', 9.5),
   col('colors.white', '흰색', '어두운 장면의 글자', 14),
   col('colors.ink', '진한 글자', '밝은 장면의 글자', 31.5)]},
 ],
 locked: '장면 순서와 길이, 글자가 나오는 박자, 움직임, 음악은 고칠 수 없어요. 곡의 드롭과 박자에 맞춰 짜여 있어서예요.',
 warnings: ['배경음(CELEBRATION)은 사내용이에요. 외부 공개용은 라이선스 음원으로 바꿔야 해요.'],
};
})();
