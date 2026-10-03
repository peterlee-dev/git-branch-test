// 영상 편집기(../video-editor.html)에 보여 줄 칸 설명. 규칙: ../editor/PROTOCOL.md
(() => {
const TL = window.TL, J = "'Jua'";
const sc = id => TL.scenes.find(s => s.id === id) || { start: 0 };
const ln = id => TL.lines[id] || { start: 0, end: 0 };
const col = (path, label, desc, at) => ({ path, label, desc, type: 'color', at });
window.SCHEMA = {
 id: 'jiwoo-big-brother',
 title: '지우의 형아 되기',
 duration: TL.duration, fps: 30,
 audio: ['audio/mix.wav', 'audio/mix.mp3'],
 audioFade: { in: 0, out: 1 },
 scenes: TL.scenes.map(s => ({ start: s.start, end: s.end, label: s.label, dark: s.id === 'night' || s.id === 'back' })),
 sounds: [{ t: ln('f3').end, label: '아기가 되어라', big: true }, { t: ln('j10').end + .15, label: '콩' }, { t: ln('f5').end, label: '형아로', big: true }, { t: ln('b4').start, label: '까르르' }],
 tabs: [{ id: 'text', label: '제목' }, { id: 'subs', label: '자막' }, { id: 'color', label: '색' }],
 groups: [
  { tab: 'text', title: '제목', at: .8, fields: [
   { path: 'title.main', label: '제목', type: 'text', fit: { size: 150, family: J, max: 1700 } },
   { path: 'title.sub', label: '제목 위 작은 글', type: 'text' }] },
  ...TL.scenes.map(s => ({ tab: 'subs', title: s.label, note: s.id === 'baby' ? '자막만 바뀌고 목소리는 그대로예요.' : undefined,
   fields: TL.order.filter(id => TL.lines[id].scene === s.id).map(id => ({ path: `subs.${id}`, label: (TL.lines[id].name || '내레이션'), type: 'text', at: (TL.lines[id].start + TL.lines[id].end) / 2, fit: { size: 46, family: J, max: 1420 } })) })),
  { tab: 'color', title: '거실', fields: [col('colors.wall', '벽', '', 10), col('colors.wallStripe', '벽 줄무늬', '', 10), col('colors.floor', '바닥', '', 10), col('colors.rug1', '러그 1', '', 10), col('colors.rug2', '러그 2', '', 10), col('colors.rug3', '러그 3', '', 10)] },
  { tab: 'color', title: '밤', fields: [col('colors.night', '밤 벽', '', sc('night').start + 4), col('colors.nightStripe', '밤 벽 줄무늬', '', sc('night').start + 4)] },
  { tab: 'color', title: '옷', fields: [col('colors.jiwooShirt', '지우 티셔츠', '', 10), col('colors.jiwooPants', '지우 바지', '', 10), col('colors.momTop', '엄마 윗옷', '', 10), col('colors.dadShirt', '아빠 셔츠', '', 10), col('colors.babyOnesie', '동생 우주복', '', 10), col('colors.babyjOnesie', '아기 지우 우주복', '', sc('baby').start + 3), col('colors.fairy', '요정 드레스', '', sc('night').start + 6)] },
  { tab: 'color', title: '자막', fields: [col('colors.subBox', '자막 상자', '', 10), col('colors.ink', '자막 글자', '', 10)] },
 ],
 locked: '이야기 순서, 대사 음성, 캐릭터 움직임은 고칠 수 없어요. 목소리 길이에 맞춰 움직임이 짜여 있어서예요. 대사를 바꾸려면 tools/make_audio.py 의 SCRIPT 를 고치고 다시 만들어요.',
 warnings: [],
};
})();
