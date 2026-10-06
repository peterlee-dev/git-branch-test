// 호박공주와 두리안 왕자 — 화면 글자·색 기본값 (영상 편집기에서 고친 내용은 이 구조 그대로 JSON 으로 저장됨, ../editor/PROTOCOL.md)
// 자막(subs) 기본값은 timeline.js 의 대사 (목소리는 바뀌지 않음)
window.CONTENT = {
 "title": window.TL.lang === 'en' ? { "main": "The Pumpkin Princess and Prince Durian", "sub": "A Fruit Land Fairy Tale", "end": "The End" } : { "main": "호박공주와 두리안 왕자", "sub": "과일 나라 동화", "end": "끝" },
 "tease": window.TL.lang === 'en' ? "Stripes don't make a pumpkin a watermelon!" : "호박에 줄 긋는다고 수박 되나?",
 "colors": {
  "sky": "#9ED8F5", "grass": "#9BD46B", "hedge": "#5FAE55", "castle": "#F7A23B", "room": "#FBD9E2",
  "pumpkin": "#F7A23B", "melon": "#6CC36A", "melonStripe": "#2F7D3A", "apple": "#EE4B4B", "grape": "#9A62C9",
  "banana": "#FFD84D", "berry": "#F2506B", "durian": "#C9CF55", "paint": "#3E9B4A",
  "subBox": "#FFFFFF", "ink": "#3A2E2A"
 },
 "subs": Object.fromEntries(window.TL.order.map(id => [id, window.TL.lines[id].text]))
};
