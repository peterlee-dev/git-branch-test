// 영상 편집기(../video-editor.html)에 보여 줄 칸 설명. 규칙: ../editor/PROTOCOL.md
// 이 영상의 시각은 '원본 시각'(내레이션에 맞춰 늘리기 전)으로 짜여 있어서, 편집기에 줄 시각은 R() 로 실제 시각으로 바꿈
(() => {
const WARP = window.WARP || [], SUBS = window.SUBS || [];
const R = v => +WARP.reduce((r, [vs, ve, f]) => v > vs ? r + (Math.min(v, ve) - vs) * (f - 1) : r, v).toFixed(3);
const KR = "'Noto Sans KR'";
const DURATION = R(124);
const SEC = [[6.5, '개념 1'], [20, '개념 2'], [38, '개념 3'], [60.5, '개념 4'], [84.5, '개념 5'], [96, '예제']];
const subAt = s => R((s[0] + s[1]) / 2);
window.SCHEMA = {
 id: 'pythagoras',
 title: '피타고라스 정리',
 duration: DURATION, fps: 30,
 audio: ['audio/mix.wav', 'audio/mix.mp3'],
 audioFade: { in: 0.3, out: 2 },
 scenes: [
  { start: 0, end: R(6.5), label: '타이틀', dark: true },
  { start: R(6.5), end: R(20), label: '개념 1 · 직각삼각형과 빗변' },
  { start: R(20), end: R(38), label: '개념 2 · 세 변 위의 정사각형' },
  { start: R(38), end: R(60.5), label: '개념 3 · 칸 세기' },
  { start: R(60.5), end: R(84.5), label: '개념 4 · 그림으로 증명' },
  { start: R(84.5), end: R(96), label: '개념 5 · 공식' },
  { start: R(96), end: R(116), label: '예제' },
  { start: R(116), end: DURATION, label: '마무리' },
 ],
 sounds: [6.05, 60.05, 84.05, 95.55, 115.55].map(t => ({ t: R(t), label: '장면 전환', big: true })),
 tabs: [{ id: 'sub', label: '자막' }, { id: 'text', label: '화면 글자' }, { id: 'color', label: '색' }],
 groups: [
  { tab: 'sub', title: '내레이션 자막', at: subAt(SUBS[0] || [0, 1]),
   note: '자막 문구만 바뀌고 내레이션 음성과 나오는 시각은 그대로예요. 영문 소문자(a, b, c)는 기울어진 수학 글자로, ²는 위첨자로 그려져요.',
   fields: SUBS.map((s, i) => ({ path: `subs.${i}`, label: `${i + 1}. ${R(s[0]).toFixed(1)}초`, type: 'text', at: subAt(s),
    fit: { size: 42, weight: 500, family: KR, max: 1680 } })) },
  { tab: 'text', title: '타이틀', at: R(3), fields: [
   { path: 'title.kicker', label: '작은 제목', type: 'text' },
   { path: 'title.line1', label: '큰 제목 첫 줄', type: 'text', fit: { size: 150, weight: 900, family: KR, max: 1000 } },
   { path: 'title.line2', label: '큰 제목 둘째 줄', type: 'text', fit: { size: 150, weight: 900, family: KR, max: 1000 } },
   { path: 'title.brand', label: '오른쪽 아래 회사 이름', type: 'text' }] },
  { tab: 'text', title: '위쪽 제목 막대', at: R(12), note: '개념마다 왼쪽에 이름표와 제목이, 오른쪽에 과목 이름이 나와요.', fields: [
   { path: 'header.right', label: '오른쪽 과목 이름', type: 'text', fit: { size: 28, weight: 500, family: KR, max: 560 } },
   ...SEC.flatMap(([s, name], i) => [
    { path: `sections.${i}.tag`, label: `${name} 이름표`, type: 'text', at: R(s + 2) },
    { path: `sections.${i}.name`, label: `${name} 제목`, type: 'text', at: R(s + 2), fit: { size: 48, weight: 700, family: KR, max: 1000 } }])] },
  { tab: 'text', title: '개념 1 · 직각삼각형과 빗변', at: R(17), fields: [
   { path: 'concept1.legs', label: 'a, b 설명', type: 'text', fit: { size: 40, weight: 700, family: KR, max: 540 } },
   { path: 'concept1.hyp', label: 'c 이름', type: 'text' },
   { path: 'concept1.hypDesc', label: 'c 설명', type: 'text', fit: { size: 36, weight: 700, family: KR, max: 540 } },
   { path: 'concept1.hypPill', label: '그림 속 빗변 이름표', type: 'text' }] },
  { tab: 'text', title: '개념 2 · 세 변 위의 정사각형', at: R(32), fields: [
   { path: 'concept2.sqA', label: 'a² 설명', type: 'text', fit: { size: 36, weight: 700, family: KR, max: 560 } },
   { path: 'concept2.sqB', label: 'b² 설명', type: 'text', fit: { size: 36, weight: 700, family: KR, max: 560 } },
   { path: 'concept2.sqC', label: 'c² 설명', type: 'text', fit: { size: 36, weight: 700, family: KR, max: 560 } }] },
  { tab: 'text', title: '개념 3 · 칸 세기', at: R(55), fields: [
   { path: 'concept3.unit', label: '칸 수 뒤에 붙는 말', type: 'text' }] },
  { tab: 'text', title: '개념 4 · 그림으로 증명', at: R(82), fields: [
   { path: 'proof.left', label: '왼쪽 그림 아래 설명', type: 'text', fit: { size: 30, weight: 500, family: KR, max: 760 } },
   { path: 'proof.right', label: '오른쪽 그림 아래 설명', type: 'text', fit: { size: 30, weight: 500, family: KR, max: 760 } }] },
  { tab: 'text', title: '개념 5 · 공식', at: R(93), fields: [
   { path: 'formula.pill', label: '이름표', type: 'text' },
   { path: 'formula.cond', label: '위 작은 글', type: 'text' },
   { path: 'formula.statement', label: '말로 쓴 공식', type: 'text', fit: { size: 50, weight: 700, family: KR, max: 1140 } }] },
  { tab: 'text', title: '마무리', at: R(121), fields: [
   { path: 'end.kicker', label: '작은 제목', type: 'text' },
   { path: 'end.title', label: '큰 제목', type: 'text', fit: { size: 110, weight: 900, family: KR, max: 1800 } },
   { path: 'end.closing', label: '마지막 한마디', type: 'text', fit: { size: 50, weight: 700, family: KR, max: 1800 } },
   { path: 'end.brand', label: '오른쪽 아래 회사 이름', type: 'text' }] },
  { tab: 'color', title: '브랜드 · 바탕', fields: [
   { path: 'colors.red', label: '브랜드 빨강', desc: '장면 전환, 이름표, 강조 글자, 마무리 바탕, a² 정사각형', type: 'color', at: R(12) },
   { path: 'colors.black', label: '검정', desc: '타이틀 바탕, 본문 글자, 삼각형 선, 자막 상자', type: 'color', at: R(3) },
   { path: 'colors.paper', label: '종이 바탕', desc: '개념·예제 장면의 바탕', type: 'color', at: R(12) },
   { path: 'colors.white', label: '흰색', desc: '설명 상자, 삼각형 안, 흰 글자', type: 'color', at: R(17) },
   { path: 'colors.gray', label: '회색 글자', desc: '과목 이름, 보조 설명', type: 'color', at: R(93) }] },
  { tab: 'color', title: '세 정사각형', note: 'a² · b² · c² 색은 영상 전체(수식 색 칩 포함)에서 같이 바뀌어요.', fields: [
   { path: 'colors.char', label: 'b² 정사각형', desc: '진한 회색', type: 'color', at: R(32) },
   { path: 'colors.pink', label: 'c² 정사각형', desc: '연분홍', type: 'color', at: R(32) },
   { path: 'colors.redDeep', label: 'c² 글자', desc: '분홍 위 진한 빨강 글자', type: 'color', at: R(32) },
   { path: 'colors.litA', label: 'a² 칸 세기', desc: '한 칸씩 켜지는 색', type: 'color', at: R(44) },
   { path: 'colors.litB', label: 'b² 칸 세기', desc: '한 칸씩 켜지는 색', type: 'color', at: R(47.5) },
   { path: 'colors.litC', label: 'c² 칸 세기', desc: '한 칸씩 켜지는 색', type: 'color', at: R(51.2) },
   { path: 'colors.tri', label: '증명 속 삼각형', desc: '큰 정사각형 안의 삼각형 4개', type: 'color', at: R(73) }] },
 ],
 locked: '수식(a² + b² = c², 3² + 4² = 5², 6·8·10 예제), 삼각형과 정사각형의 크기·모양, 장면 순서와 길이는 고칠 수 없어요. 예제 삼각형 3-4-5의 칸 수와 그림, 내레이션이 서로 맞아야 하고, 소리가 장면에 맞춰 만들어져 있어서예요.',
 warnings: [
  '자막을 바꿔도 내레이션 음성은 그대로예요. 말하는 내용과 다르게 고치지 않도록 조심하세요. 음성까지 바꾸려면 tools/make_audio.py 를 고쳐 다시 만들어야 해요.',
  '자막이 나오는 시각은 고정이에요. 너무 길게 쓰면 읽기 전에 사라질 수 있어요.',
 ],
};
})();
