# 중학교 수학 「피타고라스 정리」 설명 모션그래픽

- 길이 약 2분 19초, 1920×1080, 30fps, 한국어 내레이션 + 효과음 + 자막
- 재능교육 브랜드 컬러(레드 #E60012 / 블랙). 넓이는 a² = 레드, b² = 블랙, c² = 핑크로 영상 전체에서 통일
- 폰트: Noto Sans KR(본문), Inter(숫자), Noto Serif Italic(변수 a, b, c). 모두 SIL OFL 라이선스이고 `fonts/`에 포함

| 원본 시각 | 내용 |
|---|---|
| 0:00 | 타이틀 |
| 0:06 | 개념 1: 직각삼각형, 직각을 낀 두 변 a·b와 빗변 c |
| 0:20 | 개념 2: 세 변 위에 정사각형 세우기 (a², b², c²) |
| 0:38 | 개념 3: a=3, b=4, c=5 일 때 칸 세기 → 9 + 16 = 25 |
| 1:00 | 개념 4: 한 변이 a+b인 정사각형 안의 삼각형 4개를 옮기는 그림 증명 |
| 1:24 | 개념 5: a² + b² = c² 공식 정리 |
| 1:36 | 예제: 두 변이 6, 8일 때 빗변 구하기 → c = 10 |
| 1:56 | 마무리 |

표의 시각은 내레이션에 맞춰 늘리기 전 기준입니다.

## 수정 방법

| 바꾸고 싶은 것 | 고칠 곳 |
|---|---|
| 내레이션 문장, 자막 | `tools/make_audio.py`의 `NARRATION` (읽을 문장과 자막을 한 줄에 함께 적음) |
| 목소리, 속도, 문장 사이 쉼 | 같은 파일의 `VOICE_SID`, `BASE_SPEED`, `PAUSE` |
| 효과음 | 같은 파일의 `sfx_events()` |
| 그림, 색, 애니메이션 | `index.html`의 `C` 팔레트와 `sTitle` ~ `sEnd` 함수 |

`timeline.js`(자막과 시간 늘리기 정보)는 `tools/make_audio.py`가 만드는 파일이니 직접 고치지 마세요.

## 렌더링

```bash
npm install
pip install sherpa-onnx soundfile numpy imageio-ffmpeg
curl -LO https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/sherpa-onnx-supertonic-3-tts-int8-2026-05-11.tar.bz2
tar xjf sherpa-onnx-supertonic-3-tts-int8-2026-05-11.tar.bz2
TTS_MODEL_DIR=./sherpa-onnx-supertonic-3-tts-int8-2026-05-11 python3 tools/make_audio.py   # audio/mix.wav, timeline.js
export FFMPEG=$(python3 -c "import imageio_ffmpeg as i; print(i.get_ffmpeg_exe())")
node render.mjs                                                                            # out/pythagoras.mp4
```

화면만 바꿨다면 `node render.mjs`만 다시 실행하면 됩니다. Chromium 경로가 다르면 `CHROMIUM` 환경변수로 지정하세요.

- 내레이션: [Supertonic 3](https://github.com/supertone-inc/supertonic) (OpenRAIL-M), [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx)로 실행
- 효과음: `tools/make_audio.py`에서 코드로 합성 (외부 음원 없음)
