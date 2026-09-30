// 밤하늘 별자리 여행 — 화면 문구·색 기본값. 영상 편집기(../video-editor.html)에서 고친 내용은 이 구조 그대로 JSON 으로 저장됨
// (render.mjs --project 파일.json 으로 그 JSON 을 렌더링). 규칙: ../editor/PROTOCOL.md
window.CONTENT = {
 "colors": {
  "ink": "#EAF0FF",
  "dim": "#D2DEFF",
  "faint": "#C8D7FF",
  "gold": "#FFD27A",
  "line": "#9FC4FF",
  "guide": "#FFD27A",
  "glow": "#8CB4FF",
  "sky": "#03050D",
  "brand": "#E60012"
 },
 "title": { "kicker": "CONSTELLATIONS", "main": "밤하늘 별자리 여행", "sub": "계절마다 달라지는 네 개의 이야기" },
 "panels": [
  { "season": "SPRING · 봄 · 북쪽 하늘", "name": "북두칠성", "sub": "큰곰자리의 꼬리 부분, 국자 모양 일곱 별", "fact": "국자 끝 두 별 간격을 5배 늘이면 북극성" },
  { "season": "AUTUMN · 가을 · 북쪽 하늘", "name": "카시오페이아자리", "sub": "W 모양으로 늘어선 다섯 별", "fact": "북극성을 사이에 두고 북두칠성과 마주 봐요" },
  { "season": "WINTER · 겨울 · 남쪽 하늘", "name": "오리온자리", "sub": "사냥꾼 오리온, 허리에 나란히 선 세 별", "fact": "붉은 베텔게우스와 푸른 리겔, 별마다 색이 달라요" },
  { "season": "SUMMER · 여름 · 머리 위 하늘", "name": "여름철 대삼각형", "sub": "베가 · 데네브 · 알타이르를 잇는 커다란 삼각형", "fact": "견우성과 직녀성 사이로 은하수가 흘러요" }
 ],
 "stars": {
  "dubhe": "두베", "merak": "메라크", "alkaid": "알카이드", "mizar": "미자르",
  "caph": "카프", "schedar": "시더", "navi": "나비", "ruchbah": "루크바", "segin": "세긴",
  "betelgeuse": "베텔게우스", "rigel": "리겔", "bellatrix": "벨라트릭스", "saiph": "사이프",
  "vega": "베가 (직녀성)", "deneb": "데네브", "altair": "알타이르 (견우성)"
 },
 "polaris": "북극성",
 "ending": { "main": "별자리로 읽는 계절의 하늘", "sub": "북두칠성 · 카시오페이아 · 오리온 · 여름철 대삼각형", "brand": "재능교육" }
};
