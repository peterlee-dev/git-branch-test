// Adaptive Diagnostic Assessment — on-screen text and colours (the video editor saves edits in this same shape, ../editor/PROTOCOL.md)
// subs: subtitle defaults come from timeline.js (editing a subtitle does not change the voice)
window.CONTENT = {
 "title": { "main": "Adaptive Diagnostic Assessment", "sub": "development direction and expected benefits", "team": "2026 | Mathematics Team" },
 "subjects": ["JEI Math", "English", "Korean", "Science"],
 "colors": {
  "navy": "#14285A", "blue": "#2563EB", "blueDark": "#0B3AA8", "blueSoft": "#E3ECFF", "orange": "#F2742B", "red": "#E5484D",
  "green": "#22A45D", "gray": "#6B7690", "line": "#E1E7F2", "bg": "#EEF3FC", "subBox": "#14285A"
 },
 "subs": Object.fromEntries(window.TL.order.map(id => [id, window.TL.lines[id].text]))
};
