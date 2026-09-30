# 밤하늘 별자리 여행 (three.js 30초 교육 영상)

- 30초, 1920×1080, 30fps. [three.js](https://threejs.org) r159로 만든 3D 밤하늘 안을 카메라가 이동하며 별자리를 설명
- 폰트: Noto Sans KR(가는 굵기) + Inter. 음악은 `tools/make_audio.py`에서 코드로 합성 (외부 음원 없음)

## 실제 하늘 데이터

- 이름 있는 별 29개는 실제 적경(RA)·적위(Dec)·밝기(등급)로 배치했고, 베텔게우스는 붉게, 리겔은 푸르게 칠함
- 하늘 안쪽에서 올려다본 방향 그대로라 북쪽이 위일 때 동쪽이 왼쪽 (북두칠성 손잡이와 베텔게우스가 왼쪽에 옴)
- 은하수는 은하 좌표계(은경·은위)에서 만든 뒤 적도 좌표계로 변환해서 실제 위치에 흐름. 그래서 여름철 대삼각형 장면에서 견우성과 직녀성 사이로 은하수가 지나감

| 시간 | 별자리 | 설명 |
|---|---|---|
| 0–4s | 타이틀 | 밤하늘 별자리 여행 |
| 4–10.5s | 북두칠성 (봄·북쪽 하늘) | 큰곰자리의 꼬리, 국자 모양 일곱 별 → 국자 끝 두 별 간격의 5배로 북극성 찾기 |
| 10.5–16s | 카시오페이아자리 (가을·북쪽 하늘) | W 모양 다섯 별, 북극성을 사이에 두고 북두칠성과 마주 봄 |
| 16–22s | 오리온자리 (겨울·남쪽 하늘) | 허리의 세 별, 붉은 베텔게우스와 푸른 리겔 |
| 22–27s | 여름철 대삼각형 (여름·머리 위 하늘) | 베가(직녀성)·데네브·알타이르(견우성), 백조자리 |
| 27–30s | 마무리 | 북쪽 하늘을 넓게 보며 정리 |

## 수정·렌더링

- 별 데이터와 별자리 선: `index.html`의 `STARS`, `CONST`
- 카메라 이동: `CAM` (시각, RA, Dec, 화각)
- 화면 문구: `PANELS`, `titles()`
- 음악: `tools/make_audio.py`

```bash
npm install && pip install numpy soundfile imageio-ffmpeg
python3 tools/make_audio.py          # audio/mix.wav
export FFMPEG=$(python3 -c "import imageio_ffmpeg as i; print(i.get_ffmpeg_exe())")
node render.mjs                      # out/constellations.mp4
```

GPU가 없는 환경에서는 소프트웨어 WebGL(SwiftShader)로 그려서 렌더링에 10분 넘게 걸립니다. `vendor/three.min.js`는 three.js(MIT 라이선스, `vendor/three.LICENSE`)입니다.
