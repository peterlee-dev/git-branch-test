// 영상 편집기(../video-editor.html)에 보여 줄 칸 설명. 규칙: ../editor/PROTOCOL.md
(() => {
const TL = window.TL, at = id => TL.lines[id].start + .6, sc = id => TL.scenes.find(s => s.id === id);
const FR = "'Fredoka'";
window.SCHEMA = {
 id: 'english-nouns',
 title: 'Nouns: One and More Than One',
 duration: TL.duration, fps: 30,
 audio: ['audio/mix.wav', 'audio/mix.mp3'],
 audioFade: { in: 0.3, out: 2 },
 scenes: TL.scenes.map(s => ({ start: s.start, end: s.end, label: s.label })),
 sounds: TL.order.filter(id => TL.lines[id].m).map(id => ({ t: TL.lines[id].m, label: TL.lines[id].text })),
 tabs: [{ id: 'text', label: '화면 글자' }, { id: 'subs', label: '자막' }, { id: 'color', label: '색' }],
 groups: [
  { tab: 'text', title: '타이틀', at: 2.5, fields: [
   { path: 'title.tag', label: '위쪽 태그', type: 'text' },
   { path: 'title.main', label: '제목', type: 'text', fit: { size: 230, weight: 700, family: FR, max: 1700 } },
   { path: 'title.sub', label: '부제', type: 'text', fit: { size: 64, weight: 600, family: FR, max: 1700 } }] },
  { tab: 'text', title: '장면 제목', fields: Object.keys(window.CONTENT.heads).map(k => ({ path: `heads.${k}`, label: sc(k).label, type: 'text', at: sc(k).start + 1, fit: { size: 56, weight: 600, family: FR, max: 1300 } })) },
  { tab: 'text', title: '표·이름표', at: at('a1'), fields: [
   { path: 'labels.people', label: 'People', type: 'text', at: at('n1') }, { path: 'labels.places', label: 'Places', type: 'text', at: at('n1') }, { path: 'labels.things', label: 'Things', type: 'text', at: at('n1') },
   { path: 'labels.one', label: '표 왼쪽 제목', type: 'text' }, { path: 'labels.more', label: '표 오른쪽 제목', type: 'text' },
   { path: 'labels.singular', label: '단수 이름표', type: 'text', at: at('s1') }, { path: 'labels.plural', label: '복수 이름표', type: 'text', at: at('s2') },
   { path: 'labels.but', label: 'boy · toy 상자 제목', type: 'text', at: at('c5') }, { path: 'labels.same', label: '같은 꼴 표시', type: 'text', at: at('f1') }] },
  { tab: 'text', title: '마무리', at: at('z2'), fields: [
   { path: 'end.main', label: '큰 글자', type: 'text', fit: { size: 170, weight: 700, family: FR, max: 1700 } },
   { path: 'end.sub', label: '아래 문구', type: 'text' }, { path: 'end.brand', label: '회사 이름', type: 'text' }] },
  ...TL.scenes.map(s => ({ tab: 'subs', title: s.label, at: s.start + .5,
   fields: TL.order.filter(id => TL.lines[id].scene === s.id).map(id => ({ path: `subs.${id}`, label: id, type: 'text', at: at(id), fit: { size: 40, weight: 400, family: "'Andika'", max: 1620 } })) })),
  { tab: 'color', title: '바탕', fields: [
   { path: 'colors.paper', label: '바탕', desc: '공책 점 무늬 뒤', type: 'color', at: at('a1') },
   { path: 'colors.panel', label: '가운데 판', type: 'color', at: at('a1') },
   { path: 'colors.border', label: '판 테두리', desc: '교재의 보라 테두리', type: 'color', at: at('a1') }] },
  { tab: 'color', title: '글자', fields: [
   { path: 'colors.ink', label: '본문 글자', type: 'color', at: at('a1') },
   { path: 'colors.blue', label: '제목·표 제목', type: 'color', at: at('a1') },
   { path: 'colors.orange', label: '강조', desc: '태그, 동그라미, 지금 줄', type: 'color', at: at('n7') },
   { path: 'colors.cyan', label: '붙는 글자', desc: '-s, -es 처럼 새로 붙는 끝', type: 'color', at: TL.lines.b1.m + .6 },
   { path: 'colors.red', label: '빠지는 글자', desc: 'y, f 처럼 빠지는 끝', type: 'color', at: TL.lines.c1.m + .1 }] },
 ],
 locked: '장면 순서와 길이, 예시 낱말, 움직임은 고칠 수 없어요. 내레이션 음성에 맞춰져 있어서예요. 낱말을 바꾸려면 tools/make_audio.py 의 문장을 고쳐 음성을 다시 만들어야 해요.',
 warnings: ['자막을 바꿔도 내레이션 음성은 그대로예요. 음성과 다른 말이 되지 않게 조심해 주세요.'],
};
})();
