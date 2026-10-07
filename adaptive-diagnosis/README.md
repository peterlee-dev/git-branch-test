# Adaptive Diagnostic Assessment (재능스스로수학 온라인 적응형 진단평가 · 영문 설명 영상)

수학팀 발표 자료(PT, 영문 17장)와 영문 대본을 바탕으로 만든 모션그래픽 설명 영상이에요. 장표의 흰 바탕·파란 물결 디자인을 그대로 살리고, 각 장표의 도식을 내레이션에 맞춰 움직이게 다시 그렸어요.

- 1920×1080, 30fps. 폰트: Noto Sans KR (SIL OFL)
- 내레이션: 팀에서 준 음성 샘플(`audio/voice_ref.wav`, 4.6초)을 Qwen3-TTS (Apache 2.0) Base 모델로 복제해 영문 대본 31문장을 읽음. 샘플 파일과 만든 음성은 저장소에 올리지 않아요(`audio/` 는 gitignore)
- 자막: 문장을 읽기 좋은 길이로 나눠 소리 길이에 맞춰 보여 줌
- 효과음(정답 딩, 오답 붑, 장면 전환)과 잔잔한 배경 화음은 `tools/make_audio.py`에서 합성

| 장면 | 장표 | 움직임 |
|---|---|---|
| Title | 1 | 파란 물결이 올라오고 제목이 한 글자씩 |
| What is a diagnostic assessment? | 2 | 사전 평가 → 수준 파악 → 맞춤 처방 카드 |
| Problems | 3 | 모두 같은 문제 → 정확도↑ BUT 부담↑(문제가 쌓임), 효율↓ |
| Adaptive diagnostic assessment | 4 | 28×70 문제 → 정답이면 419×58, 오답이면 34×8 |
| Only the necessary questions | 5 | 20문항 X 표시 → 필요한 5문항만 켜짐 |
| Benefits | 6 | 효율·신뢰도↑(막대 성장), 진단 시간↓(시계) |
| How it works | 7–8 | 질문 → 정답이면 위로, 오답이면 아래로 |
| Algorithm example | 9–12 | 1~9번 노드: 오답 시 5→3→1, 정답 시 5→7→9, 요약 카드 |
| Validation step | 13–14 | 대표 문항+유사 2문항, 3개 중 2개 정답 = Understood |
| Quick Diagnosis | 15 | 수와 연산 먼저 → 빠른 리포트 → 상담 |
| Expected effects | 16 | Q1~Q91 → Q3·Q57·Q80, 부담↓·효율↑, 다른 과목으로 확장 |
| Thank you | 17 | |

## 고치기·렌더링

- 대본: `tools/make_audio.py`의 `SCRIPT` (자막 문장, 읽는 문장, 쉬는 시간). 다시 실행하면 `timeline.js`와 소리가 같이 바뀌고, 바뀐 문장만 다시 만들어요. 숫자·약어는 읽는 문장에서 풀어 써요 (No. 3 → number three, JEI → J.E.I.)
- 장면별 움직임: `index.html`의 `sIntro` ~ `sOutro`. 모든 움직임이 대사 시작·끝 시각(`st('l15', .5)` = l15 문장의 절반 지점)에 묶여 있어서 목소리를 바꿔도 맞춰져요
- 영상 편집기(`../video-editor.html`)에서 제목·과목 이름·자막·색을 바꿀 수 있어요

```bash
npm install && pip install torch qwen-tts soundfile numpy
cp <voice-sample>.wav audio/voice_ref.wav
QWEN_BASE_DIR=/path/Qwen3-TTS-12Hz-1.7B-Base python3 tools/make_audio.py
export FFMPEG=$(python3 -c "import imageio_ffmpeg as i; print(i.get_ffmpeg_exe())")
node render.mjs        # out/adaptive_diagnosis.mp4
```
