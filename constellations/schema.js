// 영상 편집기(../video-editor.html)에 보여 줄 칸 설명. 규칙: ../editor/PROTOCOL.md
(() => {
const KR = "'Noto Sans KR'", EN = "'Inter'";
// 별자리 장면 시각 (index.html 의 PANELS·CAM 과 같음, 음악에 맞춰져 있어 고정)
const P = [
 { s: 5.0, e: 10.4, factAt: 8.9, name: '북두칠성', stars: [['dubhe', '두베'], ['merak', '메라크'], ['alkaid', '알카이드'], ['mizar', '미자르']] },
 { s: 11.8, e: 16.0, factAt: 13.4, name: '카시오페이아자리', stars: [['caph', '카프'], ['schedar', '시더'], ['navi', '나비'], ['ruchbah', '루크바'], ['segin', '세긴']] },
 { s: 17.4, e: 22.0, factAt: 19.2, name: '오리온자리', stars: [['betelgeuse', '베텔게우스'], ['rigel', '리겔'], ['bellatrix', '벨라트릭스'], ['saiph', '사이프']] },
 { s: 23.6, e: 27.4, factAt: 25.2, name: '여름철 대삼각형', stars: [['vega', '베가'], ['deneb', '데네브'], ['altair', '알타이르']] },
];
const LINES = [[5.0, '북두칠성 선'], [8.9, '북극성 찾기 선'], [11.8, '카시오페이아 선'], [17.4, '오리온 선'], [23.6, '백조자리 선'], [24.4, '대삼각형 선']];
window.SCHEMA = {
 id: 'constellations',
 title: '밤하늘 별자리 여행',
 duration: 30, fps: 30,
 audio: ['audio/mix.wav', 'audio/mix.mp3'],
 audioFade: { in: 0.3, out: 2 },
 scenes: [
  { start: 0, end: 4.6, label: '타이틀', dark: true },
  { start: 4.6, end: 10.6, label: '북두칠성 · 북극성' },
  { start: 10.6, end: 16.4, label: '카시오페이아자리' },
  { start: 16.4, end: 22.6, label: '오리온자리' },
  { start: 22.6, end: 27.6, label: '여름철 대삼각형' },
  { start: 27.6, end: 30, label: '마무리', dark: true },
 ],
 sounds: [
  { t: 0.6, label: '타이틀 종소리' },
  ...LINES.map(([t, label]) => ({ t, label })),
  { t: 9.4, label: '북극성 반짝임', big: true },
  { t: 25.2, label: '은하수 반짝임', big: true },
  { t: 27.8, label: '마무리 종소리' },
  { t: 28.3, label: '마무리 반짝임' },
 ],
 tabs: [{ id: 'text', label: '문구' }, { id: 'stars', label: '별 이름' }, { id: 'color', label: '색' }],
 groups: [
  { tab: 'text', title: '처음 타이틀', at: 2.5, fields: [
   { path: 'title.kicker', label: '작은 영문', type: 'text', fit: { size: 22, weight: 500, family: EN, spacing: 14, max: 1760 } },
   { path: 'title.main', label: '제목', type: 'text', fit: { size: 104, weight: 200, family: KR, spacing: 6, max: 1760 } },
   { path: 'title.sub', label: '부제', type: 'text', fit: { size: 30, weight: 400, family: KR, max: 1760 } }] },
  ...P.map((pn, i) => ({ tab: 'text', title: `${i + 1}. ${pn.name}`, at: pn.s + 2.5, fields: [
   { path: `panels.${i}.season`, label: '계절 · 방향 (작은 영문)', type: 'text', fit: { size: 20, weight: 500, family: EN, spacing: 5, max: 1640 } },
   { path: `panels.${i}.name`, label: '별자리 이름', type: 'text', fit: { size: 88, weight: 200, family: KR, spacing: 2, max: 1640 } },
   { path: `panels.${i}.sub`, label: '설명', type: 'text', fit: { size: 32, weight: 400, family: KR, max: 1640 } },
   { path: `panels.${i}.fact`, label: '알아 두기 (금색 문구)', type: 'text', at: pn.factAt + .9, fit: { size: 28, weight: 400, family: KR, max: 1640 } }] })),
  { tab: 'text', title: '마무리', at: 29, fields: [
   { path: 'ending.main', label: '마무리 문구', type: 'text', fit: { size: 84, weight: 200, family: KR, spacing: 4, max: 1760 } },
   { path: 'ending.sub', label: '아래 문구', type: 'text', fit: { size: 28, weight: 400, family: KR, max: 1760 } },
   { path: 'ending.brand', label: '회사 이름 (오른쪽 아래)', type: 'text', fit: { size: 26, weight: 500, family: KR, max: 120 } }] },
  ...P.map((pn, i) => ({ tab: 'stars', title: pn.name, at: pn.s + 2.2, columns: 2,
   ...(i === 0 ? { note: '별 바로 옆에 붙어 나오는 이름이에요. 길게 쓰면 옆 별의 이름과 겹칠 수 있어요.' } : {}),
   fields: pn.stars.map(([k, label]) => ({ path: `stars.${k}`, label, type: 'text', fit: { size: 22, weight: 400, family: KR, max: 360 } })) })),
  { tab: 'stars', title: '북극성', at: 10.2, fields: [
   { path: 'polaris', label: '북극성 이름 (금색)', type: 'text', fit: { size: 30, weight: 500, family: KR, max: 400 } }] },
  { tab: 'color', title: '글자', fields: [
   { path: 'colors.ink', label: '주 글자', desc: '제목, 별자리 이름과 설명', type: 'color', at: 7.5 },
   { path: 'colors.dim', label: '보조 글자', desc: '작은 영문, 부제, 별 이름', type: 'color', at: 2.5 },
   { path: 'colors.faint', label: '흐린 표시', desc: '별 둘레 동그라미, 아래 진행 막대 바탕, RA·DEC 좌표', type: 'color', at: 7.5 },
   { path: 'colors.glow', label: '제목 빛 번짐', desc: '큰 제목 둘레의 푸른 빛', type: 'color', at: 2.5 }] },
  { tab: 'color', title: '강조', fields: [
   { path: 'colors.gold', label: '금색 강조', desc: '알아 두기 문구, 번호, 북극성 표시, 진행 막대', type: 'color', at: 9.8 },
   { path: 'colors.brand', label: '재능교육 사각형', desc: '마지막 회사 이름 옆', type: 'color', at: 29 }] },
  { tab: 'color', title: '하늘 · 별자리 선', fields: [
   { path: 'colors.line', label: '별자리 선', desc: '북두칠성·카시오페이아·오리온·백조자리를 잇는 선', type: 'color', at: 7.5 },
   { path: 'colors.guide', label: '안내 선', desc: '북극성 찾는 점선, 여름철 대삼각형', type: 'color', at: 26 },
   { path: 'colors.sky', label: '밤하늘 바탕', desc: '별 뒤의 가장 어두운 바탕색', type: 'color', at: 14 }] },
 ],
 locked: '장면 순서와 시각, 카메라 움직임, 별 위치·밝기·색(실제 천문 데이터), 음악은 고칠 수 없어요. 별자리 선이 그려질 때마다 울리는 종소리가 장면 시각에 맞춰져 있어서예요.',
 warnings: ['문구가 나오는 시각은 음악에 맞춰져 있어서 옮길 수 없어요. 글자와 색만 바꿀 수 있어요.'],
};
})();
