# JEI Math: An AI-Powered Personalized Learning Platform (모눈종이 워크북)

수학팀 장표 `AI 프로젝트 영상제작용.pdf`(AI 개인화 학습 플랫폼 프로젝트, 10쪽)와 그 마지막 쪽의 영문 대본(Final Video Narration Script, American English)으로 만든 영상이에요. 장표의 한글 문구는 대본에 맞춰 영어로 옮겼고, 화면은 `../adaptive-diagnosis-v2`·`../math-di-improvement-v2`와 같은 **모눈종이 워크북** 콘셉트로 새로 그렸어요.

- 내레이션: DGX의 Qwen3-TTS API(`qwen3-tts-api`, 포트 8095)에서 **Base(복제) 모델이 `audio/voice_ref.wav`(D–I 개선 내레이션 29초)를 따라** 대본 73문장을 한 문장씩 읽어요
- **모눈종이 워크북 한 장**: 장면마다 한 쪽(p. 1 ~ p. 11). 장면이 바뀔 때 종이 위를 옆으로 넘어가고(믹스의 휙 소리와 같은 때), 읽는 동안은 화면이 움직이지 않아요
- 선생님 펜 표시: 빨간 동그라미·체크·상자·화살표, 형광펜, 포스트잇, 도장(REVIEWED)
- 색: `수학 영상 컬러 개선.pdf`의 새 팔레트와 사용 기준을 따라요 (`content.js` 의 `colors`)
  - **레드 #E5303A가 메인**: 모든 섹션 태그, 핵심 숫자·강조 단어, 선생님 펜, 정답·완전학습(Mastered)
  - 비교할 때는 첫째 레드 → 둘째 블루 #2C64C8 → 셋째 민트 #32C2AD (Phase 1 레드 / Phase 2 블루 / LLM Wiki·확인 대상(Needs more practice) 민트)
  - 네이비 #0F2F57은 부정·오답·하락에만 (학습 결손, 오답 ✗). 그 밖의 어두운 칩·띠는 텍스트색 #383838
  - 덜 중요한 박스는 밝은 그레이 #F3F4F6, 배경은 중립 화이트 #FEFFFF, 형광펜은 블러시 #FDDCD6(곱하기로 칠해 글자가 비침), 포스트잇도 그레이
  - 작은 빨간 글자는 크림슨 #B81F2E, 흰 글씨 민트 칩은 민트 다크 #1E9C8A. 3계층 그림은 레드 한 가지 색의 진하기(블러시 → 라이트 레드 → 레드)로
- 1920×1080, 30fps. 글꼴은 macOS 시스템 글꼴 Avenir Next(본문)·Noteworthy(손글씨). 배경음악 없음 (내레이션 + 장면 전환 휙 소리, 끝인사 딩)
- 화면에 자막은 넣지 않아요 (내레이션만)

| p. | 장표 | 장면 | 구성 |
|---|---|---|---|
| 1 | 1 | intro | 제목 형광펜, "AI to work more efficiently → more than that: better learning products & services", 50 years, 인쇄 교재·POD·온라인 학습 세 카드를 펜으로 묶어 "one unified system" |
| 2 | 2 | kmap | Point · Line · Weight·color 범례, 예시 지도(한 자리 수의 덧셈 → 합 18 이내 덧셈 → 받아올림 있는 두 자리 수 덧셈을 읽는 단어에 동그라미), 학습목표마다 난이도 점, 3가지 특징 |
| 3 | 3 | build | STEP 1 입력 → ① AI 비교·분석 → STEP 2 JEI 공통 지식맵 → ② 지역·목적별 대응 → STEP 3 국가·지역별 지식맵, REVIEWED 도장, repeat → refine 고리, + NEW RESOURCES |
| 4 | 4 | layers | 지식 → AI 엔진 → 서비스 3계층을 아래에서부터, 과제 번호(P-01~P-07), 서비스→AI 엔진 피드백 화살표, "one shared knowledge foundation" |
| 5 | 5 | phases | Phase 1(P-01·02·03) / Phase 2(P-04·05·07), 병렬 착수 밑줄, ★ CORE, P-06 LLM Wiki가 양쪽을 받침 |
| 6 | 6 왼쪽 | pod | 개인별 맞춤 POD 5단계(진단·이력 → 학습목표·분량 → AI 콘텐츠 → 연구원 검토 → POD 출력·학습)와 되돌림 고리, 활용 형태 3가지 |
| 7 | 6 오른쪽 | online | 학습행동 4가지(정오답·풀이시간·힌트·재시도), 온라인 4단계 고리, AI 지원(학생·교사) |
| 8 | 7 | status | 3구역(미학습·현재 학습·지나온 경로)으로 자라는 지식맵(장표의 보고서 이미지 대신 그린 개념도), 네 가지 상태 색, 결손 동그라미, 추천 경로, 기준은 별도 개발 포스트잇 |
| 9 | 8 | benefits | 기대효과 4가지 카드, 마무리 띠 |
| 10 | 9 | roadmap | 2026 4Q ~ 2028 4Q 분기표: Phase 화살표, 핵심 서비스(US → Korea), 분기마다 개선 동그라미, P-06 LLM Wiki |
| 11 | 10 | outro | 50 years of learning design + AI → A new approach to personalized learning, Thank you |

장표 6쪽은 대본이 13문장이라 POD(Phase 1)와 온라인(Phase 2) 두 쪽으로 나눴어요.

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
node render.mjs --workers 6                      # out/ai_learning_platform.mp4 (브라우저 6개가 나눠 그려요)
```
