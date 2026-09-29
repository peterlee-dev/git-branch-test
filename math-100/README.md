# 수학 1-2 「1. 100까지의 수」 개념 정리 모션그래픽

- 길이 2분 4초, 1920×1080, 30fps, 한국어 내레이션 + 효과음 포함
- 재능교육 브랜드 컬러(레드 #E60012 / 블랙)를 유아용으로 부드럽게 확장. 십의 자리는 레드, 일의 자리는 블랙으로 통일
- 폰트: **Jua(주아체)**. 둥글고 귀여운 유아용 서체이고 SIL OFL 라이선스라 사내 사용 가능. `fonts/`에 포함되어 있음

| 시간 | 내용 |
|---|---|
| 0:00 | 타이틀: 100까지의 수 · 단원 개념 정리 |
| 0:07 | 개념 1: 10개씩 묶음을 세며 60 만들기 → 육십/예순, 70·80·90 읽기 표 |
| 0:31 | 개념 2: 10개씩 묶음 7개 + 낱개 3개 = 73 (칠십삼/일흔셋) |
| 0:45 | 개념 3: 89·90·91 (1만큼 더 작은 수/큰 수), 51~100 수 배열표, 99+1 = 100(백) |
| 1:11 | 개념 4: 56 < 62 (묶음 비교), 94 > 91 (묶음이 같으면 낱개 비교) |
| 1:29 | 개념 5: 둘씩 짝 짓기 → 짝수(2,4,6,8,10) / 홀수(1,3,5,7,9) |
| 1:46 | 오늘 배운 개념 정리 |

화면 아래 자막은 `index.html`의 `SUBS` 배열에서 고칠 수 있습니다. 아래 표의 시간은 내레이션에 맞춰 늘리기 전 기준입니다.

## 내레이션 · 효과음

- **내레이션**: [Supertonic 3](https://github.com/supertone-inc/supertonic) 소형 온디바이스 TTS를 [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx)로 실행. 한국어 여성 음성(sid 1)을 쓰고, 숫자는 읽는 방식대로 한글로 적어 둠(예: 육십, 여섯 개). 모델 라이선스는 OpenRAIL-M
- **효과음**: 뿅(등장), 딸깍(블록 쌓기), 띵(숫자 공개), 반짝(정답), 슉(장면 전환), 폴짝(캐릭터 점프). 모두 `tools/make_audio.py`에서 코드로 합성해서 외부 음원이 없음
- **싱크**: 내레이션은 보통 속도로 두고, 문장이 긴 구간만 애니메이션을 천천히 흐르게 늘림. 스크립트가 늘린 구간을 `warp.js`에 기록하고 페이지가 이를 반영함

```bash
pip install sherpa-onnx soundfile numpy
curl -LO https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/sherpa-onnx-supertonic-3-tts-int8-2026-05-11.tar.bz2
tar xjf sherpa-onnx-supertonic-3-tts-int8-2026-05-11.tar.bz2
TTS_MODEL_DIR=./sherpa-onnx-supertonic-3-tts-int8-2026-05-11 python3 tools/make_audio.py   # audio/mix.wav, warp.js 생성
node render.mjs
```

내레이션 문장과 시각은 `tools/make_audio.py`의 `NARRATION`에서, 효과음 위치는 `sfx_events()`에서 고칠 수 있습니다.

## 렌더링

```bash
npm install
export FFMPEG=$(python3 -c "import imageio_ffmpeg as i; print(i.get_ffmpeg_exe())")   # ffmpeg가 없을 때
node render.mjs           # out/math_100.mp4
```

`audio/mix.wav`가 있으면 렌더링할 때 자동으로 합쳐집니다.
