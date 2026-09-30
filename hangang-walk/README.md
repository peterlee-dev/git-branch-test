# 한강 다리 산책 (three.js 15초 배경 영상)

- 15초, 1920×1080, 30fps. 사람 없이 해 질 녘 한강 다리 인도를 걷는 1인칭 시점
- [three.js](https://threejs.org) r159 (`vendor/three.min.js`, MIT 라이선스)
- 배경음: 바람 · 강물 · 멀리 차 소리 · 발소리를 `tools/make_audio.py`에서 코드로 합성 (외부 음원 없음). 배경으로만 쓸 때는 음소거해도 됩니다

## 패럴랙스 층 (가까운 것일수록 빠르게 지나감)

| 거리 | 요소 |
|---|---|
| 0~3m | 난간 기둥(1.6m 간격), 보도블록, 가로등 기둥(15m 간격)과 바닥에 떨어진 불빛 |
| 5~20m | 왼쪽 차도를 오가는 차 불빛 (가까운 차선은 앞으로, 먼 차선은 반대로) |
| 200m | 강 위를 지나가는 유람선 |
| 760m · 1.9km | 멀리 강을 가로지르는 다른 다리 두 개와 조명 |
| 약 1km | 강 건너 강변 불빛, 나무 띠, 아파트·빌딩 스카이라인, 항공등 |
| 2~4km | 남산서울타워, 겹겹이 이어지는 산 능선 |

- 수면에는 스카이라인, 다리, 불빛이 거꾸로 비치고, 잔물결과 노을 반사가 움직여요
- 카메라는 초당 2.4m로 걸으면서 초당 1.85걸음에 맞춰 살짝 흔들려요. 시선은 오른쪽 강 쪽에서 조금씩 앞으로 돌아와요

## 수정·렌더링

- 걷는 속도·시선: `index.html`의 `WALK`, `camState()`
- 하늘 색: 하늘 셰이더의 `zenith`, `mid`, `horizon`
- 해 위치: `SUN_DIR`

```bash
npm install && pip install numpy soundfile imageio-ffmpeg
python3 tools/make_audio.py          # audio/mix.wav
export FFMPEG=$(python3 -c "import imageio_ffmpeg as i; print(i.get_ffmpeg_exe())")
node render.mjs                      # out/hangang_walk.mp4
```

GPU가 없는 환경에서는 소프트웨어 WebGL(SwiftShader)로 그려서 몇 분 걸립니다.
