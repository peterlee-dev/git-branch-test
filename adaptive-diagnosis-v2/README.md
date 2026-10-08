# Adaptive Diagnostic Assessment — v2 (모눈종이 워크북)

`../adaptive-diagnosis`와 **같은 내레이션(받은 음성 샘플을 복제한 Qwen3-TTS)과 같은 시각표**를 쓰고, 화면은 `../math-di-improvement-v2`와 같은 콘셉트로 새로 그린 버전이에요. 기존 장표 버전(v1)은 그대로 두었어요. 이전의 밤하늘 버전은 git 기록(`8e14945`)에 남아 있어요.

- **모눈종이 워크북 한 장**: 장면마다 한 쪽(p. 1 ~ p. 12). 장면이 바뀔 때 종이 위를 옆으로 넘어가고(믹스의 휙 소리와 같은 때), 읽는 동안은 화면이 움직이지 않아요(카메라 줌 없음)
- 선생님 펜 표시: 빨간 동그라미·체크·가위표·밑줄, 형광펜, 도장(UNDERSTOOD / NOT UNDERSTOOD)
- 되풀이되는 그림: **난이도 사다리 1~9** — 맞히면 위로, 틀리면 아래로
- 1920×1080, 30fps. 글꼴은 macOS 시스템 글꼴 Avenir Next(본문)·Noteworthy(손글씨), 한글은 Noto Sans KR로 대신 그려요. 배경음악 없음 (내레이션 + 정답·오답·장면 전환 효과음)
- 자막은 아래쪽 남색 상자

| p. | 장면 | 구성 |
|---|---|---|
| 1 | Title | 제목 형광펜, 선생님이 채점하는 진단 시험지(4 / 6) |
| 2 | What is a diagnostic assessment? | 1 ASSESS → 2 DIAGNOSE → 3 PRESCRIBE 카드 |
| 3 | The problem today | 쌓이는 문제지와 91문항 카운터, 정확도↑ BUT 부담↑, 효율↓ 막대 |
| 4 | Adaptive Diagnostic Assessment | 펜으로 자라는 분기 나무: 맞으면 위(파랑 ✓), 틀리면 아래(주황 ✗) |
| 5 | Only the questions that matter | 20문항 문제지에서 5문항만 동그라미, 나머지 가위표, 20 → 5 |
| 6 | What it improves | 효율·신뢰도↑, 진단 시간↓ 막대, "Less burden. A precise starting point." |
| 7 | One simple rule | 큰 질문 → 사다리: 정답이면 위로, 오답이면 아래로 |
| 8 | Walking the difficulty ladder | 1~9 사다리: 오답 5→3→1, 정답 5→7→9, 효과음과 같은 시각. 오답 결과는 정답 경우 동안 흐리게 남음 |
| 9 | A built-in validation step | 대표+유사 2문항 → ✓✗✓ = UNDERSTOOD 도장, ✓✗✗ = NOT UNDERSTOOD 도장 |
| 10 | Use it right away, on site | 수와 연산 구간이 먼저 차는 고리, 빠른 리포트, 상담 말풍선 |
| 11 | What changes in practice | 91 → 3 (Q3 · Q57 · Q80에 동그라미), 부담↓·효율↑, JEI Math에서 다른 과목으로 |
| 12 | Thank you | 손글씨 Thank you |

## 고치기·렌더링

- 내레이션·자막·시각: `../adaptive-diagnosis/tools/make_audio.py`에서 고친 뒤 `tools/sync_narration.sh`로 `timeline.js`와 `audio/mix.wav`를 복사
- 장면: `index.html`의 `SC.intro` ~ `SC.outro`, 색·제목: `content.js` (영상 편집기에서도 수정 가능)

```bash
npm install
tools/sync_narration.sh
export FFMPEG=$(python3 -c "import imageio_ffmpeg as i; print(i.get_ffmpeg_exe())")
export CHROMIUM="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"   # macOS
node render.mjs --workers 6   # out/adaptive_diagnosis_v2.mp4 (브라우저 6개가 나눠 그려요)
```
