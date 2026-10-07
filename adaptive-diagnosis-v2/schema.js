// Fields shown in the video editor (../video-editor.html). Rules: ../editor/PROTOCOL.md
(() => {
const TL = window.TL;
const col = (path, label, at) => ({ path, label, desc: '', type: 'color', at });
window.SCHEMA = {
 id: 'adaptive-diagnosis-v2',
 title: 'Adaptive Diagnostic Assessment v2',
 duration: TL.duration, fps: 30,
 audio: ['audio/mix.wav', 'audio/mix.mp3'],
 audioFade: { in: 0, out: 1 },
 scenes: TL.scenes.map(s => ({ start: s.start, end: s.end, label: s.label })),
 sounds: [],
 tabs: [{ id: 'text', label: 'Text' }, { id: 'subs', label: 'Subtitles' }, { id: 'color', label: 'Colours' }],
 groups: [
  { tab: 'text', title: 'Title', at: 6, fields: [
   { path: 'title.kicker', label: 'Kicker', type: 'text' }, { path: 'title.words.0', label: 'Title word 1', type: 'text' }, { path: 'title.words.1', label: 'Title word 2', type: 'text' }, { path: 'title.words.2', label: 'Title word 3', type: 'text' },
   { path: 'title.sub', label: 'Subtitle', type: 'text' }, { path: 'title.team', label: 'Team / year', type: 'text' }] },
  ...TL.scenes.map(s => ({ tab: 'subs', title: s.label, note: 'Only the subtitle changes; the voice stays the same.',
   fields: TL.order.filter(id => TL.lines[id].scene === s.id).map(id => ({ path: `subs.${id}`, label: id, type: 'text', at: (TL.lines[id].start + TL.lines[id].end) / 2 })) })),
  { tab: 'color', title: 'Colours', fields: [col('colors.bg1', 'Background top', 20), col('colors.bg2', 'Background bottom', 20), col('colors.cyan', 'Highlight', 20), col('colors.blue', 'Correct / main blue', 130), col('colors.orange', 'Incorrect', 130), col('colors.mint', 'Positive', 90)] },
 ],
 locked: 'Narration and timing are shared with ../adaptive-diagnosis (tools/sync_narration.sh). Every animation is keyed to a narration line.',
 warnings: [],
};
})();
