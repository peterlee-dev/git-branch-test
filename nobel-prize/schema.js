// 영상 편집기(../video-editor.html)에 보여 줄 칸. 규칙: ../editor/PROTOCOL.md
(() => {
const TL = window.TL;
const col = (path, label, at) => ({ path, label, desc: '', type: 'color', at });
const sc = id => TL.scenes.find(s => s.id === id);
const P = (k, label, at) => ({ tab: 'text', title: label, at, fields: [{ path: `people.${k}.name`, label: '이름', type: 'text' }, ...(k === 'nobel' || k === 'curie' ? [] : [{ path: `people.${k}.from`, label: '나라', type: 'text' }, { path: `people.${k}.prize`, label: '수상', type: 'text' }])] });
window.SCHEMA = {
 id: 'nobel-prize',
 title: '노벨상이 궁금해요',
 duration: TL.duration, fps: 30,
 audio: ['audio/mix.wav', 'audio/mix.mp3'],
 audioFade: { in: 0, out: 2 },
 scenes: TL.scenes.map(s => ({ start: s.start, end: s.end, label: s.label })),
 sounds: TL.sfx.map(c => ({ t: c.t, label: c.name })),
 tabs: [{ id: 'text', label: '글자' }, { id: 'subs', label: '자막' }, { id: 'color', label: '색' }],
 groups: [
  { tab: 'text', title: '제목', at: sc('title').start + 2, fields: [{ path: 'title.kicker', label: '시리즈 이름', type: 'text' }, { path: 'title.main', label: '제목', type: 'text' }] },
  P('einstein', '아인슈타인', 6), P('kim', '김대중', 6), P('dylan', '밥 딜런', 6), P('malala', '말랄라', 6), P('nobel', '노벨', 21), P('curie', '마리 퀴리', TL.lines.a2.end - 1),
  { tab: 'text', title: '분야', at: TL.lines.f2.end - .5, fields: [0, 1, 2, 3, 4, 5].map(i => ({ path: `fields.${i}`, label: `분야 ${i + 1}`, type: 'text' })) },
  ...TL.scenes.map(s => ({ tab: 'subs', title: s.label, note: '자막만 바뀌고 목소리는 그대로예요.',
   fields: TL.order.filter(id => TL.lines[id].scene === s.id).map(id => ({ path: `subs.${id}`, label: id, type: 'text', at: (TL.lines[id].start + TL.lines[id].end) / 2 })) })),
  { tab: 'color', title: '배경색', fields: [col('colors.sky', '하늘색', 30), col('colors.coral', '분홍', 5), col('colors.leaf', '연두', 5), col('colors.royal', '파랑', 5), col('colors.cream', '노랑', 5), col('colors.mustard', '겨자색', 80), col('colors.teal', '청록', 105), col('colors.lilac', '보라', 138)] },
  { tab: 'color', title: '글자·이름표', fields: [col('colors.ink', '글자', 38), col('colors.gold', '메달', 31), col('colors.chip', '이름표', 5), col('colors.subBox', '자막 상자', 5)] },
 ],
 locked: '내레이션과 시각은 tools/make_audio.py 에서 정해요. 움직임은 모두 내레이션 문장과 효과음 시각(TL.sfx)에 맞춰져 있어요.',
 warnings: [],
};
})();
