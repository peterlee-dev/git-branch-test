// 영상 편집기(../video-editor.html)에 보여 줄 칸 설명. 규칙: ../editor/PROTOCOL.md
(() => {
const SONG = window.SONG || { beat: .5 }, TK = SONG.beat / .5, g = x => +(x * TK).toFixed(3);   // 격자 초 → 실제 초
const DS = [8, 14, 18, 22, 26], DL = [6, 4, 4, 4, 6];
const KR = "'Noto Sans KR'", EN = "'Inter'";
const txt = (path, label, at, fit) => ({ path, label, type: 'text', ...(at != null ? { at } : {}), ...(fit ? { fit } : {}) });
const col = (path, label, desc, at) => ({ path, label, desc, type: 'color', at });
const D = window.CONTENT.divisions;
window.SCHEMA = {
 id: 'jei-group-promo',
 title: '재능그룹 홍보',
 duration: 48 * TK, fps: 30,
 audio: ['audio/mix.wav', 'audio/mix.mp3'],
 audioFade: { in: 0.1, out: 2.2 },
 scenes: [
  { start: 0, end: g(4), label: '비전', dark: true },
  { start: g(4), end: g(8), label: '종합교육문화기업', dark: true },
  ...D.map((d, i) => ({ start: g(DS[i]), end: g(DS[i] + DL[i]), label: d.name, dark: true })),
  { start: g(32), end: g(34), label: '숨 고르기', dark: true },
  { start: g(34), end: g(40), label: '지식맵 (드롭)', dark: true },
  { start: g(40), end: g(48), label: '엔딩', dark: true },
 ],
 sounds: [
  { t: g(18), label: '베이스 들어옴', big: true },
  ...[3.5, 7.5, ...DS.map((s, i) => s + DL[i] - .5)].map(t => ({ t: g(t), label: '장면 전환' })),
  { t: g(34), label: '드롭 · 지식맵', big: true },
  { t: g(40), label: '엔딩', big: true },
 ],
 tabs: [{ id: 'text', label: '문구' }, { id: 'color', label: '색' }],
 groups: [
  { tab: 'text', title: '비전', at: g(3.3), fields: [
   txt('intro.en', '영문 비전', null, { size: 74, weight: 800, family: EN, max: 1760 }),
   txt('intro.ko', '한글 비전'), txt('intro.brand', '그룹 이름')] },
  { tab: 'text', title: '종합교육문화기업', at: g(7.4), note: '사업 분야 7개는 박자에 맞춰 하나씩 나와서 개수는 바꿀 수 없어요.', fields: [
   txt('overview.since', '위쪽 표기'), txt('overview.title', '첫 줄'),
   txt('overview.title2', '큰 글자', null, { size: 132, weight: 900, family: KR, spacing: -3, max: 1600 }),
   ...[0, 1, 2, 3, 4, 5, 6].map(i => txt(`overview.fields.${i}`, `분야 ${i + 1}`, null, { size: 52, weight: 900, family: KR, max: 190 }))] },
  ...D.map((d, i) => ({ tab: 'text', title: d.name, at: g(DS[i] + DL[i] - 1), note: '계열사 수와 아이콘은 장면 박자에 맞춰 고정이에요.', fields: [
   txt(`divisions.${i}.name`, '부문 이름'), txt(`divisions.${i}.en`, '부문 영문 이름'),
   ...d.items.flatMap((it, j) => [
    txt(`divisions.${i}.items.${j}.name`, `${j + 1}번째 계열사`),
    txt(`divisions.${i}.items.${j}.desc`, `${j + 1}번째 설명`, null, { size: d.items.length === 1 ? 32 : 28, weight: 500, family: KR, max: 820 })]),
   ...(d.items[0].chips || []).map((c, k) => txt(`divisions.${i}.items.0.chips.${k}`, `대표 브랜드 ${k + 1}`))] })),
  { tab: 'text', title: '지식맵', at: g(38.9), note: '계열사 키워드는 각 사업 부문 칸의 계열사마다 정해져 있어요 (content.js 의 tags).', fields: [txt('network.center', '가운데'), txt('network.caption', '아래 문구')] },
  { tab: 'text', title: '엔딩', at: g(45), fields: [
   txt('ending.brand', '그룹 이름', null, { size: 230, weight: 900, family: KR, max: 1700 }), txt('ending.en', '영문 이름'),
   txt('ending.slogan', '영문 비전', null, { size: 50, weight: 700, family: EN, max: 1760 }), txt('ending.sub', '한글 비전'), txt('ending.url', '주소')] },
  { tab: 'color', title: '브랜드', fields: [col('colors.red', '재능 레드', '엔딩 배경, 그룹 구체, 첫 장면 빛', g(45)), col('colors.ink', '진한 색 (예비)', '지금은 쓰지 않음', g(3))] },
  { tab: 'color', title: '사업 부문 색', fields: D.map((d, i) => col(`colors.d${i + 1}`, `${d.no} ${d.name}`, '부문 구체, 빛줄기, 지식맵', g(DS[i] + DL[i] - 1))) },
  { tab: 'color', title: '배경·글자', fields: [col('colors.night', '밤 배경', '대부분의 장면', g(13)), col('colors.paper', '밝은 배경 (예비)', '지금은 쓰지 않음', g(13)), col('colors.white', '흰색', '글자, 빛', g(17)), col('colors.muted', '회색 (예비)', '지금은 쓰지 않음', g(17))] },
 ],
 locked: '장면 순서와 길이, 계열사 수, 아이콘, 움직임, 음악은 고칠 수 없어요. 비트와 효과음이 장면 전환과 계열사 등장에 맞춰져 있어서예요.',
 warnings: ['배경음(CELEBRATION)은 사내용이에요. 외부 공개용은 라이선스 음원으로 바꿔야 해요.'],
};
})();
