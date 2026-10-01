# 재능교육 홍보 · CELEBRATION 버전 (모션그래픽)

`../jei-promo-30s`(재능교육 홍보 30초)와 같은 사실·문구를, 교육플랫폼팀 홍보에서 쓴 배경음(Forrest Frank – CELEBRATION)의 드롭과 박자에 맞춰 다시 짠 버전이에요. 기존 30초 영상은 그대로 두었어요.

- 33.4초, 1920×1080, 30fps. 레드 #E60012 · 블랙 · 크림에 포인트 노랑
- 폰트: Black Han Sans(제목) · Noto Sans KR · Inter, 모두 SIL OFL 라이선스로 `fonts/`에 포함
- 곡에 맞춘 표현: 드롭 전 4박에 한 글자씩 쿵 → 드롭 순간 화면이 터지며 **스스로.** 착지, 흐르는 띠(티커), 노란 형광펜, 스티커, 16분음표마다 착착 올라가는 연도·숫자, 큰 순간마다 흔들림과 줌 펀치

| 시간(곡 박자 기준) | 장면 | 내용 |
|---|---|---|
| 0–2s | 드롭 전 4박 | AI 시대에도 (한 글자씩) → 화면 안으로 빨려 들어감 |
| 2–6s | 드롭 | 결국, **스스로.** + 흐르는 띠 + 색종이 |
| 6–10s | 교육 50년 | 1977 → 2027 연도 카운터, 교육 한 길, 50년. · 1981 재능산수로 시작한 스스로학습 |
| 10–16s | 스스로학습시스템 | 스스로 생각하고 / 풀고 / 자란다 (마디마다 한 줄), 공이 박마다 계단을 오름 |
| 16–22s | 수상 | 18년 연속 대한민국 퍼스트브랜드 대상 · 13년 연속 소비자 선정 최고의 브랜드 대상 |
| 22–27s | 세계로 | 1992년 미국을 시작으로, 나라 6곳이 박마다 하나씩 |
| 27–33s | 엔딩 | 재능교육 · AI 시대에도 결국, 스스로. · jei.com |

시각은 120BPM 격자 기준이고, 실제 영상은 곡의 박 길이(약 122BPM)에 맞게 조금 줄어요. 사실 출처는 `../jei-promo-30s/README.md`와 같아요.

## 배경음 (사내용)

- 곡 파일은 저작권 때문에 저장소에 넣지 않아요. `audio/celebration.mp3`로 직접 넣고 아래 순서로 만드세요. 외부 공개용은 라이선스 음원으로 바꿔야 해요
- 곡 구간·박자는 교육플랫폼팀 영상과 같아요 (`song.js`: 드롭 33.5초, 드롭 4박 전 31.54초부터 33.4초)
- 효과음(전환 슉, 착지 쾅, 숫자 딸깍, 나라 뿅)은 곡을 해치지 않게 작게 넣어요. 시각은 화면에서 뽑아 와요 (`tools/export_events.mjs` → `tools/events.json`)

## 고치기·렌더링

문구·색은 `content.js`, 장면·박자는 `index.html`의 `s0`~`s6`, 소리는 `tools/make_audio.py`에 있어요. 공용 영상 편집기(`../video-editor.html`)에서 **재능교육 홍보 · CELEBRATION**을 골라 문구와 색을 바꿀 수 있어요.

```bash
npm install && pip install numpy soundfile imageio-ffmpeg
# audio/celebration.mp3 를 넣은 뒤
pip install librosa && python3 tools/analyze_song.py   # song.js, tools/song.json (이미 들어 있으면 생략)
node tools/export_events.mjs         # tools/events.json
python3 tools/make_audio.py          # audio/mix.wav
export FFMPEG=$(python3 -c "import imageio_ffmpeg as i; print(i.get_ffmpeg_exe())")
node render.mjs                      # out/jei_promo_celebration.mp4
```
