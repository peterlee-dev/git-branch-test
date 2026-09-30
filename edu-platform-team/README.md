# 재능교육 교육플랫폼팀 30초 홍보 영상

- 30초, 1920×1080, 30fps. **통통 튀는 버전**: 장면마다 레드·크림·노랑·파랑·민트·네이비로 배경이 바뀌고, 글자가 한 글자씩 튀어 올라 찌그러졌다 펴져요. 박자마다 화면이 쿵 흔들리고 색종이가 터져요
- 폰트: Black Han Sans(제목) · Noto Sans KR · Inter · JetBrains Mono, 모두 SIL OFL 라이선스로 `fonts/`에 포함
- 사운드: 120BPM 비트 + 마림바 멜로디 + 뿅·통·도장 효과음을 `tools/make_audio.py`에서 합성 (외부 음원 없음)

| 시간 | 장면 | 내용 |
|---|---|---|
| 0–4s | 인트로 | `Hello, World!` 스티커 → **우리는 교육플랫폼팀!** 글자가 통통 떨어지고 색종이 폭발 |
| 4–8s | 파이프라인 | **상상하면, 만든다!** 노란 공이 박자마다 연구원 → 저작도구 → 콘텐츠 → 교육 서비스로 통통 |
| 8–12s | 저작도구 | 문제·보기·정답·해설 블록이 튀며 떨어져 문항 완성 → **발행!** 도장 쾅 |
| 12–16s | 양산 | 카드가 박자마다 ×2 → ×128까지 늘어남. **하나를 만들면 모두에게!** |
| 16–20s | 웹 + 앱 | 브라우저와 휴대폰이 번갈아 뛰어오름. **웹도! 앱도!** |
| 20–25s | AI | 로봇 캐릭터에게 "덧셈 문항 5개랑 해설 만들어 줘!" → 문항 카드가 톡톡. **AI랑 같이, 더 빠르게!** |
| 25–30s | 엔딩 | **열정** 스위치 ON → **교육의 미래를, 코드로.** · 재능교육 교육플랫폼팀 |

참고: [재능e아카데미 회사소개](https://it.jei.com/about/), [팀문화](https://it.jei.com/culture/) (검색 결과로 확인. 작업 환경에서 사이트 직접 접속은 차단됨)

## 비트 싱크

- 모든 등장 시각은 8분음표(0.25초) 격자에, 글자 하나하나는 16분·32분음표 격자에 맞춰요. 글자와 블록은 떨어져서 **바닥에 닿는 순간이 박자**예요
- 계속 움직이는 펄스는 없고, 등장·착지·도장·폭발·장면 전환 순간에만 한 번씩 쿵(흔들림 + 짧은 줌 펀치) 쳐요
- `node tools/export_events.mjs`가 영상에서 등장·착지 시각을 뽑아 `tools/events.json`에 저장하고, `tools/make_audio.py`가 그 시각에 효과음을 놓아요. 화면을 고친 뒤 이 두 단계를 다시 돌리면 소리도 자동으로 맞춰져요

## 수정·렌더링

문구와 타이밍은 `index.html`의 `s1`~`s7`에, 사운드는 `tools/make_audio.py`에 있습니다.

```bash
npm install && pip install numpy soundfile imageio-ffmpeg
node tools/export_events.mjs         # tools/events.json (화면의 박자 이벤트)
python3 tools/make_audio.py          # audio/mix.wav
export FFMPEG=$(python3 -c "import imageio_ffmpeg as i; print(i.get_ffmpeg_exe())")
node render.mjs                      # out/edu_platform_team.mp4
```
