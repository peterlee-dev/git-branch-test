// 홍보 영상 문구·색 기본값. 영상 편집기(../video-editor.html)에서 고친 내용은 이 구조 그대로 JSON 으로 저장됨
// (render.mjs --project 파일.json 으로 그 JSON 을 렌더링). 규칙: ../editor/PROTOCOL.md
// 글자가 나오는 시각은 비트·효과음에 맞춰져 있어서 여기 없음 (index.html 에 고정)
window.CONTENT = {
 "colors": {
  "red": "#E60012",
  "black": "#0B0B0B",
  "char": "#141414",
  "paper": "#F4F2EF",
  "white": "#FFFFFF",
  "gray": "#8C8C8C",
  "ink": "#1A1A1A",
  "soft": "#CFCFCF",
  "url": "#8A8A8A"
 },
 "hud": { "brand": "JEI 재능교육", "since": "SINCE 1977" },
 "hook": { "line1": "AI 시대에도", "line2": "결국,", "accent": "스스로." },
 "history": {
  "label": "SINCE 1977",
  "yearFrom": 1977,
  "yearTo": 2027,
  "title1": "교육 한 길,",
  "title2": "50년.",
  "sub": "1981 재능산수로 시작한 스스로학습"
 },
 "system": {
  "label": "SELF-LEARNING SYSTEM",
  "rows": [
   { "a": "스스로", "b": "생각하고" },
   { "a": "스스로", "b": "풀고" },
   { "a": "스스로", "b": "자란다" }
  ],
  "sub": "개인별·능력별 스스로학습시스템"
 },
 "awards": {
  "label": "AWARDS 2026",
  "items": [
   { "n": 18, "unit": "년 연속", "title": "대한민국 퍼스트브랜드 대상", "brand": "스스로학습시스템", "org": "한국소비자포럼 · 학습지 부문" },
   { "n": 13, "unit": "년 연속", "title": "소비자 선정 최고의 브랜드 대상", "brand": "생각하는피자", "org": "중앙일보 · 포브스코리아 · 학습지 부문" }
  ]
 },
 "global": {
  "label": "GLOBAL JEI",
  "lead": "1992년 미국을 시작으로",
  "title": "세계로 뻗어가는 JEI",
  "countries": ["미국", "캐나다", "중국", "일본", "호주", "뉴질랜드"],
  "sub": "세계 곳곳의 아이들이 스스로학습으로 배우고 있어요"
 },
 "ending": { "brand": "재능교육", "slogan1": "AI 시대에도 결국,", "slogan2": "스스로.", "url": "jei.com" }
};
