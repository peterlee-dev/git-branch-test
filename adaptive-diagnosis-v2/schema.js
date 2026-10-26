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
 tabs: [{ id: 'text', label: 'Text' }, { id: 'color', label: 'Colours' }],
 groups: [
  { tab: 'text', title: 'Title', at: 6, fields: [
   { path: 'title.kicker', label: 'Kicker', type: 'text' }, { path: 'title.words.0', label: 'Title word 1', type: 'text' }, { path: 'title.words.1', label: 'Title word 2', type: 'text' }, { path: 'title.words.2', label: 'Title word 3', type: 'text' },
   { path: 'title.sub', label: 'Subtitle', type: 'text' }, { path: 'title.team', label: 'Team / year', type: 'text' }] },
  { tab: 'color', title: 'Colours', fields: [col('colors.paper', 'Paper', 20), col('colors.grid', 'Graph-paper lines', 20), col('colors.ink', 'Ink (text)', 20), col('colors.red', "Main red: correct · up · teacher's pen", 130), col('colors.navy', 'Navy: incorrect · down', 130), col('colors.blue', 'Blue: 2nd of a comparison', 20), col('colors.mint', 'Mint: check this one', 130)] },
 ],
 locked: 'Narration: the recorded reading audio/narration.mp3, cut into lines and timed by tools/make_audio.py. Every animation is keyed to a narration line or a spoken word.',
 warnings: [],
};
})();
