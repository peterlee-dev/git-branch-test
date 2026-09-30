// 영상 편집기(../video-editor.html)에 보여 줄 칸 설명. 규칙: ../editor/PROTOCOL.md
(() => {
const TL = window.TL, KR = "'Noto Sans KR'", EN = "'Inter'";
window.SCHEMA = {
 id: 'ai-math-trailer',
 title: '재능스스로AI수학 리뉴얼 예고편',
 duration: TL.duration, fps: 30,
 audio: ['audio/mix.wav', 'audio/mix.mp3'],
 audioFade: { in: 0.3, out: 2 },
 scenes: [
  { start: 0, end: 4.5, label: '암전 · 인트로', dark: true },
  { start: 4.5, end: TL.connect[0], label: '별이 하나씩 켜짐' },
  { start: TL.connect[0], end: TL.braam[0], label: '북두칠성 완성 · 보상' },
  { start: TL.braam[0], end: TL.ui[0], label: '그리고', dark: true },
  { start: TL.ui[0], end: TL.montage[0], label: '새 앱 화면 4장' },
  { start: TL.montage[0], end: TL.title, label: '몽타주' },
  { start: TL.title, end: TL.date, label: '타이틀' },
  { start: TL.date, end: TL.duration, label: '개봉일' },
 ],
 sounds: [
  ...TL.ignite.map(t => ({ t, label: '별 종소리' })),
  { t: TL.braam[0], label: '브람', big: true },
  ...TL.montage.map(t => ({ t, label: '째깍' })),
  { t: TL.title, label: '타이틀 타격', big: true },
  { t: TL.sting, label: '마지막 스팅', big: true },
 ],
 timed: {
  path: 'cards', label: '이야기 문구', textKey: 'text', startKey: 'start', endKey: 'end', minLen: 0.4,
  fields: [
   { key: 'text', label: '문구', type: 'text', fitFrom: { size: 'size', weight: 'weight', spacing: 'spacing' }, family: KR, max: 1660 },
   { key: 'start', label: '시작(초)', type: 'number', step: 0.1, min: 0, max: TL.duration },
   { key: 'end', label: '끝(초)', type: 'number', step: 0.1, min: 0, max: TL.duration },
   { key: 'size', label: '크기', type: 'number', step: 2, min: 16, max: 200 },
   { key: 'weight', label: '굵기', type: 'select', options: [100, 200, 300, 400, 500, 700, 900] },
   { key: 'y', label: '세로 위치(px)', type: 'number', step: 10, min: 160, max: 920 },
   { key: 'spacing', label: '자간', type: 'number', step: 1, min: 0, max: 60 },
  ],
 },
 tabs: [{ id: 'text', label: '문구' }, { id: 'app', label: '앱 화면' }, { id: 'color', label: '색' }],
 groups: [
  { tab: 'text', title: '별이 켜질 때 표기', at: TL.ignite[0] + .5, fields: [
   { path: 'lesson.day', label: '앞 글자 (예: DAY → DAY 01)', type: 'text' },
   { path: 'lesson.done', label: '설명', type: 'text' }] },
  { tab: 'text', title: '별자리 보상', at: 15, fields: [
   { path: 'reward.label', label: '작은 영문', type: 'text' },
   { path: 'reward.name', label: '별자리 이름', type: 'text', fit: { size: 36, weight: 300, family: KR, spacing: 14, max: 1700 } }] },
  ...[0, 1, 2, 3].map(i => ({ tab: 'text', title: `새 화면 ${i + 1}`, at: TL.ui[i] + 1, fields: [
   { path: `ui.${i}.sub`, label: '작은 영문', type: 'text' },
   { path: `ui.${i}.copy`, label: '문구', type: 'text', fit: { size: 56, weight: 300, family: KR, spacing: 3, max: 1600 } }] })),
  { tab: 'text', title: '몽타주 단어', at: TL.montage[1] + .05, columns: 2,
   fields: [0, 1, 2, 3, 4, 5, 6, 7].map(i => ({ path: `montage.${i}`, label: `${i + 1}번째`, type: 'text', at: TL.montage[i * 2 + 1] + .05 })) },
  { tab: 'text', title: '타이틀', at: TL.title + 3, fields: [
   { path: 'title.light', label: '가늘게 쓰는 부분', type: 'text', fit: { size: 140, weight: 200, family: KR, max: 860 } },
   { path: 'title.bold', label: '굵게 쓰는 부분', type: 'text', fit: { size: 140, weight: 800, family: KR, max: 860 } },
   { path: 'title.sub', label: '아래 영문', type: 'text' }] },
  { tab: 'text', title: '개봉일', at: TL.sting + 1.5, fields: [
   { path: 'date.main', label: '날짜', type: 'text', fit: { size: 170, weight: 100, family: EN, spacing: 24, max: 1780 } },
   { path: 'date.sub', label: '아래 문구', type: 'text' },
   { path: 'date.brand', label: '회사 이름', type: 'text' }] },
  { tab: 'app', title: '모든 앱 화면 공통', at: TL.ui[0] + 1, note: '앱 화면은 리뉴얼 방향을 보여 주는 가상 목업이에요. 실제 시안이 나오면 문구를 맞춰 넣으세요.', fields: [
   { path: 'app.name', label: '앱 이름 (왼쪽 위)', type: 'text' },
   { path: 'app.stars', label: '별 개수 (오른쪽 위)', type: 'text' }] },
  { tab: 'app', title: '홈', at: TL.ui[0] + 1, fields: [
   { path: 'app.homeGreeting', label: '인사말', type: 'text' },
   { path: 'app.homeProgress', label: '오늘의 학습 진행', type: 'text' },
   { path: 'app.lessons.0', label: '학습 1', type: 'text' }, { path: 'app.lessons.1', label: '학습 2', type: 'text' }, { path: 'app.lessons.2', label: '학습 3', type: 'text' }] },
  { tab: 'app', title: '문제 풀기 · AI 힌트', at: TL.ui[1] + 1, fields: [
   { path: 'app.problem', label: '문제', type: 'text' },
   { path: 'app.hint', label: 'AI 힌트', type: 'text' }] },
  { tab: 'app', title: '별자리 도감', at: TL.ui[2] + 1, fields: [
   { path: 'app.dexTitle', label: '제목', type: 'text' },
   ...[0, 1, 2, 3].map(i => ({ path: `app.dexNames.${i}`, label: `별자리 ${i + 1}`, type: 'text' }))] },
  { tab: 'app', title: '나의 성장', at: TL.ui[3] + 1, fields: [{ path: 'app.growthTitle', label: '제목', type: 'text' }] },
  { tab: 'color', title: '글자', fields: [
   { path: 'colors.accent', label: '강조 글자', desc: 'DAY 표기, 보상 영문, 리뉴얼 오픈', type: 'color', at: TL.sting + 1.5 },
   { path: 'colors.dim', label: '보조 글자', desc: '새 화면 영문, RENEWAL', type: 'color', at: TL.ui[0] + 1 }] },
  { tab: 'color', title: '빛', fields: [
   { path: 'colors.star', label: '별빛·별자리 선', desc: '켜진 별의 빛무리와 이어지는 선', type: 'color', at: 14.2 },
   { path: 'colors.flare', label: '렌즈 플레어', desc: '별이 켜질 때, 타이틀 뒤 빛', type: 'color', at: TL.title + .3 }] },
  { tab: 'color', title: '브랜드', fields: [
   { path: 'colors.app', label: '앱 강조색', desc: '앱 화면 안의 별·진행 막대', type: 'color', at: TL.ui[0] + 1 },
   { path: 'colors.brand', label: '재능교육 사각형', desc: '마지막 로고 옆', type: 'color', at: TL.sting + 1.5 }] },
 ],
 locked: '장면 순서와 길이, 카메라 움직임, 음악은 고칠 수 없어요. 음악의 타격음이 장면 전환에 맞춰져 있어서예요.',
};
})();
