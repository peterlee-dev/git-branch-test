# JEI Math Grades D–I Improvement Plan v2 (같은 내레이션 · 새 화면)

`../math-di-improvement` 와 같은 영문 내레이션(사내 TTS)과 큐 시각을 그대로 쓰고, 화면만 새로 만든 버전이에요.

- 콘셉트: **모눈종이 워크북 한 장**. 장면마다 한 쪽(p. 1 ~ p. 18)이고, 장면이 바뀔 때 종이 위를 옆으로 미끄러지듯 넘어가요. 읽는 동안에는 화면이 움직이지 않아요(카메라 줌 없음)
- 선생님 펜 표시: 빨간 동그라미·체크·밑줄, 형광펜, 포스트잇, 도장(LESS FATIGUE, MASTERY)
- 1920×1080, 30fps. 글꼴은 macOS 시스템 글꼴 Avenir Next(본문)와 Noteworthy(손글씨). 다른 OS에서 렌더하면 대체 글꼴로 바뀌어요
- 자막은 영상에 넣지 않았어요(원본과 같음). 필요하면 `subtitles.srt` 를 함께 쓰세요

| p. | 장면 | 화면 |
|---|---|---|
| 1 | intro | 제목 형광펜, D~I 학년 카드, 안내 3줄 체크 |
| 2 | priority | 학년별 회원 막대, D~I ≈ 80 %, 목표 2개 체크 |
| 3 | roadmap | JEI 작은 단계 계단 vs CCSS 진행(빨간 점선), 어긋나는 곳 ≠ |
| 4 | align | CCSS 2.MD.A.1~4 와 JEI 로드맵, 빠진 내용 추가 |
| 5 | gradeD | 8 + 4 = 7 + 5 저울, 토끼 세 수 문장제 |
| 6 | gradeI | 모눈 위 좌표평면, 정수 비교, 절댓값 |
| 7 | synergy | JEI 체계 ↔ 현지 교육과정, D→I 연결 |
| 8 | workbook | 지금 쪽(12~24문항) → 다시 짠 핵심 교재 쪽 |
| 9 | supp | 반복 연습 → 세트별 보충 자료, 센터 다운로드·인쇄·제공 |
| 10 | mastery | 핵심 교재 + 보충 자료 = 완전 학습 도장 |
| 11 | sequence | 큰 계단 3칸 → 작은 계단 7칸 |
| 12 | gradeF | 똑같이 나누기 → 1/4, □ → x |
| 13 | gradeGH | 수직선(어림), 넓이 모델(×), 묶음 모델(÷) |
| 14 | gradeI2 | 식 → 표 → 그래프 |
| 15 | cycle | 시스템 데이터 위의 진단 → 처방 → 학습 순환 |
| 16 | scope | 221세트 모눈: 140 유지, 81 개정, +5 신규 = 226 |
| 17 | package | 학년마다 한 묶음 |
| 18 | outro | 정리, Thank you |

## 고치기·렌더링

- 장면별 화면: `index.html` 의 `S.intro` ~ `S.outro`. 모든 움직임이 `timeline.js` 의 큐(장면 시작부터의 초)에 묶여 있어요
- 대본·음성을 바꾸면 `../math-di-improvement` 에서 `build_audio.py` 를 다시 돌린 뒤 `timeline.js`, `timeline.json`, `subtitles.srt`, `narration.wav` 를 이 폴더로 복사하세요
- 미리보기: `index.html?fit` (창에 맞춤), `?play` (내레이션과 함께 재생), `?t=120` (그 시각으로 이동)

```bash
npm install
node render.js stills 10,60,200     # stills/*.png
node render.js video out/math_di_improvement_v2.mp4 6   # 작업자 6개로 병렬 렌더 → 깨진 프레임 검사
```
