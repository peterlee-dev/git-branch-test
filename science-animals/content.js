// 화면 글자·색 기본값 (영상 편집기에서 고친 내용은 이 구조 그대로 JSON 으로 저장됨 — ../editor/PROTOCOL.md)
// 자막(subs) 기본값은 timeline.js 의 문장 (내레이션 음성은 바뀌지 않음)
window.CONTENT = {
 "colors": {
  "kraft": "#D8B98E",
  "cream": "#F6EEDC",
  "white": "#FFFDF7",
  "ink": "#3B2F2A",
  "unit1": "#B9A6E0",
  "unit2": "#9ACD6A",
  "unit3": "#F4B860",
  "unit4": "#F2A7C3",
  "grass": "#7DBF5A",
  "grassDark": "#4F9235",
  "grassLight": "#B4DB86",
  "sky": "#AFDAF2",
  "sea": "#5FA9DA",
  "seaDark": "#3E7FB8",
  "soil": "#9A6B45",
  "leafFall": "#D9893B",
  "brand": "#E60012"
 },
 "title": { "tag": "재능스스로과학 F01", "main": "동물 관찰 일기", "topics": ["몸 색깔", "움직임", "빠르기", "필요한 것"] },
 "heads": ["몸 색깔과 생김새", "동물의 움직임", "동물의 빠르기", "살아가는 데 필요한 것"],
 "color": {
  "found": "찾았다!",
  "same": "몸 색깔 ≈ 주위 환경의 색깔",
  "hidden": "다른 동물의 눈에 잘 보이지 않아요",
  "branch": "나뭇가지와 비슷해요",
  "leaves": "떨어진 낙엽과 비슷해요",
  "term": "보호색",
  "termDesc": "자신의 몸을 보호하기 위해 주위와 비슷하게 되어 있는 몸의 색깔",
  "fish": "위에서 보면 바다색과 비슷해요"
 },
 "move": { "legs": "다리", "wings": "날개", "fins": "지느러미", "crawl": "기어다니기", "arms": "팔과 다리" },
 "speed": {
  "start": "출발!", "finish": "결승",
  "faster": "기린보다 빨라요", "slower": "사자보다 느려요",
  "ostrich1": "날개가 있지만 날 수 없어요", "ostrich2": "길고 튼튼한 두 다리",
  "differ": "동물마다 빠르기가 각각 달라요",
  "hunt": "사냥", "escape": "도망", "rule": "적으로부터 도망치거나 · 사냥을 하기 위해"
 },
 "need": { "items": ["먹이", "물", "공기", "집"], "homes": ["땅속 굴", "나무 구멍 속 둥지", "진흙·지푸라기 둥지", "마른 풀 둥지"], "differ": "동물마다 사는 집이 각각 달라요" },
 "end": {
  "lines": ["보호색으로 몸을 숨겨요", "다리 · 날개 · 지느러미로 움직여요", "동물마다 빠르기가 달라요", "먹이 · 물 · 공기 · 집이 필요해요"],
  "stamp": "참 잘했어요", "brand": "재능교육"
 },
 "subs": Object.fromEntries(window.TL.order.map(id => [id, window.TL.lines[id].text]))
};
