// 지우의 형아 되기 — 화면 글자·색 기본값 (영상 편집기에서 고친 내용은 이 구조 그대로 JSON 으로 저장됨, ../editor/PROTOCOL.md)
// 자막(subs) 기본값은 timeline.js 의 대사 (목소리는 바뀌지 않음)
window.CONTENT = {
 "title": { "main": "지우의 형아 되기", "sub": "호기심 TV 이야기", "end": "끝" },
 "colors": {
  "wall": "#C9E7B0", "wallStripe": "#B5DC97", "floor": "#BBA6E2", "rug1": "#F6C85F", "rug2": "#F29F7C", "rug3": "#F7D9A0",
  "night": "#1E2350", "nightStripe": "#262C63",
  "jiwooShirt": "#4FA3E8", "jiwooPants": "#6B3F2E", "momTop": "#E8607A", "dadShirt": "#F6C26B", "babyOnesie": "#9B6BC4", "babyjOnesie": "#5DB0F0",
  "fairy": "#FF9FD6", "subBox": "#FFFFFF", "ink": "#3A2E2A"
 },
 "subs": Object.fromEntries(window.TL.order.map(id => [id, window.TL.lines[id].text]))
};
