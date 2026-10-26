# Adaptive Diagnostic Assessment — v2 (모눈종이 워크북)

`../adaptive-diagnosis`와 **같은 대본(31문장)**을 쓰고, 화면은 `../math-di-improvement-v2`와 같은 콘셉트로 새로 그린 버전이에요. 내레이션은 v1의 Qwen3-TTS 복제 음성 대신 **같은 대본을 한 번에 읽은 녹음 `audio/narration.mp3`**(223초, 영어)를 문장 31개로 잘라 다시 배치해요. 기존 장표 버전(v1)과 그 소리·시각표는 그대로 두었어요. 이전의 밤하늘 버전은 git 기록(`8e14945`)에 남아 있어요.

- **모눈종이 워크북 한 장**: 장면마다 한 쪽(p. 1 ~ p. 12). 장면이 바뀔 때 종이 위를 옆으로 넘어가고(믹스의 휙 소리와 같은 때), 읽는 동안은 화면이 움직이지 않아요(카메라 줌 없음)
- 선생님 펜 표시: 빨간 동그라미·체크·가위표·밑줄, 형광펜, 도장(UNDERSTOOD / NOT UNDERSTOOD)
- 색(2026-10-22, `수학 영상 컬러 개선.pdf`): 흰 바탕 위에 레드 `#E5303A` 하나를 메인으로(정답·긍정·상승·체크, 섹션 태그·핵심 숫자, 선생님 펜), 네이비 `#0F2F57`는 오답·부정·하락, 블루 `#2C64C8`·민트 `#32C2AD`는 비교 2·3번째(진단 단계 2·3, 고리의 나머지 영역, check this one), 나머지는 그레이. 글자 `#383838`, 형광펜은 연한 블러시. 팔레트는 `content.js`의 `colors`
- 되풀이되는 그림: **난이도 사다리 1~9** — 맞히면 위로, 틀리면 아래로
- 1920×1080, 30fps. 글꼴은 macOS 시스템 글꼴 Avenir Next(본문)·Noteworthy(손글씨), 한글은 Noto Sans KR로 대신 그려요. 배경음악 없음 (내레이션 + 정답·오답·장면 전환 효과음)
- 화면에 자막은 넣지 않아요 (내레이션만)

| p. | 장면 | 구성 |
|---|---|---|
| 1 | Title | 제목 형광펜, 선생님이 채점하는 진단 시험지, 아래 가운데 "Find the starting point"에 빨간 펜 밑줄 (점수 표시 없음) |
| 2 | What is a diagnostic assessment? | 1 ASSESS(take an assessment) → 2 DIAGNOSE → 3 PRESCRIBE(Personalized program) 카드 |
| 3 | The problem today | 쌓이는 문제지와 91문항 카운터, 정확도↑ BUT 부담↑, Effectiveness↓ 막대(finding the starting point) |
| 4 | Adaptive Diagnostic Assessment | 문제 카드 28×70 → "correctly"에 맞음(레드 ○) 위쪽 더 어려운 419×58, "incorrectly"에 틀림(네이비 ✗) 아래쪽 더 쉬운 34×8 |
| 5 | Only the questions that matter | 20문항 문제지에서 5문항만 동그라미, 나머지 가위표, 20 → 5 |
| 6 | What it improves | 효율·신뢰도↑, 진단 시간↓ 막대, "Less burden. A precise starting point." |
| 7 | One simple rule | 큰 질문 → 사다리: 정답이면 위로(move UP to find how far they know), 오답이면 아래로 |
| 8 | Each answer narrows the range | 1~9 사다리. 오답: 5 ✗ → 6~9 ✗(no need to ask) → 펜 화살표 → 3 ✗ → 4 ✗ → 화살표 → 1 ✓. 정답 설명이 시작되면 사다리를 처음 상태로 지우고: 5 ✓ → 1~4 ✓ → 화살표 → 7 ✓ → 6 ✓ → 화살표 → 9 ✗. 문항 번호를 읽는 단어에 효과음과 같은 시각 |
| 9 | A built-in validation step | 대표+유사 2문항 → ✓✗✓ = UNDERSTOOD 도장, ✓✗✗ = NOT UNDERSTOOD 도장 |
| 10 | Use it right away, on site | 회색 고리에서 수와 연산 구간(레드)이 차고 → 오른쪽 빠른 리포트(막대 3개 레드) → 리포트 아래에 꼬리가 오른쪽 위를 향한 말풍선 "How well does this learner know Numbers & Operations?", "Let's plan the next steps."가 차례로 → 고리 나머지(다른 영역)가 블루로 차고 블루 "other areas continue…" |
| 11 | What changes in practice | 카드 위 작은 글씨 "Currently → With Adaptive (example)", 91 → 40 (40에서 멈추며 레드로, 아래 "Q1 ~ Q91"은 그대로 두고 그 아래 가운데 검정 "51" + 회색 "skipped"), Workload↓·Smoother running↑, JEI Math에서 다른 과목으로 |
| 12 | Thank you | 손글씨 Thank you |

## 고치기·렌더링

- 내레이션·시각: `tools/make_audio.py`가 `audio/narration.mp3`(녹음)와 `audio/narration_words.json`(whisper large-v3-turbo 단어 받아쓰기)으로 `timeline.js`와 `audio/mix.wav`를 만들어요
  - 대본·장면 목록·간격(GAP 0.45초, 장면 사이 SCENE_GAP 1초, 문장별 쉼)·효과음은 `../adaptive-diagnosis/tools/make_audio.py`(v1)에서 그대로 불러 써요(v1 파일과 결과물은 건드리지 않음)
  - 대본 단어를 받아쓰기에 맞춰(601/601 단어 일치) 문장마다 앞뒤 무음 한가운데서 자르고, 소리 나는 부분 앞 0.08초·뒤 0.15초를 남겨요
  - **3차 수정**: 최종 대본(`[최종] 수학 어댑티브 정밀진단평가 영상 대본_최종.pdf`)에서 문구가 바뀐 **15문장**(l3, l5, l6, l8, l11, l15, l16, l17, l21, l22, l23, l25, l27, l28, l29)은 녹음에서 자르지 않고, **이 녹음의 목소리를 복제한** Qwen3-TTS(DGX `~/dev/qwen3-tts-api`, 참조 = 녹음의 l3~l4 14.1–28.7초)로 새로 만든 `audio/clone_<id>.wav`를 같은 자리에 넣어요. 문장마다 후보 8개 → Whisper 받아쓰기 일치 → 화자 유사도 최고 → 원래 문장 말 빠르기에 맞춰 배속. `make_audio.py`가 녹음 평균 스펙트럼에 맞춘 EQ와 원래 문장과 같은 음량으로 맞춰요. 생성 스크립트는 `tools/clone_lines_dgx.py`(DGX에서 실행, 문장 목록 `tools/clone_lines.json` → DGX `out/clone-adaptive/lines.json`), 나머지 16문장은 그대로 녹음
  - `TL.cues`에 그림·효과음이 따르는 단어 시각(사다리의 "incorrectly / three / one", "correctly / seven / nine", 4쪽 "correctly / incorrectly", 9쪽 "Understood / Not" 등)이 들어가요
- 장면: `index.html`의 `SC.intro` ~ `SC.outro`, 색·제목: `content.js` (영상 편집기에서도 수정 가능)

```bash
npm install
python3 -m venv .venv && .venv/bin/pip install numpy soundfile   # 한 번만 (.venv 는 저장소 밖에 두어도 돼요)
.venv/bin/python tools/make_audio.py                             # timeline.js, audio/mix.wav
export FFMPEG=$(python3 -c "import imageio_ffmpeg as i; print(i.get_ffmpeg_exe())")
export CHROMIUM="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"   # macOS
node render.mjs --workers 4   # out/adaptive_diagnosis_v2.mp4 (브라우저 4개가 나눠 그려요)
```
