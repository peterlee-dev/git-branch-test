# 호박공주와 두리안 왕자 (과일 나라 동화 · 캐릭터 애니메이션)

호박나라 호박공주님이 연 파티에 옆 나라 수박공주님이 오자 모두 수박공주님 곁으로 몰려가요. 부러운 호박공주님은 몸에 수박처럼 초록 줄무늬를 그리고, 멋진 왕자님들이 다가오지요. 그런데 비가 와서 줄무늬가 지워지고, 과일 친구들이 "호박에 줄 긋는다고 수박 되나?" 하고 놀려요. 슬퍼하는 공주님에게 두리안 왕자님이 우산을 씌워 주며 "줄을 긋지 않아도 아름다워요" 하고 말해 주고, 둘은 결혼해서 행복하게 살아요.

- 3분 이내, 1920×1080, 30fps. 폰트: Jua(주아체) · Noto Sans KR (SIL OFL)
- 캐릭터는 코드로 그린 유아용 TV 애니메이션 스타일(과일 몸통에 얼굴, 가는 팔다리, 부분마다 진한 색 테두리, 바닥 그림자)
  - 호박공주(호박 골 무늬, 꼭지, 리본), 수박공주(물결 줄무늬), 사과 왕자·포도 왕자(망토), 바나나, 딸기, 두리안 왕자(가시, 망토, 나비넥타이)
- 모두 움직여요: 대사 소리 크기에 맞춰 입이 벌어지고, 눈을 깜빡이고, 들썩이며 걷고, 춤추고, 웃고, 울어요. 붓질하면 줄무늬가 한 줄씩 생기고, 비가 오면 흘러내리며 지워져요. 거울 속 모습도 같이 움직여요
- 목소리: Qwen3-TTS (Apache 2.0). VoiceDesign 모델로 캐릭터마다 기준 목소리를 지어낸 뒤(내레이터·호박공주·수박공주·사과 왕자·포도 왕자·바나나·딸기·두리안 왕자), Base 모델로 그 목소리를 복제해 모든 대사를 읽어서 한 캐릭터의 목소리가 끝까지 같아요
- 효과음(팡파르, 붓질, 반짝임, 천둥, 빗소리, 우산, 결혼식 종)과 장면마다 다른 오르골 배경음(파티 왈츠, 비 오는 단조, 결혼식)은 `tools/make_audio.py`에서 합성

| 장면 | 내용 |
|---|---|
| 호박나라 | 호박 성 앞의 호박공주님, 초대장을 날려 보냄 |
| 파티 | 친구들이 오고, 팡파르와 함께 수박공주님 등장 → 모두 그쪽으로 |
| 줄무늬 그리기 | 방에서 붓으로 초록 줄무늬 (거울에도 비침) "짜잔!" |
| 줄무늬 공주 | 왕자님들이 다가와 함께 춤 |
| 비 | 천둥·비, 줄무늬가 흘러내려 지워짐, 놀림 "호박에 줄 긋는다고 수박 되나?" |
| 두리안 왕자 | 우산을 씌워 주며 "줄을 긋지 않아도 아름다워요", 비가 그치고 무지개 |
| 결혼식 | 꽃 아치 아래 결혼식, 친구들이 축하 |

## 고치기·렌더링

- 대사·장면 순서: `tools/make_audio.py`의 `SCRIPT` (다시 실행하면 `timeline.js`와 소리가 같이 바뀌고, 바뀐 줄만 다시 만들어요)
- 목소리 느낌: `VOICES`의 설명 문장 (바꾸면 그 캐릭터 대사를 모두 다시 만들어요)
- 캐릭터·움직임: `index.html`의 `fruitBody`(캐릭터), `sCastle` ~ `sWedding`(장면별 동작)
- 영상 편집기(`../video-editor.html`)에서 제목·자막·색을 바꿀 수 있어요

```bash
npm install && pip install torch qwen-tts soundfile numpy
QWEN_DESIGN_DIR=/path/Qwen3-TTS-12Hz-1.7B-VoiceDesign QWEN_BASE_DIR=/path/Qwen3-TTS-12Hz-1.7B-Base python3 tools/make_audio.py
export FFMPEG=$(python3 -c "import imageio_ffmpeg as i; print(i.get_ffmpeg_exe())")
node render.mjs        # out/pumpkin_princess.mp4
```

## 영어판 (English version)

같은 장면·움직임에 영어 대사와 영어 목소리를 입힌 버전이에요. 대사는 `tools/make_audio.py`의 `LINES_EN`, 목소리 설명은 `VOICES_EN`(원어민 미국 영어 발음)에서 고쳐요.

```bash
VIDEO_LANG=en QWEN_DESIGN_DIR=... QWEN_BASE_DIR=... python3 tools/make_audio.py   # timeline_en.js, audio/mix_en.wav
node render.mjs --lang en                                                         # out/pumpkin_princess_en.mp4
```

미리보기는 `index.html?lang=en`. 제목·놀림 자막·이름표가 영어로 바뀌고, 긴 영어 자막은 두 줄로 나와요.
