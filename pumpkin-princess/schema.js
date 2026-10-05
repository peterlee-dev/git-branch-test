// 영상 편집기(../video-editor.html)에 보여 줄 칸 설명. 규칙: ../editor/PROTOCOL.md
(() => {
const TL = window.TL, J = "'Jua'";
const sc = id => TL.scenes.find(s => s.id === id) || { start: 0 };
const ln = id => TL.lines[id] || { start: 0, end: 0 };
const col = (path, label, at) => ({ path, label, desc: '', type: 'color', at });
window.SCHEMA = {
 id: 'pumpkin-princess',
 title: '호박공주와 두리안 왕자',
 duration: TL.duration, fps: 30,
 audio: ['audio/mix.wav', 'audio/mix.mp3'],
 audioFade: { in: 0, out: 1 },
 scenes: TL.scenes.map(s => ({ start: s.start, end: s.end, label: s.label, dark: s.id === 'rain' })),
 sounds: [{ t: ln('n4').end, label: '팡파르', big: true }, { t: ln('p6').start, label: '짜잔' }, { t: ln('n9').start + .2, label: '천둥', big: true }, { t: ln('n13').start + .6, label: '무지개' }, { t: sc('wedding').start + .3, label: '종소리', big: true }],
 tabs: [{ id: 'text', label: '제목' }, { id: 'subs', label: '자막' }, { id: 'color', label: '색' }],
 groups: [
  { tab: 'text', title: '제목', at: 1, fields: [
   { path: 'title.main', label: '제목', type: 'text', fit: { size: 130, family: J, max: 1700 } },
   { path: 'title.sub', label: '제목 위 작은 글', type: 'text' },
   { path: 'title.end', label: '마지막 글', type: 'text', at: TL.duration - 2 }] },
  ...TL.scenes.map(s => ({ tab: 'subs', title: s.label, note: '자막만 바뀌고 목소리는 그대로예요.',
   fields: TL.order.filter(id => TL.lines[id].scene === s.id).map(id => ({ path: `subs.${id}`, label: (TL.lines[id].name || '내레이션'), type: 'text', at: (TL.lines[id].start + TL.lines[id].end) / 2, fit: { size: 46, family: J, max: 1420 } })) })),
  { tab: 'color', title: '배경', fields: [col('colors.sky', '하늘', 10), col('colors.grass', '잔디', 10), col('colors.hedge', '울타리 나무', 10), col('colors.castle', '호박 성', 5), col('colors.room', '공주 방 벽', sc('paint').start + 3)] },
  { tab: 'color', title: '캐릭터', fields: [col('colors.pumpkin', '호박공주', 10), col('colors.melon', '수박공주', sc('party').start + 12), col('colors.melonStripe', '수박 줄무늬', sc('party').start + 12), col('colors.apple', '사과 왕자', sc('party').start + 6), col('colors.grape', '포도 왕자', sc('party').start + 6), col('colors.banana', '바나나', sc('party').start + 6), col('colors.berry', '딸기', sc('party').start + 6), col('colors.durian', '두리안 왕자', sc('durian').start + 8), col('colors.paint', '그린 줄무늬 물감', sc('paint').start + 8)] },
  { tab: 'color', title: '자막', fields: [col('colors.subBox', '자막 상자', 10), col('colors.ink', '자막 글자', 10)] },
 ],
 locked: '이야기 순서, 대사 음성, 캐릭터 움직임은 고칠 수 없어요. 목소리 길이에 맞춰 움직임이 짜여 있어서예요. 대사를 바꾸려면 tools/make_audio.py 의 SCRIPT 를 고치고 다시 만들어요.',
 warnings: [],
};
})();
