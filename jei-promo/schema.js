// 영상 편집기(../video-editor.html)에 보여 줄 칸 설명. 규칙: ../editor/PROTOCOL.md
(() => {
const KR = "'Noto Sans KR'", EN = "'Inter'";
const kr = (size, weight, max, spacing = 0) => ({ size, weight, family: KR, spacing, max });
const en = (size, weight, max, spacing = 0) => ({ size, weight, family: EN, spacing, max });
window.SCHEMA = {
 id: 'jei-promo',
 title: '재능교육 50년 홍보',
 duration: 60, fps: 30,
 audio: [],
 scenes: [
  { start: 0, end: 6, label: '인트로 · 재능교육', dark: true },
  { start: 6, end: 17, label: '교육 50년' },
  { start: 17, end: 33, label: '스스로학습' },
  { start: 33, end: 44.6, label: '자기의 일은 스스로 하자', dark: true },
  { start: 44.6, end: 53, label: '연혁', dark: true },
  { start: 53, end: 60, label: '엔딩' },
 ],
 tabs: [ { id: 'text', label: '문구' }, { id: 'history', label: '연혁' }, { id: 'color', label: '색' } ],
 groups: [
  { tab: 'text', title: '인트로', at: 4.5, fields: [
   { path: 'intro.title', label: '큰 제목', type: 'text', fit: kr(210, 900, 1700, -4) },
   { path: 'intro.sub', label: '부제', type: 'text', fit: kr(46, 500, 1700) },
   { path: 'intro.en', label: '영문 이름', type: 'text', fit: en(22, 600, 1700, 10) },
  ] },
  { tab: 'text', title: '교육 50년', at: 12, note: '오른쪽 문구는 1160px 지점에서 시작해서 한 줄이 짧아야 해요. 큰 숫자 00→50 카운터는 고칠 수 없어요.', fields: [
   { path: 'years.label', label: '위쪽 작은 영문', type: 'text', at: 8, fit: en(26, 600, 720, 8) },
   { path: 'years.unit', label: '숫자 옆 단위', type: 'text', at: 10 },
   { path: 'years.copy1.0', label: '첫 문구 1줄', type: 'text', at: 12, fit: kr(110, 900, 720) },
   { path: 'years.copy1.1', label: '첫 문구 2줄', type: 'text', at: 12, fit: kr(110, 900, 720) },
   { path: 'years.copy2.0', label: '둘째 문구 1줄', type: 'text', at: 15.5, fit: kr(92, 900, 720) },
   { path: 'years.copy2.1', label: '둘째 문구 2줄', type: 'text', at: 15.5, fit: kr(92, 900, 720) },
   { path: 'years.copy2.2', label: '둘째 문구 3줄 (검은 글자)', type: 'text', at: 15.5, fit: kr(92, 900, 720) },
   { path: 'years.from', label: '트랙 시작 연도', type: 'text', at: 10 },
   { path: 'years.to', label: '트랙 끝 연도', type: 'text', at: 10 },
  ] },
  { tab: 'text', title: '스스로학습', at: 28, fields: [
   { path: 'self.label', label: '위쪽 작은 영문', type: 'text', fit: en(24, 600, 1600, 8) },
   { path: 'self.title1', label: '제목 앞 (검은 글자)', type: 'text', at: 19, fit: kr(280, 900, 950, -6) },
   { path: 'self.title2', label: '제목 뒤 (빨간 글자)', type: 'text', at: 19, fit: kr(280, 900, 700, -6) },
   { path: 'self.desc', label: '제목 옆 설명', type: 'text', fit: kr(34, 500, 1080) },
   { path: 'self.statement', label: '아래 한 줄', type: 'text', fit: kr(50, 700, 1650) },
  ] },
  ...[0, 1, 2].map(i => ({ tab: 'text', title: `스스로학습 ${i + 1}번째 칸`, at: 28, columns: 2, fields: [
   { path: `self.cols.${i}.n`, label: '번호', type: 'text' },
   { path: `self.cols.${i}.title`, label: '제목', type: 'text', fit: kr(58, 900, 500) },
   { path: `self.cols.${i}.sub`, label: '설명', type: 'text', fit: kr(30, 500, 500) },
  ] })),
  { tab: 'text', title: '노래 가사', at: 43, note: '가사 네 단어는 한 단어씩 크게 나오고, 뒤쪽 계단 아래 이름표로도 쓰여요. 세 번째 단어 뒤에 빨간 박스가 깔려요.', fields: [
   { path: 'song.label', label: '위쪽 작은 제목', type: 'text', at: 36, fit: kr(26, 600, 1600, 3) },
   { path: 'song.words.0', label: '가사 1', type: 'text', at: 34.2, fit: kr(330, 900, 1800, -8) },
   { path: 'song.words.1', label: '가사 2', type: 'text', at: 35.4, fit: kr(330, 900, 1800, -8) },
   { path: 'song.words.2', label: '가사 3 (빨간 박스)', type: 'text', at: 36.6, fit: kr(330, 900, 1680, -8) },
   { path: 'song.words.3', label: '가사 4', type: 'text', at: 37.8, fit: kr(330, 900, 1800, -8) },
   { path: 'song.line1', label: '문장 1줄 (흰 글자)', type: 'text', fit: kr(150, 900, 880, -4) },
   { path: 'song.line2', label: '문장 2줄 (빨간 글자)', type: 'text', fit: kr(150, 900, 880, -4) },
   { path: 'song.habit', label: '아래 한 줄', type: 'text', fit: kr(46, 500, 880) },
  ] },
  { tab: 'history', title: '연혁 제목', at: 51.5, fields: [
   { path: 'history.label', label: '위쪽 작은 영문', type: 'text', fit: en(24, 600, 1600, 8) },
   { path: 'history.title', label: '제목', type: 'text', fit: kr(104, 900, 1600) },
   { path: 'history.slogan1', label: '슬로건 앞 (흰 글자)', type: 'text', fit: kr(76, 900, 1300) },
   { path: 'history.slogan2', label: '슬로건 뒤 (빨간 글자)', type: 'text', fit: kr(76, 900, 300) },
  ] },
  ...[0, 1, 2, 3, 4].map(i => ({ tab: 'history', title: `연혁 ${i + 1}${i === 4 ? ' (빨간 점)' : ''}`, at: 51.5, columns: 2,
   note: i === 0 ? '칸 사이가 370px라서 설명은 짧게 써 주세요. 실제 연혁과 맞는지 꼭 확인해 주세요.' : undefined, fields: [
   { path: `history.items.${i}.y`, label: '연도', type: 'text', fit: en(64, 800, 350) },
   { path: `history.items.${i}.a`, label: '내용', type: 'text', fit: kr(34, 700, 350) },
   { path: `history.items.${i}.b`, label: '작은 설명', type: 'text', fit: kr(24, 500, 350) },
  ] })),
  { tab: 'text', title: '엔딩', at: 57.5, fields: [
   { path: 'ending.title', label: '큰 제목', type: 'text', fit: kr(220, 900, 1700, -4) },
   { path: 'ending.sub', label: '빨간 부제', type: 'text', fit: kr(52, 700, 1700) },
   { path: 'ending.song', label: '노래 제목', type: 'text', fit: kr(34, 500, 1700) },
   { path: 'ending.foot', label: '맨 아래 영문', type: 'text', fit: en(20, 600, 1700, 8) },
  ] },
  { tab: 'text', title: '위·아래 테두리 글자', at: 10, note: '6초부터 52초까지 화면 네 귀퉁이에 떠 있는 글자예요.', fields: [
   { path: 'hud.brand', label: '왼쪽 위', type: 'text' },
   { path: 'hud.since', label: '오른쪽 위', type: 'text' },
   { path: 'hud.sections.0', label: '구간 이름 · 교육 50년', type: 'text', at: 10 },
   { path: 'hud.sections.1', label: '구간 이름 · 스스로학습', type: 'text', at: 25 },
   { path: 'hud.sections.2', label: '구간 이름 · 노래', type: 'text', at: 40 },
   { path: 'hud.sections.3', label: '구간 이름 · 연혁', type: 'text', at: 48 },
  ] },
  { tab: 'color', title: '브랜드 색', columns: 2, fields: [
   { path: 'colors.red', label: '레드', desc: '로고 마크, 50년 장면 배경, 강조 글자, 점과 선', type: 'color', at: 10 },
   { path: 'colors.black', label: '블랙', desc: '인트로·노래 장면 배경, 밝은 장면의 글자', type: 'color', at: 3 },
   { path: 'colors.white', label: '화이트', desc: '어두운 장면의 글자와 선', type: 'color', at: 4.5 },
   { path: 'colors.paper', label: '종이색', desc: '스스로학습·엔딩 장면 배경', type: 'color', at: 25 },
   { path: 'colors.char', label: '짙은 회색', desc: '연혁 장면 배경', type: 'color', at: 48 },
   { path: 'colors.gray', label: '회색', desc: '연혁 작은 설명, 계단 이름표', type: 'color', at: 48 },
  ] },
  { tab: 'color', title: '보조 글자 색', columns: 2, fields: [
   { path: 'colors.introSub', label: '인트로 부제', type: 'color', at: 4.5 },
   { path: 'colors.ink', label: '스스로학습 제목 옆 설명', type: 'color', at: 23 },
   { path: 'colors.colSub', label: '스스로학습 칸 설명', type: 'color', at: 28 },
   { path: 'colors.habit', label: '노래 장면 아래 한 줄', type: 'color', at: 43 },
   { path: 'colors.endSong', label: '엔딩 노래 제목', type: 'color', at: 57.5 },
   { path: 'colors.endFoot', label: '엔딩 맨 아래 영문', type: 'color', at: 57.5 },
  ] },
 ],
 locked: '장면 길이와 순서, 글자가 나오고 들어가는 시각, 00→50 숫자 카운터, 아이콘과 계단 움직임은 고칠 수 없어요. 글자들이 정해진 박자에 맞춰 차례로 밀려 올라오도록 짜여 있고, 나중에 넣을 노래에도 맞춰야 해서예요.',
 warnings: ['연혁 연도와 내용은 회사 공식 자료와 맞는지 확인하고 고쳐 주세요.', '가사를 바꿔도 나중에 넣는 노래 「자기의 일은 스스로 하자」는 그대로예요.'],
};
})();
