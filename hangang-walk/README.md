# 한강 다리 산책 (three.js 15초 배경 영상)

- 15초, 1920×1080, 30fps. 사람 없이 해 질 녘 한강 다리 인도를 따라 옆으로 이동하는 시점 (강을 정면으로 보는 옆면 샷)
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

- 수면: 카메라를 수면 아래로 뒤집어 한 번 더 그리는 실제 평면 반사를 쓰고, 여러 방향 물결로 불빛이 세로로 길게 번져요. 해 반사 반짝임도 있어요
- 조명: 노을 방향광, 하늘빛, 가까운 가로등 네 개의 점광원이 난간과 기둥에 음영을 만들어요. 빌딩 창문은 층마다 켜진 창과 꺼진 창이 섞여 스스로 빛나요
- 하늘: 노을빛을 받은 층구름(노이즈 셰이더)
- 카메라 느낌: 셔터 1/60초 모션블러(프레임마다 3장 합성), 빛 번짐(블룸), 필름 톤 보정과 입자
- 카메라는 강을 정면(옆 90°)으로 보며 초당 2.6m로 옆으로 이동하고, 초당 1.85걸음에 맞춰 살짝 흔들려요

## 수정·렌더링

- 영상 편집기(`../video-editor.html`)에서 하늘·해·구름·안개 색, 햇빛·가로등·창문 불빛, 강물 색과 반짝임, 블룸·색조·비네트·필름 입자를 바꿀 수 있어요. 기본값은 `content.js`, 편집기 칸 설명은 `schema.js` (규칙: `../editor/PROTOCOL.md`)
- 편집기에서 저장한 작업 파일은 `node render.mjs --project 작업.json` 으로 렌더링해요
- 걷는 속도·흔들림·시선(`WALK`, `camState()`)과 해 위치(`SUN_DIR`)는 편집기에서 못 바꿔요. 발소리가 초당 1.85걸음에 맞춰 합성돼 있어서, 바꾸려면 `tools/make_audio.py`의 `STEPS_PER_SEC`도 함께 고쳐야 해요

```bash
npm install && pip install numpy soundfile imageio-ffmpeg
python3 tools/make_audio.py          # audio/mix.wav
export FFMPEG=$(python3 -c "import imageio_ffmpeg as i; print(i.get_ffmpeg_exe())")
node render.mjs                      # out/hangang_walk.mp4
```

GPU가 없는 환경에서는 소프트웨어 WebGL(SwiftShader)로 그려서 30분 가까이 걸립니다(프레임당 약 3.7초). 빠르게 확인할 때는 `node render.mjs --preview`를 쓰세요.
