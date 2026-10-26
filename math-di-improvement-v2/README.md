# JEI Math Grades D–I Improvement Plan v2 (TTS 내레이션 · 새 대본)

복제 목소리 TTS로 새로 만든 영문 내레이션(`source/di_tts.wav`, 대본 `수학상품소개 대본.pdf` 그대로 읽은 한 파일)을 문장별로 잘라 다시 배치하고, 화면을 그 대본에 맞춘 버전이에요. `../math-di-improvement`(v1)과는 대본·음성이 달라요.

- 콘셉트: **모눈종이 워크북 한 장**. 장면마다 한 쪽(p. 1 ~ p. 18)이고, 장면이 바뀔 때 종이 위를 옆으로 미끄러지듯 넘어가요. 읽는 동안에는 화면이 움직이지 않아요(카메라 줌 없음)
- 선생님 펜 표시: 빨간 동그라미·체크·밑줄, 형광펜, 포스트잇, 도장(LESS FATIGUE, MASTERY)
- 색(2026-10-22, `수학 영상 컬러 개선.pdf`): 흰 바탕 위에 레드 `#E5303A` 하나를 메인으로(긍정·상승·체크·정답, 비교군 1번째, 섹션 태그·핵심 숫자), 네이비 `#0F2F57` 는 부정·감소·오답, 블루 `#2C64C8`·민트 `#32C2AD` 는 비교군 2·3번째, 나머지는 그레이. 글자 `#383838`, 형광펜은 연한 블러시. 팔레트는 `index.html` 의 `K`, 학년 타일(D→I 그레이→레드)은 `GRADE_COLS`
- 1920×1080, 30fps, 약 5분 15초. 글꼴은 macOS 시스템 글꼴 Avenir Next(본문)와 Noteworthy(손글씨). 다른 OS에서 렌더하면 대체 글꼴로 바뀌어요
- 자막은 영상에 넣지 않았어요. 필요하면 `subtitles.srt` 를 함께 쓰세요
- 용어: 대본을 따라 **main textbook**

| p. | 장면 | 화면 |
|---|---|---|
| 1 | intro | 제목 형광펜, D~I 학년 카드, 안내 3줄 체크(개선 방향 셋 · 학년별 변화 · 보충 자료 활용) |
| 2 | priority | 학년별 회원 막대, D~I ≈ 80 %, JEI 학습 구조를 바탕으로 한 최우선 학년, 목표 2개(CCSS 정합성 · 학습자 경험) |
| 3 | roadmap | JEI 네 단계 계단 위에 "Review CCSS Alignment — Timing · Progression · Coverage" 노란 상자, 상자에서 각 단계로 화살표 (수정 1) |
| 4 | standards | JEI 로드맵 + U.S. 학년 기준 → 정합성 강화 → 적시성(시계) · 완결성(채워지는 고리) |
| 5 | gradeD | 8 + 4 = 7 + 5 저울, 토끼 세 수 문장제(5 + 2 − 3) |
| 6 | gradeI | 모눈 위 좌표평면(NEW), 정수 비교, 절댓값, 더 높은 개념으로 |
| 7 | synergy | JEI’s Strong Learning System + Local Curriculum (U.S.) → A Closer Connection → 학년 사이 자연스러운 흐름 D→I, 아래 띠 (수정 2) |
| 8 | workbook | 기존 쪽(12~24 계산 연습 문항 중 5문항에만 빨간 줄, 연습·숙달 기회) → 다시 짠 main textbook 쪽(개념·핵심 목표·풀이 공간) (수정 4) |
| 9 | supp | 반복 문항 → 세트별 맞춤 보충 자료, 센터가 학생마다 필요한 만큼 유연하게 활용(학생 셋, 보충 자료 장수가 서로 다름). 운영 방식(다운로드·인쇄·제공)은 확정되지 않아 뺐어요 (수정 5) |
| 10 | mastery | main textbook + 보충 자료 = 완전 학습 도장 |
| 11 | sequence | JEI 개념 구조(큰 계단 3칸) → 더 잘게 나눈 계단 7칸, 방정식·분수·소수로 |
| 12 | gradeF | 똑같이 나누기 → 1/4, □ + 3 = 7 → x + 3 = 7(학년에 맞춰 차근차근), 방정식의 직관적 이해 |
| 13 | gradeGH | 기하 그림만: 눈금 수직선, 색이 다른 직사각형 두 개(넓이 모델), 둥근 네모 세 개(묶음 모델) (수정 3) |
| 14 | gradeI2 | 식 → 표 → 그래프 |
| 15 | cycle | 진단평가·시스템 데이터 재설계, 진단(학생별 출발점) → 처방(맞춤 보충 자료) → 학습, 더 완전한 학습 순환 |
| 16 | scope | 221세트 모눈: 140 유지, 81 개정·보강, +5 신규 |
| 17 | package | 학년마다 하나의 통합 패키지(main textbook · 시스템 데이터 · 보충 자료) |
| 18 | outro | 정리 2줄, Thank you |

이전 녹음판에 있던 suppSets(보충 자료 81세트 학년별)·schedule(개발 일정) 쪽과 63.3 %·CCSS 코드 +39·226세트·2027년 6월 목표는 새 대본에 없어 뺐어요.

## 음성·시각표 만들기

- 대본: `narration.py` 의 `SCENES`. 장면별 문장(자막에 쓰는 바른 문장, ` | ` 는 자막을 나누는 자리)과 화면 큐 `(이름, 문장 번호, 기준 구절)`
- `python3 build_audio.py` (numpy 필요) → `narration.wav`(44.1 kHz 모노), `timeline.js`, `timeline.json`, `subtitles.srt`, `source/clips.txt`(문장별 원본 구간 → 새 구간)
  - 문장 경계: `source/di_tts_words.json`(whisper large-v3-turbo 단어 받아쓰기, mlx-whisper)으로 문장 첫·끝 단어를 찾고, 그 사이 가장 긴 무음에서 자름(앞 0.05 s · 뒤 0.10 s 여유)
  - 받아쓰기가 쉼을 다음 단어에 붙인 경우(단어 구간 안에 0.15 s 넘는 무음)는 단어 시작을 무음 끝으로 옮겨요
  - 배치 간격은 v1 `build_audio.py` 와 같아요: 첫 장면 전 0.8 s, 장면 시작 → 첫 문장 1.0 s, 문장 사이 0.4 s, 장면 끝 0.9 s(장면별 `tail`), 큐는 그 단어가 말해지기 0.15 s 전
- supp 장면 둘째 문장("…centers will be able to use these materials flexibly according to individual learning needs.")은 대본 수정으로 따로 다시 만들었어요(2026-10-22). DGX `qwen3-tts-api` 에서 처음 TTS와 같은 참조 음성(`D~I 개선.mp3` 앞 15초)으로 후보 8개를 만들고, 받아쓰기가 대본과 같은 것 중 원래 목소리와 가장 닮은 것(화자 유사도 0.870, 기존 문장 0.879)을 1.05배속으로 골랐어요(`source/supp_new.wav`·`supp_new.json`). `python3 source/splice_supp.py` 가 원본(`source/di_tts_orig.wav`·`di_tts_words_orig.json`)의 옛 문장 자리에 끼워 `di_tts.wav`·`di_tts_words.json` 을 만들어요
- TTS는 기본 속도판(4분 47초)을 썼어요. 같은 폴더의 1.0배속판(5분 00초)으로 바꾸려면 `source/di_tts.wav` 를 바꾸고 받아쓰기를 다시 한 뒤 `build_audio.py` 를 돌리세요
- `narration.wav`·`source/di_tts.wav` 와 `out/` 은 저장소에 올리지 않으니 받은 뒤 `build_audio.py` 를 한 번 돌리세요

## 고치기·렌더링

- 장면별 화면: `index.html` 의 `S.intro` ~ `S.outro`. 모든 움직임이 `timeline.js` 의 큐(장면 시작부터의 초)에 묶여 있어요. 장면 순서는 `narration.py` 순서를 따라요(쪽 번호도 자동)
- 미리보기: `index.html?fit` (창에 맞춤), `?play` (내레이션과 함께 재생), `?t=120` (그 시각으로 이동)

```bash
npm install
python3 build_audio.py               # narration.wav · timeline.js · subtitles.srt
node render.js stills 10,60,200     # stills/*.png
node render.js video out/math_di_improvement_v2.mp4 4   # 작업자 4개로 병렬 렌더 → 깨진 프레임 검사
node render.js patch 이전영상.mp4 out/math_di_improvement_v2.mp4 44-60,84-91.6   # 고친 구간(초)만 다시 렌더해 이전 영상에 끼움(오디오는 이전 영상 그대로)
```
