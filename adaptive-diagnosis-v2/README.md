# Adaptive Diagnostic Assessment — v2 (새 구성)

`../adaptive-diagnosis`와 **같은 내레이션(받은 음성 샘플을 복제한 Qwen3-TTS)과 같은 시각표**를 쓰고, 화면은 장표를 따라 하지 않고 처음부터 새로 구성한 버전이에요. 기존 버전은 그대로 두었어요.

- 어두운 밤하늘 배경 + 떠다니는 빛 입자, 빛나는 구슬 = 학습자
- 큰 제목 글자가 아래에서 솟아오르는 키네틱 타이포
- 하나의 시각 은유로 끝까지: **난이도 사다리** — 맞히면 한 칸 위로, 틀리면 한 칸 아래로
- 1920×1080, 30fps, 폰트 Noto Sans KR. 배경음악 없음 (내레이션 + 정답·오답 효과음)
- 모든 글자는 폭을 재서(`measure`, `maxW`, `pill`) 상자 밖으로 넘치지 않게 배치

| 장면 | 구성 |
|---|---|
| Title | 빛 입자가 모여 고리가 되고 제목 세 단어가 솟아오름 |
| What is a diagnostic assessment? | 1 ASSESS → 2 DIAGNOSE → 3 PRESCRIBE 정거장을 구슬이 지나감 |
| The problem today | 문제 타일이 학습자 위에 쌓이며 91문항 카운터, 정확도↑·부담↑(BUT)·효율↓ 막대 |
| Adaptive Diagnostic Assessment | 실시간으로 자라는 분기 나무: 맞으면 위(파랑), 틀리면 아래(주황) |
| Only the questions that matter | 20문항을 빛이 훑고 5문항만 남음, 20 → 5 카운터 |
| What it improves | 효율·신뢰도 게이지↑, 진단 시간 게이지↓, "Less burden. A precise starting point." |
| One simple rule | 사다리에서 정답이면 위로, 오답이면 아래로 |
| Walking the difficulty ladder | 1~9 사다리: 오답 5→3→1(학습 공백 시작), 정답 5→7→9(이해가 닿는 곳), 효과음과 같은 시각 |
| A built-in validation step | 카드 3장(대표+유사 2) → ✓✗✓ = UNDERSTOOD 도장, ✓✗✗ = NOT UNDERSTOOD 도장 |
| Use it right away, on site | 수와 연산 구간이 먼저 차는 고리, 빠른 리포트 카드, 상담 말풍선 |
| What changes in practice | 91 → 3 카운터, 부담↓·효율↑ 막대, JEI Math 허브에서 다른 과목으로 뻗는 선 |
| Thank you | 입자 고리 안의 Thank you |

## 고치기·렌더링

- 내레이션·자막·시각: `../adaptive-diagnosis/tools/make_audio.py`에서 고친 뒤 `tools/sync_narration.sh`로 `timeline.js`를 복사하고 `python3 tools/make_mix.py`로 소리를 다시 섞음 (정답·오답 효과음은 v2의 사다리 단계 시각 `STEPS`에 맞춤)
- 장면: `index.html`의 `sIntro` ~ `sOutro`, 색·제목: `content.js` (영상 편집기에서도 수정 가능)

```bash
npm install
tools/sync_narration.sh
export FFMPEG=$(python3 -c "import imageio_ffmpeg as i; print(i.get_ffmpeg_exe())")
node render.mjs        # out/adaptive_diagnosis_v2.mp4
```
