// 화면 글자·색 기본값 (영상 편집기에서 고친 내용은 이 구조 그대로 JSON 으로 저장됨 — ../editor/PROTOCOL.md)
// 자막(subs) 기본값은 timeline.js 의 문장 (내레이션 음성은 바뀌지 않음)
window.CONTENT = {
 "colors": {
  "paper": "#FBFAF7",
  "panel": "#FFFFFF",
  "border": "#B9B3DE",
  "ink": "#2B2B33",
  "blue": "#2F6DB5",
  "orange": "#F39A3D",
  "cyan": "#1FA7DF",
  "red": "#E8505B"
 },
 "title": { "tag": "D01 · Nouns", "main": "Nouns", "sub": "One and More Than One" },
 "heads": {
  "noun": "What is a noun?",
  "sp": "One and more than one",
  "r1": "Add -s",
  "r2": "Add -es",
  "r3": "Change -y to -i, add -es",
  "r4": "Change -f to -v, add -es",
  "irr": "Irregular plurals",
  "same": "Same for one and many",
  "quiz": "Quiz time!"
 },
 "labels": {
  "people": "People", "places": "Places", "things": "Things",
  "one": "One (Singular)", "more": "More Than One (Plural)",
  "singular": "singular noun", "plural": "plural noun",
  "same": "same!", "but": "These words just add -s"
 },
 "end": { "main": "Great job!", "sub": "Look for nouns all around you!", "brand": "© JEI Corporation" },
 "subs": Object.fromEntries(window.TL.order.map(id => [id, window.TL.lines[id].text]))
};
