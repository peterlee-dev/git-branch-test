// 예고편 문구·색 기본값. editor.html 에서 고친 내용은 이 구조 그대로 JSON 으로 저장됨
// (render.mjs --project 파일.json 으로 그 JSON 을 렌더링)
window.CONTENT = {
 "colors": {
  "accent": "#ECE4D2",
  "dim": "#DCE2F0",
  "star": "#F2E6CC",
  "flare": "#C9D6EE",
  "app": "#FFD37A",
  "brand": "#E60012"
 },
 "cards": [
  { "id": "intro",  "text": "재능교육이 선보이는",   "start": 0.8,  "end": 4.1,  "y": 540, "size": 40, "weight": 300, "spacing": 18 },
  { "id": "story1", "text": "하루의 학습이",         "start": 5.6,  "end": 10.8, "y": 300, "size": 58, "weight": 200, "spacing": 14 },
  { "id": "story2", "text": "하나의 별이 되고",      "start": 7.6,  "end": 10.8, "y": 390, "size": 58, "weight": 200, "spacing": 14 },
  { "id": "story3", "text": "쌓인 별은",             "start": 11.4, "end": 16.6, "y": 300, "size": 58, "weight": 200, "spacing": 14 },
  { "id": "story4", "text": "나만의 별자리가 된다",  "start": 12.6, "end": 16.6, "y": 390, "size": 58, "weight": 400, "spacing": 14 },
  { "id": "and",    "text": "그리고,",               "start": 17.4, "end": 18.9, "y": 540, "size": 60, "weight": 200, "spacing": 20 }
 ],
 "lesson": { "day": "DAY", "done": "학습 완료" },
 "reward": { "label": "CONSTELLATION UNLOCKED", "name": "북두칠성" },
 "ui": [
  { "sub": "NEW UI",               "copy": "완전히 새로워진 화면" },
  { "sub": "AI HINT",              "copy": "AI가 곁에서 힌트를" },
  { "sub": "CONSTELLATION REWARD", "copy": "모으는 재미, 별자리 도감" },
  { "sub": "MY GROWTH",            "copy": "한눈에 보는 나의 성장" }
 ],
 "montage": ["스스로", "생각하고", "도전하고", "빛나는", "매일", "스스로", "AI", "수학"],
 "title": { "light": "재능스스로", "bold": "AI수학", "sub": "RENEWAL" },
 "date": { "main": "2026. 12", "sub": "리뉴얼 오픈", "brand": "재능교육" },
 "app": {
  "name": "재능스스로AI수학",
  "stars": "128",
  "homeGreeting": "오늘도 반짝여 볼까요?",
  "homeProgress": "3 / 5",
  "lessons": ["덧셈과 뺄셈", "100까지의 수", "시계 보기"],
  "problem": "18 + 25 = ?",
  "hint": "AI 힌트: 일의 자리부터 더해 볼까요? 8 + 5 = 13",
  "dexTitle": "모은 별자리 4 / 12",
  "dexNames": ["북두칠성", "카시오페이아", "오리온", "백조"],
  "growthTitle": "이번 주, 이만큼 자랐어요"
 }
};
