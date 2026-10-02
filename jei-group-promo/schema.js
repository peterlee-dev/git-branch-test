// 영상 편집기(../video-editor.html)에 보여 줄 칸 설명. 규칙: ../editor/PROTOCOL.md
(() => {
const KR = "'Noto Sans KR'", EN = "'Inter'";
const txt = (path, label, at, fit) => ({ path, label, type: 'text', ...(at != null ? { at } : {}), ...(fit ? { fit } : {}) });
const col = (path, label, desc, at) => ({ path, label, desc, type: 'color', at });
const D = window.CONTENT.divisions;
window.SCHEMA = {
 id: 'jei-group-promo',
 title: '재능그룹 홍보',
 duration: 52, fps: 30,
 audio: ['audio/mix.wav', 'audio/mix.mp3'],
 audioFade: { in: 0.05, out: 1.8 },
 scenes: [
  { start: 0, end: 4, label: '비전', dark: true },
  { start: 4, end: 8, label: '종합교육문화기업' },
  ...D.map((d, i) => ({ start: 8 + i * 6, end: 14 + i * 6, label: `${d.no} ${d.name}` })),
  { start: 38, end: 44, label: '계열사 연결도' },
  { start: 44, end: 52, label: '엔딩', dark: true },
 ],
 sounds: [
  { t: 4, label: '비트 시작', big: true },
  ...[3.5, 7.5, 13.5, 19.5, 25.5, 31.5, 37.5].map(t => ({ t, label: '장면 전환' })),
  { t: 44, label: '엔딩', big: true },
 ],
 tabs: [{ id: 'text', label: '문구' }, { id: 'color', label: '색' }],
 groups: [
  { tab: 'text', title: '비전', at: 3.3, fields: [
   txt('intro.en', '영문 비전', null, { size: 74, weight: 800, family: EN, max: 1760 }),
   txt('intro.ko', '한글 비전'), txt('intro.brand', '그룹 이름')] },
  { tab: 'text', title: '종합교육문화기업', at: 7.4, note: '사업 분야 7개는 박자에 맞춰 하나씩 나와서 개수는 바꿀 수 없어요.', fields: [
   txt('overview.since', '위쪽 표기'), txt('overview.title', '첫 줄'),
   txt('overview.title2', '빨간 큰 글자', null, { size: 132, weight: 900, family: KR, spacing: -3, max: 1600 }),
   ...[0, 1, 2, 3, 4, 5, 6].map(i => txt(`overview.fields.${i}`, `분야 ${i + 1}`, null, { size: 52, weight: 900, family: KR, max: 190 }))] },
  ...D.map((d, i) => ({ tab: 'text', title: `${d.no} ${d.name}`, at: 8 + i * 6 + 5, note: '계열사 수와 아이콘은 장면 박자에 맞춰 고정이에요.', fields: [
   txt(`divisions.${i}.name`, '부문 이름'),
   ...d.items.flatMap((it, j) => [
    txt(`divisions.${i}.items.${j}.name`, `${j + 1}번째 계열사`),
    txt(`divisions.${i}.items.${j}.desc`, `${j + 1}번째 설명`, null, { size: d.items.length === 1 ? 32 : 28, weight: 500, family: KR, max: 820 })]),
   ...(d.items[0].chips || []).map((c, k) => txt(`divisions.${i}.items.0.chips.${k}`, `대표 브랜드 ${k + 1}`))] })),
  { tab: 'text', title: '계열사 연결도', at: 43, fields: [txt('network.center', '가운데'), txt('network.caption', '아래 문구')] },
  { tab: 'text', title: '엔딩', at: 49, fields: [
   txt('ending.brand', '그룹 이름', null, { size: 230, weight: 900, family: KR, max: 1700 }), txt('ending.en', '영문 이름'),
   txt('ending.slogan', '영문 비전', null, { size: 50, weight: 700, family: EN, max: 1760 }), txt('ending.sub', '한글 비전'), txt('ending.url', '주소')] },
  { tab: 'color', title: '브랜드', fields: [col('colors.red', '재능 레드', '엔딩 배경, 강조 글자', 49), col('colors.ink', '진한 색', '첫 장면 배경, 글자', 3)] },
  { tab: 'color', title: '사업 부문 색', fields: D.map((d, i) => col(`colors.d${i + 1}`, `${d.no} ${d.name}`, '왼쪽 판, 아이콘 칸, 연결도', 8 + i * 6 + 5)) },
  { tab: 'color', title: '배경·글자', fields: [col('colors.paper', '밝은 배경', '대부분의 장면', 7.4), col('colors.white', '흰색', '카드, 흰 글자', 20), col('colors.muted', '설명 글자', '카드 설명', 20)] },
 ],
 locked: '장면 순서와 길이, 계열사 수, 아이콘, 움직임, 음악은 고칠 수 없어요. 비트와 효과음이 장면 전환과 카드 등장에 맞춰져 있어서예요.',
 warnings: [],
};
})();
