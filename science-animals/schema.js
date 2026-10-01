// 영상 편집기(../video-editor.html)에 보여 줄 칸 설명. 규칙: ../editor/PROTOCOL.md
(() => {
const TL = window.TL, at = id => TL.lines[id].start + .8, sc = id => TL.scenes.find(s => s.id === id);
const J = "'Jua'";
window.SCHEMA = {
 id: 'science-animals',
 title: '동물 관찰 일기 (재능스스로과학 F01)',
 duration: TL.duration, fps: 30,
 audio: ['audio/mix.wav', 'audio/mix.mp3'],
 audioFade: { in: 0.3, out: 2 },
 scenes: TL.scenes.map(s => ({ start: s.start, end: s.end, label: s.label })),
 sounds: [{ t: TL.lines.a2.end + .5, label: '메뚜기 찾음' }, { t: TL.lines.c1.end + .05, label: '출발', big: true }, { t: TL.lines.z3.start, label: '참 잘했어요', big: true }],
 tabs: [{ id: 'text', label: '화면 글자' }, { id: 'subs', label: '자막' }, { id: 'color', label: '색' }],
 groups: [
  { tab: 'text', title: '타이틀', at: 3, fields: [
   { path: 'title.tag', label: '위쪽 태그', type: 'text' },
   { path: 'title.main', label: '제목', type: 'text', fit: { size: 170, family: J, max: 1000 } },
   ...[0, 1, 2, 3].map(i => ({ path: `title.topics.${i}`, label: `주제 ${i + 1}`, type: 'text', at: TL.lines.i2.end })) ] },
  { tab: 'text', title: '단원 제목 (왼쪽 위)', fields: [0, 1, 2, 3].map(i => ({ path: `heads.${i}`, label: `${i + 1}단원`, type: 'text', at: sc(['color', 'move', 'speed', 'need'][i]).start + 1.2 })) },
  { tab: 'text', title: '1. 몸 색깔과 생김새', fields: [
   { path: 'color.found', label: '메뚜기 찾았을 때', type: 'text', at: TL.lines.a2.end + 1 },
   { path: 'color.same', label: '메뚜기·청개구리', type: 'text', at: TL.lines.a3.end, fit: { size: 52, family: J, max: 1500 } },
   { path: 'color.hidden', label: '잘 보이지 않음', type: 'text', at: TL.lines.a4.end },
   { path: 'color.branch', label: '자벌레·대벌레', type: 'text', at: TL.lines.a5.end + .5 },
   { path: 'color.leaves', label: '나방', type: 'text', at: TL.lines.a6.end },
   { path: 'color.term', label: '낱말', type: 'text', at: TL.lines.a7.end },
   { path: 'color.termDesc', label: '뜻', type: 'textarea', at: TL.lines.a7.end },
   { path: 'color.fish', label: '고등어', type: 'text', at: TL.lines.a8.end }] },
  { tab: 'text', title: '2. 움직임', at: at('b6'), fields: ['legs', 'wings', 'fins', 'crawl', 'arms'].map(k => ({ path: `move.${k}`, label: k, type: 'text' })) },
  { tab: 'text', title: '3. 빠르기', fields: [
   { path: 'speed.start', label: '출발', type: 'text', at: TL.lines.c1.end + .3 }, { path: 'speed.finish', label: '결승', type: 'text', at: TL.lines.c1.end + .3 },
   { path: 'speed.faster', label: '캥거루 1', type: 'text', at: TL.lines.c4.end }, { path: 'speed.slower', label: '캥거루 2', type: 'text', at: TL.lines.c4.end },
   { path: 'speed.ostrich1', label: '타조 1', type: 'text', at: TL.lines.c5.end }, { path: 'speed.ostrich2', label: '타조 2', type: 'text', at: TL.lines.c5.end },
   { path: 'speed.differ', label: '빠르기 정리', type: 'text', at: TL.lines.c6.end },
   { path: 'speed.hunt', label: '사냥', type: 'text', at: TL.lines.c7.end }, { path: 'speed.escape', label: '도망', type: 'text', at: TL.lines.c7.end },
   { path: 'speed.rule', label: '이유 정리', type: 'text', at: TL.lines.c8.end, fit: { size: 48, family: J, max: 1700 } }] },
  { tab: 'text', title: '4. 필요한 것', fields: [
   ...[0, 1, 2, 3].map(i => ({ path: `need.items.${i}`, label: `필요한 것 ${i + 1}`, type: 'text', at: TL.lines.d2.end })),
   ...[0, 1, 2, 3].map(i => ({ path: `need.homes.${i}`, label: `집 ${i + 1}`, type: 'text', at: TL.lines[`d${6 + i}`].end })),
   { path: 'need.differ', label: '집 정리', type: 'text', at: TL.lines.d10.end }] },
  { tab: 'text', title: '정리', at: TL.lines.z3.end, fields: [
   ...[0, 1, 2, 3].map(i => ({ path: `end.lines.${i}`, label: `정리 ${i + 1}`, type: 'text', fit: { size: 52, family: J, max: 1180 } })),
   { path: 'end.stamp', label: '도장', type: 'text' }, { path: 'end.brand', label: '회사 이름', type: 'text' }] },
  ...TL.scenes.map(s => ({ tab: 'subs', title: s.label, at: s.start + .5,
   fields: TL.order.filter(id => TL.lines[id].scene === s.id).map(id => ({ path: `subs.${id}`, label: id, type: 'text', at: at(id) })) })),
  { tab: 'color', title: '바탕·종이', fields: [
   { path: 'colors.kraft', label: '크라프트지', type: 'color', at: 3 }, { path: 'colors.cream', label: '크림 종이', type: 'color', at: at('a3') },
   { path: 'colors.white', label: '흰 종이', type: 'color', at: at('a3') }, { path: 'colors.ink', label: '글자', type: 'color', at: at('a3') }] },
  { tab: 'color', title: '단원 색 (교재와 같게)', fields: [1, 2, 3, 4].map(i => ({ path: `colors.unit${i}`, label: `${i}단원`, type: 'color', at: sc(['color', 'move', 'speed', 'need'][i - 1]).start + 1.2 })) },
  { tab: 'color', title: '풍경', fields: [
   { path: 'colors.grass', label: '풀', type: 'color', at: at('a2') }, { path: 'colors.grassDark', label: '진한 풀', type: 'color', at: at('a2') }, { path: 'colors.grassLight', label: '연한 풀', type: 'color', at: at('a2') },
   { path: 'colors.sky', label: '하늘', type: 'color', at: at('a2') }, { path: 'colors.sea', label: '바다', type: 'color', at: at('a8') }, { path: 'colors.seaDark', label: '깊은 바다·고등어 등', type: 'color', at: at('a8') },
   { path: 'colors.leafFall', label: '낙엽', type: 'color', at: at('a6') }, { path: 'colors.brand', label: '재능교육 빨강', type: 'color', at: TL.lines.z3.end }] },
 ],
 locked: '장면 순서와 길이, 교재 사진, 움직임, 달리기 순서(치타 > 사자 > 캥거루 > 기린)는 고칠 수 없어요. 내레이션과 교재 내용에 맞춰져 있어서예요.',
 warnings: ['자막을 바꿔도 내레이션 음성은 그대로예요. 음성과 다른 말이 되지 않게 조심해 주세요.'],
};
})();
