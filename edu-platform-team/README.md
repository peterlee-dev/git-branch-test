# 재능교육 교육플랫폼팀 30초 홍보 영상

- 30초, 1920×1080, 30fps. 다크 톤 테크 모션그래픽 + 재능교육 레드 포인트
- 폰트: Noto Sans KR · Inter · JetBrains Mono (코드), 모두 SIL OFL 라이선스로 `fonts/`에 포함
- 사운드: 120BPM 비트 + 타건음·글리치·효과음을 `tools/make_audio.py`에서 합성 (외부 음원 없음). 장면 전환은 마디(2초)에 맞춤

| 시간 | 장면 | 내용 |
|---|---|---|
| 0–4s | 인트로 | 터미널에 `npm run edu-platform-team` 타이핑 → "교육의 내일을 만드는 사람들" |
| 4–8s | 파이프라인 | 연구원 → **저작도구** → 콘텐츠 → 교육 서비스, 데이터가 흐르는 연결선 |
| 8–12s | 저작도구 | 연구원용 편집기 목업. 문제·보기·정답·해설 블록을 끌어와 문항 완성 → 발행 |
| 12–16s | 양산 | 카드 한 장이 수많은 카드로 퍼짐. "하나를 만들면, 수많은 아이들의 학습으로." |
| 16–20s | 웹 + 앱 | 브라우저와 휴대폰에 같은 학습 화면, 진도가 함께 채워짐 |
| 20–25s | AI | 프롬프트 입력 → 문항 5개와 해설 생성, 신경망 모티프 |
| 25–30s | 엔딩 | 교육의 미래를, 코드로. · 재능교육 교육플랫폼팀 |

참고: [재능e아카데미 회사소개](https://it.jei.com/about/), [팀문화](https://it.jei.com/culture/) (검색 결과로 확인. 작업 환경에서 사이트 직접 접속은 차단됨)

## 수정·렌더링

문구와 타이밍은 `index.html`의 `s1`~`s7`에, 사운드는 `tools/make_audio.py`에 있습니다.

```bash
npm install && pip install numpy soundfile imageio-ffmpeg
python3 tools/make_audio.py          # audio/mix.wav
export FFMPEG=$(python3 -c "import imageio_ffmpeg as i; print(i.get_ffmpeg_exe())")
node render.mjs                      # out/edu_platform_team.mp4
```
