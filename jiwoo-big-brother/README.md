# 지우의 형아 되기 (호기심 TV 이야기 · 캐릭터 애니메이션)

엄마 아빠가 아기 동생만 챙겨서 서운한 지우가 꿈별 요정의 마법으로 아기가 되어 보고, 아기는 힘든 게 많다는 걸 알게 된 뒤 다시 형아로 돌아와 동생을 돌봐 주는 이야기예요. 교재 2~3쪽(지우네 가족: 엄마, 아빠, 아기 동생)의 그림을 바탕으로 캐릭터를 다시 그렸어요.

- 약 2분 45초, 1920×1080, 30fps. 폰트: Jua(주아체) · Noto Sans KR (SIL OFL)
- 캐릭터는 코드로 그린 그림책 스티커 스타일(흰 테두리). 모두 움직여요: 대사 소리 크기에 맞춰 입이 벌어지고, 눈을 깜빡이고, 숨 쉬듯 들썩이고, 걷고, 기고, 넘어지고, 울고, 웃고, 요정은 날갯짓하며 날아다녀요. 카메라는 말하는 사람 쪽으로 천천히 다가가요
- 목소리: Qwen3-TTS (Apache 2.0). VoiceDesign 모델로 캐릭터마다 기준 목소리를 지어낸 뒤(지우·엄마·아빠·꿈별 요정·아기·내레이터), Base 모델로 그 목소리를 복제해 모든 대사를 읽어서 한 캐릭터의 목소리가 끝까지 같아요
- 효과음(요정 반짝임, 마법, 콩 넘어짐, 딸랑이)과 장면마다 분위기가 다른 오르골 배경음은 `tools/make_audio.py`에서 합성

| 장면 | 내용 |
|---|---|
| 바쁜 엄마 아빠 | 엄마는 우유, 아빠는 기저귀. "나도 아기가 되면 좋겠다!" |
| 꿈별 요정 | 밤, 요정이 날아와 "반짝반짝, 아기가 되어라! 얍!" |
| 아기가 된 지우 | 말 대신 "응애", 과자 대신 우유, 걷지 못해 기다가 콩, 낮잠 |
| 요정과 다시 | "아기는 힘든 게 정말 많아요… 동생도 힘들었겠다" |
| 형아가 된 지우 | 우는 동생에게 딸랑이로 까꿍, 동생이 까르르. 엄마 아빠 칭찬 |
| 끝 | "지우는 동생을 아끼는 멋진 형아가 되었답니다." |

## 고치기·렌더링

- 대사·장면 순서: `tools/make_audio.py`의 `SCRIPT` (다시 실행하면 `timeline.js`와 소리가 같이 바뀌고, 바뀐 줄만 다시 만들어요)
- 목소리 느낌: `VOICES`의 설명 문장 (바꾸면 그 캐릭터 대사를 모두 다시 만들어요)
- 캐릭터·움직임: `index.html`의 `drawChar`(캐릭터), `sHome` ~ `sEnd`(장면별 동작)
- 영상 편집기(`../video-editor.html`)에서 제목·자막·색을 바꿀 수 있어요

```bash
npm install && pip install torch qwen-tts soundfile numpy
QWEN_DESIGN_DIR=/path/Qwen3-TTS-12Hz-1.7B-VoiceDesign QWEN_BASE_DIR=/path/Qwen3-TTS-12Hz-1.7B-Base python3 tools/make_audio.py
export FFMPEG=$(python3 -c "import imageio_ffmpeg as i; print(i.get_ffmpeg_exe())")
node render.mjs        # out/jiwoo_big_brother.mp4
```
