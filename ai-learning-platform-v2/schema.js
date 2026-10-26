// Fields shown in the video editor (../video-editor.html). Rules: ../editor/PROTOCOL.md
(() => {
const TL = window.TL;
const col = (path, label, at) => ({ path, label, desc: '', type: 'color', at });
const sceneAt = (id, d = 3) => { const s = TL.scenes.find(x => x.id === id); return s ? s.start + d : 0; };
window.SCHEMA = {
 id: 'ai-learning-platform-v2',
 title: 'JEI Math: AI-Powered Personalized Learning Platform v2',
 duration: TL.duration, fps: 30,
 audio: ['audio/mix.wav', 'audio/mix.mp3'],
 audioFade: { in: 0.3, out: 2 },
 scenes: TL.scenes.map(s => ({ start: s.start, end: s.end, label: s.label })),
 sounds: [],
 tabs: [{ id: 'text', label: 'Text' }, { id: 'color', label: 'Colours' }],
 groups: [
  { tab: 'text', title: 'Title', at: 5, fields: [
   { path: 'title.kicker', label: 'Kicker', type: 'text' }, { path: 'title.words.0', label: 'Title line 1', type: 'text' }, { path: 'title.words.1', label: 'Title line 2', type: 'text' }, { path: 'title.words.2', label: 'Title line 3', type: 'text' },
   { path: 'title.sub', label: 'Subtitle', type: 'text' }, { path: 'title.team', label: 'Team', type: 'text' }] },
  { tab: 'text', title: 'Closing', at: sceneAt('outro', 6), fields: [
   { path: 'outro.line1', label: 'Line 1', type: 'text' }, { path: 'outro.line2', label: 'Line 2 (handwriting)', type: 'text' }, { path: 'outro.thanks', label: 'Thank you', type: 'text' }] },
  { tab: 'color', title: 'Main colours', fields: [col('colors.red', 'Red — main · positive · 1st of a comparison · pen', 20), col('colors.blue', 'Blue — 2nd of a comparison (Phase 2)', sceneAt('phases', 10)), col('colors.mint', 'Mint — 3rd · to check (needs practice)', sceneAt('status', 30)),
   col('colors.navy', 'Navy — negative · gap', sceneAt('status', 30)), col('colors.ink', 'Text', 20), col('colors.paper', 'Background', 20)] },
  { tab: 'color', title: 'Sub colours', fields: [col('colors.mintDark', 'Mint dark (text · white-text chips)', sceneAt('phases', 40)), col('colors.crimson', 'Crimson (small red text)', sceneAt('build', 30)), col('colors.lightRed', 'Light red', sceneAt('layers', 10)),
   col('colors.blush', 'Blush (highlighter)', 5), col('colors.redTint', 'Red tint', sceneAt('roadmap', 30)), col('colors.blueTint', 'Blue tint', sceneAt('roadmap', 30)), col('colors.mintTint', 'Mint tint', sceneAt('status', 20)),
   col('colors.muted', 'Slate (secondary text)', 20), col('colors.midGrey', 'Mid grey (not yet studied)', sceneAt('status', 30)), col('colors.lineGrey', 'Line grey (outlines)', sceneAt('kmap', 20)), col('colors.lightBox', 'Light box (secondary boxes)', sceneAt('kmap', 20)), col('colors.grid', 'Graph-paper lines', 20), col('colors.gridMajor', 'Graph-paper lines (every 5th)', 20), col('colors.margin', 'Left margin line', 20)] },
 ],
 locked: 'Narration: Qwen3-TTS clone of audio/voice_ref.wav, one line at a time (tools/make_audio.py). Every animation is keyed to a narration line or a spoken word.',
 warnings: [],
};
})();
