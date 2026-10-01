# 동물 관찰 일기 (재능스스로과학 F01 · 종이공예 모션그래픽)

재능스스로과학 **F01** 교재의 학습 내용을 종이공예(페이퍼 컷아웃) 느낌의 영상으로 정리했어요. 1920×1080, 30fps, 약 3분, 한국어 내레이션·자막·효과음·배경음이 들어가요.

| 장면 | 교재 쪽 | 내용 |
|---|---|---|
| 동물 관찰 일기 | 표지, 학습목표 | 몸 색깔 · 움직임 · 빠르기 · 필요한 것 |
| 1. 몸 색깔과 생김새 | F1b–F4a | 풀숲에 숨은 메뚜기 찾기, 메뚜기·청개구리, 자벌레·대벌레(나뭇가지), 으름덩굴큰나방(낙엽), **보호색**, 고등어의 푸른 등 |
| 2. 동물의 움직임 | F4b–F6b | 다리(호랑이·기린), 날개(독수리·잠자리), 지느러미(붕어·돌고래), 기어다니기(지렁이·뱀), 팔과 다리(원숭이) |
| 3. 동물의 빠르기 | F7b–F9b | 달리기 시합: 치타 > 사자 > 캥거루 > 기린, 타조의 두 다리, 사냥과 도망 |
| 4. 살아가는 데 필요한 것 | F10b–F12b | 먹이·물·공기·집, 두더지·딱따구리·제비·청둥오리의 집 |
| 정리 | | 네 가지 정리, 참 잘했어요 도장 |

- 사진·그림: 교재 F01의 사진과 삽화를 테이프로 붙인 사진 카드로 썼어요 (`img/`)
- 종이 표현: 종이결 텍스처, 겹친 종이 그림자, 가위로 오린 가장자리, 종이가 밀려 지나가는 장면 전환, 15fps 스톱모션 (광합성 영상과 같은 방식)
- 단원 색은 교재처럼 1단원 보라, 2단원 연두, 3단원 주황, 4단원 분홍
- 폰트: Jua(주아체) + Noto Sans KR, SIL OFL
- 내레이션: Qwen3-TTS 1.7B CustomVoice(Alibaba Qwen, Apache 2.0)의 한국어 목소리 Sohee. 말투는 `QWEN_INSTRUCT`(다정하고 또박또박)로 지정. 예전 Supertonic 3 음성은 `TTS_ENGINE=supertonic`으로 다시 쓸 수 있어요. 효과음(종이 소리, 출발 호루라기 등)과 배경음(잔잔한 마림바)은 `tools/make_audio.py`에서 합성
- 시각: `tools/make_audio.py`가 문장마다 음성을 만들고 실제 길이로 `timeline.js`를 써요

## 편집기

공용 영상 편집기(`../video-editor.html`)에서 이 영상의 장면을 넣고 빼거나, 화면 글자·자막·색을 고칠 수 있어요. 자막을 바꿔도 내레이션 음성은 그대로예요.

## 고치기·렌더링

- 내레이션 문장·쉼: `tools/make_audio.py`의 `SCRIPT` (다시 실행하면 `timeline.js`와 소리가 같이 바뀜)
- 화면 글자·색 기본값: `content.js`
- 장면 그림: `index.html`의 `sIntro` ~ `sEnd`

```bash
npm install && pip install torch qwen-tts soundfile numpy
# 모델(약 4.3GB): Hugging Face Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice
QWEN_MODEL_DIR=/path/to/Qwen3-TTS-12Hz-1.7B-CustomVoice python3 tools/make_audio.py   # timeline.js, audio/mix.wav
# CPU 에서는 한 줄에 1분 남짓(37줄 약 40분). 만든 음성은 audio/tts_cache/ 에 남아서 바뀐 줄만 다시 만들어요
export FFMPEG=$(python3 -c "import imageio_ffmpeg as i; print(i.get_ffmpeg_exe())")
node render.mjs                      # out/science_animals.mp4 (종이 질감 때문에 GPU 없는 환경에서 약 50분)
```
