// 한강 다리 산책 — 편집할 수 있는 색·세기 기본값. 영상 편집기(../video-editor.html)에서 고친 내용은 이 구조 그대로 JSON 으로 저장됨
// (render.mjs --project 파일.json 으로 그 JSON 을 렌더링). 규칙: ../editor/PROTOCOL.md
window.CONTENT = {
 "sky": {
  "zenith": "#1A2657",
  "mid": "#5C578F",
  "horizon": "#DB8F94",
  "sunHalo": "#FF8C40",
  "sunCore": "#FFC773",
  "cloudLit": "#FFA16B",
  "cloudShade": "#6B4D75",
  "cloudOpacity": 0.75,
  "cloudCover": 0.48,
  "fog": "#B98A9A"
 },
 "light": {
  "sun": "#FFB27A",
  "sunIntensity": 1.6,
  "skyFill": "#8C86C8",
  "groundFill": "#2A2238",
  "fillIntensity": 0.9
 },
 "lamps": {
  "light": "#FFC98E",
  "intensity": 22,
  "glow": "#FFD9A0",
  "halo": "#FFB870",
  "pool": "#FFD9A8"
 },
 "city": {
  "warmWindow": "#FFD08A",
  "coolWindow": "#DDE8FF",
  "windowBrightness": 0.95
 },
 "water": {
  "deep": "#0D0F1F",
  "glint": "#FFA85C",
  "glintStrength": 2.2
 },
 "film": {
  "bloom": 1,
  "warmTone": "#FFAA78",
  "warmAmount": 0.18,
  "shadowTint": "#D2D7F5",
  "vignette": 0.5,
  "grain": 1
 }
};
