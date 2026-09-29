# 광합성 종이공예(페이퍼 컷아웃) 과학 영상

- 길이 약 2분 31초, 1920×1080, 30fps, 한국어 내레이션 + 효과음 + 자막
- 종이 재질 표현
  - 종이결 텍스처(코드로 생성해 multiply로 입힘)와 조각마다 겹쳐 쌓인 그림자
  - 가위로 오린 듯한 가장자리와 종이가 슥 밀려 지나가는 장면 전환
  - 스톱모션: 움직임을 15fps로 끊고, 종이가 초당 6번 살짝 떨림
- 폰트: Jua(주아체) + Noto Sans KR(특수 기호 보조). 모두 SIL OFL 라이선스이고 `fonts/`에 포함

| 원본 시각 | 내용 |
|---|---|
| 0:00 | 타이틀 |
| 0:07 | 궁금해요: 식물은 밥을 먹지 않는데 어떻게 자랄까? |
| 0:22 | 광합성의 재료: 빛, 물(뿌리 → 줄기 → 잎), 이산화탄소(기공) |
| 0:48 | 광합성이 일어나는 곳: 잎 → 세포 → 엽록체, 엽록소 |
| 1:08 | 광합성 식: 이산화탄소 + 물 → (빛에너지) → 포도당 + 산소 |
| 1:32 | 결과: 포도당(성장에 사용, 녹말로 저장), 산소 방출 |
| 1:52 | 영향 요인: 빛의 세기, 이산화탄소 농도, 온도 그래프 |
| 2:12 | 정리 |

표의 시각은 내레이션에 맞춰 늘리기 전 기준입니다.

## 수정 방법

| 바꾸고 싶은 것 | 고칠 곳 |
|---|---|
| 내레이션 문장, 자막 | `tools/make_audio.py`의 `NARRATION` (읽을 문장과 자막을 한 줄에 함께 적음) |
| 목소리, 속도, 문장 사이 쉼 | 같은 파일의 `VOICE_SID`, `BASE_SPEED`, `PAUSE` |
| 효과음 | 같은 파일의 `sfx_events()` |
| 색, 그림, 장면 | `index.html` 위쪽의 색 상수와 `sTitle` ~ `s7` 함수 |
| 스톱모션 프레임 수 | `index.html`의 `draw()` 안 `t * 15` |

`timeline.js`(자막과 시간 늘리기 정보)는 `tools/make_audio.py`가 만드는 파일이니 직접 고치지 마세요.

## 렌더링

```bash
npm install
pip install sherpa-onnx soundfile numpy imageio-ffmpeg
curl -LO https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/sherpa-onnx-supertonic-3-tts-int8-2026-05-11.tar.bz2
tar xjf sherpa-onnx-supertonic-3-tts-int8-2026-05-11.tar.bz2
TTS_MODEL_DIR=./sherpa-onnx-supertonic-3-tts-int8-2026-05-11 python3 tools/make_audio.py   # audio/mix.wav, timeline.js
export FFMPEG=$(python3 -c "import imageio_ffmpeg as i; print(i.get_ffmpeg_exe())")
node render.mjs                                                                            # out/photosynthesis.mp4
```

화면만 바꿨다면 `node render.mjs`만 다시 실행하면 됩니다. Chromium 경로가 다르면 `CHROMIUM` 환경변수로 지정하세요.

- 내레이션: [Supertonic 3](https://github.com/supertone-inc/supertonic) (OpenRAIL-M), [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx)로 실행
- 효과음: `tools/make_audio.py`에서 코드로 합성 (외부 음원 없음)
