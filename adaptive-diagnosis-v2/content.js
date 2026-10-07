// Adaptive Diagnostic Assessment v2 — on-screen text and colours (the video editor saves edits in this same shape, ../editor/PROTOCOL.md)
// subs: subtitle defaults come from timeline.js (shared narration with ../adaptive-diagnosis; editing a subtitle does not change the voice)
window.CONTENT = {
 "title": { "kicker": "SELF-LEARNING JEI MATH  ·  MATH ONLINE", "words": ["Adaptive", "Diagnostic", "Assessment"], "sub": "Development direction & expected benefits", "team": "2026  ·  Mathematics Team" },
 "colors": {
  "bg1": "#0A1330", "bg2": "#111F4A", "ink": "#EAF0FF", "dim": "#8E9CC4", "blue": "#4D8DFF", "cyan": "#5CE1E6",
  "orange": "#FF9147", "mint": "#43E0A0", "card": "#16264F", "cardLine": "#2A3D73"
 },
 "subs": Object.fromEntries(window.TL.order.map(id => [id, window.TL.lines[id].text]))
};
