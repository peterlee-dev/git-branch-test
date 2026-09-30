// 영상 편집기(../video-editor.html)에 보여 줄 칸 설명. 규칙: ../editor/PROTOCOL.md
// 소리 시각은 tools/make_audio.py 와 같음 (120BPM, 한 마디 = 2초)
(() => {
const KR = "'Noto Sans KR'", EN = "'Inter'";
const T = { hook: 1, history: 7, system: 12.5, awards: 18.5, global: 24, ending: 28.5 };   // 장면마다 글자가 다 보이는 시각
window.SCHEMA = {
 id: 'jei-promo-30s',
 title: '재능교육 홍보 30초',
 duration: 30, fps: 30,
 audio: ['audio/mix.wav', 'audio/mix.mp3'],
 audioFade: { in: 0.3, out: 2 },
 scenes: [
  { start: 0, end: 4, label: '훅 · AI 시대에도 결국, 스스로', dark: true },
  { start: 4, end: 8, label: '교육 50년' },
  { start: 8, end: 14, label: '스스로학습시스템' },
  { start: 14, end: 20, label: '수상', dark: true },
  { start: 20, end: 25, label: '세계로', dark: true },
  { start: 25, end: 30, label: '엔딩' },
 ],
 sounds: [
  { t: .3, label: '딸깍' }, { t: 1.1, label: '딸깍' }, { t: 1.9, label: '띵' },
  { t: 2, label: '상승음' },
  { t: 3.5, label: '슉 (전환)' },
  { t: 4, label: '비트 시작', big: true },
  { t: 4.3, label: '연도 카운터 딸깍' }, { t: 6.5, label: '띵' },
  { t: 7.5, label: '슉 (전환)' },
  { t: 8.5, label: '뿅' }, { t: 9.5, label: '뿅' }, { t: 10.5, label: '뿅' },
  { t: 13.5, label: '슉 (전환)' },
  { t: 14.5, label: '숫자 딸깍' }, { t: 15.6, label: '띵 · 숫자 딸깍' }, { t: 16.7, label: '띵' },
  { t: 19.5, label: '슉 (전환)' },
  ...[0, 1, 2, 3, 4, 5].map(i => ({ t: +(21.4 + i * .35).toFixed(2), label: '뿅' })),
  { t: 24.6, label: '슉 (전환)' },
  { t: 25, label: '엔딩 반짝', big: true },
  { t: 25.4, label: '띵' }, { t: 26.7, label: '띵' },
 ],
 tabs: [{ id: 'text', label: '문구' }, { id: 'color', label: '색' }],
 groups: [
  { tab: 'text', title: '첫 장면 (훅)', at: T.hook + 1.5, fields: [
   { path: 'hook.line1', label: '첫 줄', type: 'text', fit: { size: 150, weight: 900, family: KR, spacing: -4, max: 1600 } },
   { path: 'hook.line2', label: '둘째 줄 앞부분', type: 'text' },
   { path: 'hook.accent', label: '둘째 줄 빨간 글자', type: 'text' }] },
  { tab: 'text', title: '교육 50년', at: T.history, note: '연도 숫자는 딸깍 소리 12번에 맞춰 올라가요. 숫자를 바꿔도 소리 길이는 그대로예요.', fields: [
   { path: 'history.label', label: '위쪽 작은 영문', type: 'text' },
   { path: 'history.yearFrom', label: '시작 연도', type: 'number', min: 0, max: 9999, step: 1, at: 4.3 },
   { path: 'history.yearTo', label: '끝 연도', type: 'number', min: 0, max: 9999, step: 1 },
   { path: 'history.title1', label: '오른쪽 첫 줄 (흰 글자)', type: 'text', fit: { size: 96, weight: 900, family: KR, max: 600 } },
   { path: 'history.title2', label: '오른쪽 둘째 줄 (검은 글자)', type: 'text', fit: { size: 96, weight: 900, family: KR, max: 600 } },
   { path: 'history.sub', label: '오른쪽 설명', type: 'text', fit: { size: 34, weight: 500, family: KR, max: 600 } }] },
  { tab: 'text', title: '스스로학습시스템', at: T.system, note: '세 줄은 뿅 소리에 맞춰 한 줄씩 나와요. 앞말과 뒷말을 합쳐 너무 길면 오른쪽 막대와 겹쳐요.', fields: [
   { path: 'system.label', label: '위쪽 작은 영문', type: 'text' },
   ...[0, 1, 2].flatMap(i => [
    { path: `system.rows.${i}.a`, label: `${i + 1}번째 줄 앞말`, type: 'text', at: 8.5 + i + .8 },
    { path: `system.rows.${i}.b`, label: `${i + 1}번째 줄 뒷말 (빨간 글자)`, type: 'text', at: 8.5 + i + .8, fit: { size: 140, weight: 900, family: KR, spacing: -4, max: 640 } }]),
   { path: 'system.sub', label: '아래 설명', type: 'text', fit: { size: 44, weight: 700, family: KR, max: 1600 } }] },
  { tab: 'text', title: '수상', at: T.awards, fields: [
   { path: 'awards.label', label: '위쪽 작은 영문', type: 'text' }] },
  ...[0, 1].map(i => ({ tab: 'text', title: `수상 ${i + 1} (${i ? '오른쪽' : '왼쪽'})`, at: T.awards, fields: [
   { path: `awards.items.${i}.n`, label: '숫자', type: 'number', min: 0, max: 99, step: 1, desc: '딸깍 소리에 맞춰 0부터 올라가요' },
   { path: `awards.items.${i}.unit`, label: '숫자 옆 빨간 글자', type: 'text' },
   { path: `awards.items.${i}.title`, label: '상 이름', type: 'text', fit: { size: 42, weight: 700, family: KR, max: 740 } },
   { path: `awards.items.${i}.brand`, label: '받은 브랜드 (빨간 글자)', type: 'text', fit: { size: 34, weight: 700, family: KR, max: 740 } },
   { path: `awards.items.${i}.org`, label: '주최', type: 'text', fit: { size: 24, weight: 500, family: KR, max: 740 } }] })),
  { tab: 'text', title: '세계로', at: T.global, fields: [
   { path: 'global.label', label: '위쪽 작은 영문', type: 'text' },
   { path: 'global.lead', label: '첫 줄', type: 'text', fit: { size: 52, weight: 700, family: KR, max: 1600 } },
   { path: 'global.title', label: '큰 제목', type: 'text', fit: { size: 110, weight: 900, family: KR, spacing: -3, max: 1600 } },
   { path: 'global.sub', label: '아래 설명', type: 'text', fit: { size: 36, weight: 500, family: KR, max: 1600 } }] },
  { tab: 'text', title: '나라 이름 (6개)', at: T.global, columns: 2, note: '나라는 뿅 소리에 맞춰 6개가 차례로 나와서 개수는 바꿀 수 없어요.',
   fields: [0, 1, 2, 3, 4, 5].map(i => ({ path: `global.countries.${i}`, label: `${i + 1}번째`, type: 'text', fit: { size: 50, weight: 700, family: KR, max: 260 } })) },
  { tab: 'text', title: '엔딩', at: T.ending, fields: [
   { path: 'ending.brand', label: '회사 이름', type: 'text', fit: { size: 220, weight: 900, family: KR, spacing: -4, max: 1700 } },
   { path: 'ending.slogan1', label: '슬로건 앞부분', type: 'text' },
   { path: 'ending.slogan2', label: '슬로건 빨간 글자', type: 'text' },
   { path: 'ending.url', label: '홈페이지 주소', type: 'text' }] },
  { tab: 'text', title: '화면 위 고정 표기', at: 10, note: '4초부터 25초까지 화면 위쪽 양 끝에 나와요.', fields: [
   { path: 'hud.brand', label: '왼쪽 위', type: 'text' },
   { path: 'hud.since', label: '오른쪽 위', type: 'text' }] },
  { tab: 'color', title: '브랜드', fields: [
   { path: 'colors.red', label: '재능 레드', desc: '빨간 글자, 교육 50년 배경, 막대·점·줄', type: 'color', at: T.history }] },
  { tab: 'color', title: '배경', fields: [
   { path: 'colors.black', label: '검정 배경', desc: '첫 장면·수상 배경, 밝은 장면의 검은 글자', type: 'color', at: T.hook + 1.5 },
   { path: 'colors.char', label: '짙은 회색 배경', desc: '세계로 장면 배경', type: 'color', at: T.global },
   { path: 'colors.paper', label: '밝은 배경', desc: '스스로학습시스템·엔딩 배경', type: 'color', at: T.system }] },
  { tab: 'color', title: '글자', fields: [
   { path: 'colors.white', label: '흰 글자', desc: '어두운 장면의 글자와 그리드 선', type: 'color', at: T.awards },
   { path: 'colors.gray', label: '회색 글자', desc: '아직 차례가 아닌 뒷말, 수상 주최', type: 'color', at: T.awards },
   { path: 'colors.ink', label: '진한 글자', desc: '스스로학습시스템 아래 설명', type: 'color', at: T.system },
   { path: 'colors.soft', label: '연회색 글자', desc: '세계로 아래 설명', type: 'color', at: T.global },
   { path: 'colors.url', label: '주소 글자', desc: '엔딩의 홈페이지 주소', type: 'color', at: T.ending }] },
 ],
 locked: '장면 순서와 길이, 글자가 나오는 시각, 움직임, 음악은 고칠 수 없어요. 비트와 효과음이 장면 전환과 글자 등장에 맞춰 만들어져 있어서예요.',
 warnings: ['숫자(연도·수상 횟수)나 나라 이름을 바꿔도 딸깍·뿅 소리의 횟수와 시각은 그대로예요.'],
};
})();
