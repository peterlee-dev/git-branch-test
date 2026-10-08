// Adaptive Diagnostic Assessment v2 — on-screen text and colours (the video editor saves edits in this same shape, ../editor/PROTOCOL.md)
// subs: subtitle defaults come from timeline.js (shared narration with ../adaptive-diagnosis; editing a subtitle does not change the voice)
window.CONTENT = {
 "title": { "kicker": "SELF-LEARNING JEI MATH  ·  MATH ONLINE", "words": ["Adaptive", "Diagnostic", "Assessment"], "sub": "Development direction & expected benefits", "team": "2026  ·  Mathematics Team" },
 "colors": {
  "paper": "#F7F9FC", "grid": "#E2E9F3", "ink": "#18264A", "muted": "#66748F",
  "blue": "#2B59E0", "pen": "#E0362C", "orange": "#EE8A23", "green": "#1D9A60", "teal": "#14A0A6", "subBox": "#18264A"
 },
 "subs": Object.fromEntries(window.TL.order.map(id => [id, window.TL.lines[id].text]))
};
