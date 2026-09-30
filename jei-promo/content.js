// 재능교육 50년 홍보 영상의 문구·색 기본값. 영상 편집기에서 고친 내용은 이 구조 그대로 JSON 으로 저장됨
// (render.mjs --project 파일.json 으로 그 JSON 을 렌더링). 규칙: ../editor/PROTOCOL.md
window.CONTENT = {
 "colors": {
  "black": "#0B0B0B",
  "char": "#141414",
  "red": "#E60012",
  "white": "#FFFFFF",
  "paper": "#F4F2EF",
  "gray": "#8C8C8C",
  "ink": "#1A1A1A",
  "introSub": "#D9D9D9",
  "colSub": "#6B6B6B",
  "habit": "#CFCFCF",
  "endSong": "#555555",
  "endFoot": "#8A8A8A"
 },
 "intro": { "title": "재능교육", "sub": "스스로 자라는 힘, 50년", "en": "JAENEUNG EDUCATION" },
 "years": {
  "label": "EDUCATION  ·  50 YEARS",
  "unit": "년",
  "copy1": ["반세기,", "오직 교육 한 길"],
  "copy2": ["교육업 50년,", "아이들의 배움에", "전념해 왔습니다"],
  "from": "1977",
  "to": "2027"
 },
 "self": {
  "label": "01  —  SELF-LEARNING",
  "title1": "스스로",
  "title2": "학습",
  "desc": "스스로 생각하고, 스스로 풀고, 스스로 자라는 힘",
  "cols": [
   { "n": "01", "title": "스스로 생각하고", "sub": "궁금한 것을 먼저 떠올리는 힘" },
   { "n": "02", "title": "스스로 풀고", "sub": "내 속도에 맞춰, 한 단계씩" },
   { "n": "03", "title": "스스로 자랍니다", "sub": "작은 성취가 쌓여 자신감으로" }
  ],
  "statement": "아이 스스로 답을 찾는 힘, 재능교육이 키웁니다."
 },
 "song": {
  "label": "02  —  ♪ 자기의 일은 스스로 하자",
  "words": ["자기의", "일은", "스스로", "하자"],
  "line1": "자기의 일은",
  "line2": "스스로 하자",
  "habit": "작은 습관이 평생의 힘이 됩니다."
 },
 "history": {
  "label": "03  —  HISTORY",
  "title": "50년의 발자취",
  "items": [
   { "y": "1977", "a": "㈜신영상역으로 창립", "b": "재능교육의 시작" },
   { "y": "1981", "a": "재능산수 출시", "b": "스스로학습의 출발" },
   { "y": "1992", "a": "미국 진출", "b": "세계로 뻗어가는 JEI" },
   { "y": "1998", "a": "생각하는피자 출시", "b": "종합 사고력 학습 프로그램" },
   { "y": "2027", "a": "창립 50주년", "b": "다시, 스스로" }
  ],
  "slogan1": "AI 시대에도 결국,",
  "slogan2": "스스로."
 },
 "ending": {
  "title": "재능교육",
  "sub": "스스로학습  ·  교육 50년",
  "song": "♪ 자기의 일은 스스로 하자",
  "foot": "JEI  ·  SINCE 1977"
 },
 "hud": {
  "brand": "JEI 재능교육",
  "since": "SINCE 1977",
  "sections": ["EDUCATION 50", "SELF-LEARNING", "OUR SONG", "HISTORY"]
 }
};
