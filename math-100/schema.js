// 영상 편집기(../video-editor.html)에 보여 줄 칸 설명. 규칙: ../editor/PROTOCOL.md
// 그림 코드의 시각은 늘리기 전(애니메이션) 시각이라, 편집기에 줄 시각은 warp.js 로 실제 재생 시각으로 바꿈
(() => {
const WARP = window.WARP || [];
const R = v => +WARP.reduce((r, [vs, ve, f]) => v > vs ? r + (Math.min(v, ve) - vs) * (f - 1) : r, v).toFixed(3);
const JUA = "'Jua'";
const fit = (size, max) => ({ size, weight: 400, family: JUA, spacing: 0, max });
// 자막이 나오는 시각(늘리기 전). index.html 의 SUB_TIMES 와 같음 — 편집기에서 칸을 누를 때 이동할 위치로만 씀
const SUB_AT = [7.6, 13, 16, 19.4, 23.4, 26.9, 31.6, 36, 39.4, 45.6, 49.2, 53.3, 57, 62.4, 65.2, 68, 71.6, 74.5, 77, 80.8, 83.5, 86, 89.6, 92.6, 95.2, 97.8, 101.4];
const CONCEPT_AT = [7, 31, 45, 71, 89];
window.SCHEMA = {
 id: 'math-100',
 title: '100까지의 수',
 duration: R(114), fps: 30,
 audio: ['audio/mix.wav', 'audio/mix.mp3'],
 audioFade: { in: 0.3, out: 2 },
 scenes: [
  { start: 0, end: R(7), label: '타이틀' },
  { start: R(7), end: R(31), label: '개념 1 · 60, 70, 80, 90' },
  { start: R(31), end: R(45), label: '개념 2 · 99까지의 수' },
  { start: R(45), end: R(71), label: '개념 3 · 수의 순서' },
  { start: R(71), end: R(89), label: '개념 4 · 크기 비교' },
  { start: R(89), end: R(106), label: '개념 5 · 짝수와 홀수' },
  { start: R(106), end: R(114), label: '오늘 배운 개념' },
 ],
 sounds: [
  ...[6.95, 30.55, 44.55, 70.55, 88.55, 105.55].map(t => ({ t: R(t), label: '슉' })),
  ...[13.6, 36.2, 65.6, 76.6, 87, 93.1].map(t => ({ t: R(t), label: '띵', big: true })),
  { t: R(109), label: '반짝', big: true },
 ],
 tabs: [{ id: 'text', label: '문구' }, { id: 'sub', label: '자막' }, { id: 'color', label: '색' }],
 groups: [
  { tab: 'text', title: '타이틀', at: R(3.5), fields: [
   { path: 'title.grade', label: '학년 · 단원', type: 'text', fit: fit(54, 980) },
   { path: 'title.main', label: '큰 제목', type: 'text', fit: fit(190, 1000) },
   { path: 'title.badge', label: '제목 아래 띠', type: 'text', fit: fit(64, 900) },
   { path: 'title.brand', label: '오른쪽 아래 회사 이름', type: 'text' }] },
  { tab: 'text', title: '타이틀 아래 작은 띠', at: R(3.5), columns: 2, note: '작은 띠는 176px 간격으로 놓여서, 너무 길면 옆 띠와 겹쳐요.',
   fields: [0, 1, 2, 3, 4].map(i => ({ path: `title.chips.${i}`, label: `${i + 1}번째`, type: 'text', fit: fit(30, 130) })) },
  { tab: 'text', title: '위쪽 제목 띠', at: R(8), fields: [
   { path: 'header.concept', label: '번호 앞 글자 (예: 개념 → 개념 1)', type: 'text' },
   { path: 'header.unit', label: '오른쪽 단원 이름', type: 'text', fit: fit(38, 420) }] },
  { tab: 'text', title: '개념 이름', note: '위쪽 제목 띠와 마지막 정리 화면에 함께 나와요.',
   fields: [0, 1, 2, 3, 4].map(i => ({ path: `concepts.${i}`, label: `개념 ${i + 1}`, type: 'text', at: R(CONCEPT_AT[i] + 1.5), fit: fit(44, 580) })) },
  { tab: 'text', title: '개념 1 · 표', at: R(21), fields: [
   ...[0, 1, 2].map(i => ({ path: `s1.tableHead.${i}`, label: `표 머리 ${i + 1}`, type: 'text' })),
   { path: 'or', label: "읽는 법 사이 글자 ('또는')", type: 'text', at: R(17) }] },
  { tab: 'text', title: '개념 2 · 자리 이름', at: R(38), fields: [
   { path: 's2.tensLabel', label: '십의 자리 설명', type: 'text' },
   { path: 's2.onesLabel', label: '일의 자리 설명', type: 'text' }] },
  { tab: 'text', title: '개념 3 · 수의 순서', fields: [
   { path: 's3.smaller', label: '왼쪽 띠', type: 'text', at: R(50), fit: fit(40, 300) },
   { path: 's3.bigger', label: '오른쪽 띠', type: 'text', at: R(50), fit: fit(40, 300) },
   { path: 's3.stepHint', label: '수 배열표 아래 글자', type: 'text', at: R(59) }] },
  { tab: 'text', title: '개념 5 · 짝수와 홀수', fields: [
   { path: 's5.evenNote', label: '6개 아래 글자', type: 'text', at: R(96), fit: fit(50, 820) },
   { path: 's5.oddNote', label: '7개 아래 글자', type: 'text', at: R(96), fit: fit(50, 820) },
   { path: 's5.even', label: "'짝수' 이름", type: 'text', at: R(96) },
   { path: 's5.odd', label: "'홀수' 이름", type: 'text', at: R(96) },
   { path: 's5.evenDesc', label: '짝수 설명', type: 'text', at: R(103), fit: fit(32, 1200) },
   { path: 's5.oddDesc', label: '홀수 설명', type: 'text', at: R(103), fit: fit(32, 1200) }] },
  { tab: 'text', title: '마지막 정리', at: R(111), fields: [
   { path: 'end.title', label: '제목', type: 'text', fit: fit(76, 1200) },
   { path: 'end.cheer', label: '맺는 말', type: 'text', fit: fit(60, 1240) },
   { path: 'end.brand', label: '오른쪽 아래 회사 이름', type: 'text' }] },
  { tab: 'sub', title: '화면 아래 자막', note: '자막이 나오는 시각은 내레이션에 맞춰 고정되어 있어요. 문구만 바꿀 수 있어요.',
   fields: SUB_AT.map((t, i) => ({ path: `subs.${i}`, label: `자막 ${i + 1}`, type: 'text', at: R(t + .5), fit: fit(50, 1680) })) },
  { tab: 'color', title: '레드 (십의 자리)', fields: [
   { path: 'colors.red', label: '브랜드 레드', desc: '타이틀 배경, 십의 자리 숫자, 10개씩 묶음 블록, 장면 전환', type: 'color', at: R(3.5) },
   { path: 'colors.redDeep', label: '진한 레드', desc: '블록 테두리', type: 'color', at: R(12) },
   { path: 'colors.redSoft', label: '연한 레드', desc: '캐릭터 볼, 강조 테두리', type: 'color', at: R(76) },
   { path: 'colors.pink', label: '분홍', desc: '카드 테두리, 강조 칸 바탕', type: 'color', at: R(16) },
   { path: 'colors.pinkDot', label: '배경 점', desc: '배경의 물방울 무늬', type: 'color', at: R(20) }] },
  { tab: 'color', title: '블랙 (일의 자리)', fields: [
   { path: 'colors.black', label: '블랙', desc: '일의 자리 숫자, 본문 글자, 캐릭터 발·눈', type: 'color', at: R(38) },
   { path: 'colors.ink', label: '보조 글자', desc: '블록 아래 설명 글자', type: 'color', at: R(12) },
   { path: 'colors.gray', label: '회색 글자', desc: "단원 이름, '또는', 짝수·홀수 설명", type: 'color', at: R(17) },
   { path: 'colors.cubeDark', label: '낱개 블록', desc: '낱개 블록 색', type: 'color', at: R(38) },
   { path: 'colors.cubeDarkEdge', label: '낱개 블록 테두리', type: 'color', at: R(38) }] },
  { tab: 'color', title: '바탕', fields: [
   { path: 'colors.cream', label: '크림 바탕', desc: '개념 장면 배경', type: 'color', at: R(20) },
   { path: 'colors.white', label: '흰색', desc: '카드, 자막 상자, 레드 위 글자', type: 'color', at: R(16) }] },
 ],
 locked: '장면 순서와 길이, 움직임, 자막이 나오는 시각은 고칠 수 없어요. 내레이션과 효과음이 화면에 맞춰 만들어져 있어서예요. 블록 개수, 숫자, 읽는 법(육십·예순 등)처럼 수학 내용 자체인 글자도 그림과 내레이션에 맞물려 있어서 잠가 두었어요.',
 warnings: [
  '자막을 바꿔도 내레이션 음성은 그대로예요. 음성과 다른 말이 되지 않게 조심해 주세요.',
  '맺는 말도 내레이션("스스로 정리 끝! 참 잘했어요!")과 함께 나와요.',
 ],
};
})();
