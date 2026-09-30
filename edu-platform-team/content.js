// 홍보 영상 문구·색 기본값. 영상 편집기(../video-editor.html)에서 고친 내용은 이 구조 그대로 JSON 으로 저장됨
// (render.mjs --project 파일.json 으로 그 JSON 을 렌더링). 장면·박자 시각은 배경음에 묶여 있어서 여기 없음
window.CONTENT = {
 "colors": {
  "red": "#E60012",
  "yellow": "#FFC93C",
  "blue": "#3D7CFF",
  "mint": "#22CFA0",
  "pink": "#FF7AB6",
  "cream": "#FFF6EC",
  "ink": "#17151F",
  "white": "#FFFFFF",
  "purple": "#8B5CFF",
  "toggleOff": "#B00010"
 },
 "intro": { "hello": "Hello, World!", "we": "우리는", "team": "교육플랫폼팀!" },
 "pipeline": {
  "title1": "상상하면,", "title2": "만든다!",
  "nodes": ["연구원", "저작도구", "콘텐츠", "교육 서비스"],
  "tag": "우리가 만드는 것!",
  "caption": "콘텐츠 양산 파이프라인"
 },
 "authoring": {
  "title": "연구원을 위한 저작도구",
  "window": "수학 1-2 · 문항 만들기",
  "blocks": [
   { "label": "문제", "body": "18 + 25 = ?" },
   { "label": "보기", "body": "① 33   ② 43   ③ 53" },
   { "label": "정답", "body": "② 43" },
   { "label": "해설", "body": "8 + 5 = 13, 받아올림 1!" }
  ],
  "stamp": "발행!"
 },
 "scale": { "title1": "하나를 만들면", "title2": "모두에게!", "caption": "빠르게 · 정확하게 · 많이!" },
 "multi": {
  "web": "웹도!", "app": "앱도!",
  "screenTitle": "오늘의 스스로학습",
  "lessons": ["덧셈", "뺄셈", "수의 순서"],
  "caption": "하나의 코드로 어디서나!"
 },
 "ai": {
  "title1": "AI랑 같이,", "title2": "더 빠르게!",
  "prompt": "덧셈 문항 5개랑 해설 만들어 줘!",
  "cards": ["27 + 35", "48 + 16", "53 + 29", "66 + 18", "39 + 44"],
  "caption": "사람의 아이디어 + AI의 속도"
 },
 "ending": {
  "on": "ON", "off": "OFF", "passion": "열정",
  "line1": "교육의 미래를,", "line2": "코드로.",
  "team": "재능교육 교육플랫폼팀",
  "roles": "Frontend · Web & App · AI",
  "cta": "Let's build together!"
 }
};
