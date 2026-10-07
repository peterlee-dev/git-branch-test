// Fields shown in the video editor (../video-editor.html). Rules: ../editor/PROTOCOL.md
(() => {
const TL = window.TL;
const sc = id => TL.scenes.find(s => s.id === id) || { start: 0 };
const col = (path, label, at) => ({ path, label, desc: '', type: 'color', at });
window.SCHEMA = {
 id: 'adaptive-diagnosis',
 title: 'Adaptive Diagnostic Assessment',
 duration: TL.duration, fps: 30,
 audio: ['audio/mix.wav', 'audio/mix.mp3'],
 audioFade: { in: 0, out: 1 },
 scenes: TL.scenes.map(s => ({ start: s.start, end: s.end, label: s.label })),
 sounds: [],
 tabs: [{ id: 'text', label: 'Text' }, { id: 'subs', label: 'Subtitles' }, { id: 'color', label: 'Colours' }],
 groups: [
  { tab: 'text', title: 'Title', at: 5, fields: [
   { path: 'title.main', label: 'Title', type: 'text' }, { path: 'title.sub', label: 'Subtitle', type: 'text' }, { path: 'title.team', label: 'Team / year', type: 'text' }] },
  { tab: 'text', title: 'Subjects (expected effects)', at: sc('effects').start + 30, fields: [0, 1, 2, 3].map(i => ({ path: `subjects.${i}`, label: `Subject ${i + 1}`, type: 'text' })) },
  ...TL.scenes.map(s => ({ tab: 'subs', title: s.label, note: 'Only the subtitle changes; the voice stays the same.',
   fields: TL.order.filter(id => TL.lines[id].scene === s.id).map(id => ({ path: `subs.${id}`, label: id, type: 'text', at: (TL.lines[id].start + TL.lines[id].end) / 2 })) })),
  { tab: 'color', title: 'Colours', fields: [col('colors.navy', 'Title text', 20), col('colors.blue', 'Main blue', 20), col('colors.orange', 'Incorrect / accent', 150), col('colors.green', 'Arrows', 40), col('colors.bg', 'Background', 20), col('colors.subBox', 'Subtitle box', 20)] },
 ],
 locked: 'Narration and animation timing cannot be edited here: every animation is keyed to a narration line. To change the script, edit SCRIPT in tools/make_audio.py and rerun it.',
 warnings: [],
};
})();
