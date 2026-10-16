// 노벨상이 궁금해요 — 화면 글자와 색 (영상 편집기도 같은 모양으로 저장해요, ../editor/PROTOCOL.md)
// subs: 자막 기본값은 timeline.js 에서 와요 (자막을 고쳐도 목소리는 그대로예요)
window.CONTENT = {
 "title": { "kicker": "지식 한 스푼", "main": "노벨상이 궁금해요!" },
 "people": {
  "einstein": { "name": "아인슈타인", "from": "독일", "prize": "물리학상 1921" },
  "kim": { "name": "김대중", "from": "대한민국", "prize": "평화상 2000" },
  "dylan": { "name": "밥 딜런", "from": "미국", "prize": "문학상 2016" },
  "malala": { "name": "말랄라 유사프자이", "from": "파키스탄", "prize": "평화상 2014" },
  "nobel": { "name": "알프레드 노벨" },
  "curie": { "name": "마리 퀴리" }
 },
 "fields": ["물리학", "화학", "생리학·의학", "문학", "평화", "경제학"],
 "colors": {
  "sky": "#7CC4F4", "coral": "#F27585", "leaf": "#B5D98B", "royal": "#6A8FDE", "cream": "#FCEFA6", "mustard": "#DDA94B",
  "teal": "#45B8D8", "lilac": "#B9A7E3", "ink": "#2C2F45", "gold": "#F5C431", "chip": "#7DC243", "subBox": "#1E2238"
 },
 "subs": Object.fromEntries(window.TL.order.map(id => [id, window.TL.lines[id].text]))
};
