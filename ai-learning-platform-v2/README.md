# JEI Math: An AI-Powered Personalized Learning Platform v2 (30쪽)

수학팀 장표 `AI 프로젝트 영상제작용.pdf`(AI 개인화 학습 플랫폼 프로젝트, 10쪽)와 그 마지막 쪽의 영문 대본(Final Video Narration Script, American English)으로 만든 영상이에요. 장표의 한글 문구는 대본에 맞춰 영어로 옮겼고, 화면은 `../adaptive-diagnosis-v2`·`../math-di-improvement-v2`와 같은 **모눈종이 워크북** 콘셉트로 새로 그렸어요.

**v2**: `../ai-learning-platform`(v1, 11쪽)과 대본·음성·색은 같고, 한 화면에 오래 머물지 않도록 **30쪽**으로 나눴어요(v1은 한 쪽 평균 50초, v2는 평균 19초, 가장 긴 쪽 31초). 문장마다 어느 쪽에 속하는지는 `tools/make_audio.py` 의 `PAGE`. 장면 사이 간격은 1.0초라 전체가 9분 52초예요.

- 내레이션: DGX의 Qwen3-TTS API(`qwen3-tts-api`, 포트 8095)에서 **Base(복제) 모델이 `audio/voice_ref.wav`(D–I 개선 내레이션 29초)를 따라** 대본 73문장을 한 문장씩 읽어요
- **모눈종이 워크북 한 장**: 장면마다 한 쪽(p. 1 ~ p. 30). 장면이 바뀔 때 종이 위를 옆으로 넘어가고(믹스의 휙 소리와 같은 때), 읽는 동안은 화면이 움직이지 않아요
- 선생님 펜 표시: 빨간 동그라미·체크·상자·화살표, 형광펜, 포스트잇, 도장(REVIEWED)
- 색: `수학 영상 컬러 개선.pdf`의 새 팔레트와 사용 기준을 따라요 (`content.js` 의 `colors`)
  - **레드 #E5303A가 메인**: 모든 섹션 태그, 핵심 숫자·강조 단어, 선생님 펜, 정답·완전학습(Mastered)
  - 비교할 때는 첫째 레드 → 둘째 블루 #2C64C8 → 셋째 민트 #32C2AD (Phase 1 레드 / Phase 2 블루 / LLM Wiki·확인 대상(Needs more practice) 민트)
  - 네이비 #0F2F57은 부정·오답·하락에만 (학습 결손, 오답 ✗). 그 밖의 어두운 칩·띠는 텍스트색 #383838
  - 덜 중요한 박스는 밝은 그레이 #F3F4F6, 배경은 중립 화이트 #FEFFFF, 형광펜은 블러시 #FDDCD6(곱하기로 칠해 글자가 비침), 포스트잇도 그레이
  - 작은 빨간 글자는 크림슨 #B81F2E, 흰 글씨 민트 칩은 민트 다크 #1E9C8A. 3계층 그림은 레드 한 가지 색의 진하기(블러시 → 라이트 레드 → 레드)로
- 1920×1080, 30fps. 글꼴은 macOS 시스템 글꼴 Avenir Next(본문)·Noteworthy(손글씨). 배경음악 없음 (내레이션 + 장면 전환 휙 소리, 끝인사 딩)
- 화면에 자막은 넣지 않아요 (내레이션만)

| p. | 장면 | 문장 | 구성 |
|---|---|---|---|
| 1 | title | l1_1 | 제목, "more than that: better learning products & services" |
| 2 | vision | l1_2–3 | 50 years, 학습설계 자산 → organized for AI → 인쇄 교재·POD·온라인 세 카드를 "one unified system"으로 |
| 3 | kmap | l2_1–3 | Point·Line 범례, 예시 경로 3단계(왼쪽)와 지도에서 동그라미 |
| 4 | kmapHow | l2_4–6 | 지도를 왼쪽으로 옮겨 굵은 선(직접 선수)·난이도 표시, AI가 전체 구조를 이해 |
| 5 | gather | l3_1–3 | 단계 띠(1 INPUT), 목표, JEI 학습설계 자산 4가지, 각국 교육과정 |
| 6 | analyze | l3_4–6 | 입력 → AI 비교·분석(similarities·differences) → 제안된 목표·연결, REVIEWED 도장, repeat → refine |
| 7 | expand | l3_7–8 | 새 자료가 들어와 자라는 지도, 국가별 연결(미국·한국·영국·호주·뉴질랜드) |
| 8 | layerK | l4_1–4 | 왼쪽 3계층 쌓기 + 지식 계층 상세(구조화, P-01·P-06) |
| 9 | layerA | l4_5–7 | AI 엔진 계층(단계별 콘텐츠 계단, 학습상태 분석·설명·힌트, P-02·04·05) |
| 10 | layerS | l4_8–11 | 서비스 계층(교재·POD·온라인·교사 지원), 결과 피드백 화살표, 하나의 공통 기반 |
| 11 | phases | l5_1–2 | Phase 1·2와 7개 과제 막대(장표의 개월 수), in parallel |
| 12 | phase1 | l5_3–4 | P-01·02·03 카드, CORE, 학습 순환 |
| 13 | phase2 | l5_5 | P-04·05·07 카드, CORE |
| 14 | wiki | l5_6–7 | LLM Wiki 허브와 6개 과제 |
| 15 | pod | l6_1–4 | POD 5단계 |
| 16 | podCycle | l6_5–6 | 5단계 순환 고리, 활용 형태 3가지 |
| 17 | behavior | l6_7–9 | 문제 푸는 화면(시간·힌트·재시도)과 학습행동 4가지 |
| 18 | loop | l6_10–11 | 온라인 4단계와 보충·복습·심화 |
| 19 | assistant | l6_12–13 | 학생(답 대신 힌트), 교사(진도·어려움 → 코칭) |
| 20–22 | statusMap · statuses · recommend | l7_1–9 | 같은 지식맵을 이어 쓰며 오른쪽만 바뀜: 3구역 → 4가지 상태 → 추천 경로·기준 포스트잇 |
| 23–26 | ben1–4 | l8_1–6 | 기대효과 한 쪽에 하나(1 2 3 4 진행 점), 마지막에 마무리 띠 |
| 27 | roadmap | l9_1–2 | 두 단계 화살표와 기간 |
| 28 | roadmapPhases | l9_3–5 | 단계별 결과물, POD 미국 → 한국 |
| 29 | roadmapAll | l9_6–7 | 전체 분기표: 분기마다 개선, LLM Wiki |
| 30 | outro | l10_1–3 | 50 years + AI → new approach, Thank you |

## 음성·시각표 만들기

- `tools/make_audio.py`: 대본(`SCRIPT`, 화면 문구와 같은 바른 문장 + 필요하면 읽는 문장), 장면 목록, 간격
  - 읽는 문장만 바꾼 곳: POD → "P-O-D", JEI-SLI → "J-E-I S-L-I", Phase 1/2 → "Phase One/Two", 18·2026~2028 → 숫자를 말로, JEI-Math → "JEI Math"
  - 문장마다 3번 읽혀(`N`) whisper large-v3-turbo(mlx-whisper)로 받아쓰고, 대본과 다르게 읽은 것을 빼고, 남은 것 중 말 빠르기가 가운데에 가깝고 중간에 긴 쉼이 없는 것을 골라요. 결과는 `audio/tts_cache/`에 남아서 문장을 고치면 그 줄만 다시 만들어요 (`--redo l3_2,l6_4` 로 다시 뽑기)
  - 문장 사이 0.45초, 장면 사이 1.1초(+문장별 쉼). 문장마다 소리 크기를 맞춰요
  - `timeline.js` 에 문장마다 **읽힌 단어와 그 시각**(`lines[id].words`)이 들어가요. 화면은 `W(문장, 단어)`로 그 단어가 읽히는 때에 맞춰 움직여요(못 찾으면 문장 안 비율로 대신하고 `tools/snap.mjs` 가 알려 줘요)
- 목소리를 바꾸려면 `audio/voice_ref.wav` 와 그 대사 `audio/voice_ref.txt` 를 바꾸고 다시 돌리면 돼요 (캐시 이름에 참조 음성이 들어가 있어 모두 새로 읽어요)

```bash
export FFMPEG=../math-di-improvement-v2/node_modules/ffmpeg-static/ffmpeg   # 아무 ffmpeg (whisper 는 PATH 의 ffmpeg 도 써요)
TTS_URL=http://192.168.51.8:8095 uv run --with mlx-whisper python tools/make_audio.py   # timeline.js, audio/mix.wav
```

## 고치기·렌더링

- 장면: `index.html` 의 `SC.intro` ~ `SC.outro`, 제목·마무리 문구와 색: `content.js` (영상 편집기에서도 수정 가능)
- 미리보기: `index.html` (재생 막대), `index.html?t=120` (그 시각)

```bash
npm install
node tools/snap.mjs out/snaps --ends            # 장면마다 다 그려진 때의 정지 화면 + 못 찾은 큐 단어
export CHROMIUM="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"   # macOS
export FFMPEG=../math-di-improvement-v2/node_modules/ffmpeg-static/ffmpeg         # PATH 에 ffmpeg 가 없으면
node render.mjs --workers 6                      # out/ai_learning_platform_v2.mp4 (브라우저 6개가 나눠 그려요)
```
