# Nouns: One and More Than One (영어 명사·복수형 모션그래픽)

재능 미주영어 **D01** 교재의 학습 내용을 한 편의 영상으로 정리했어요. 1920×1080, 30fps, 약 2분 40초, 영어 내레이션과 자막이 들어가요.

| 장면 | 교재 쪽 | 내용 |
|---|---|---|
| What is a noun? | D1a, D5a | 명사는 사람·장소·사물의 이름 (teacher · school · desk), 문장에서 명사에 동그라미 |
| One and more than one | D5a, D5b | 단수 명사 / 복수 명사 (bunny → bunnies) |
| Rule 1 · add -s | D5b | dog → dogs, playground → playgrounds, baseball → baseballs |
| Rule 2 · add -es | D1b | -ch, -s, -x, -sh 로 끝나면 -es: church, bus, fox, dish |
| Rule 3 · y → ies | D2a | baby → babies, bunny → bunnies, city → cities / 예외 boy → boys, toy → toys |
| Rule 4 · f → ves | D2b | leaf → leaves, knife → knives, wolf → wolves |
| Irregular plurals | D3a, D9a | mouse → mice, man → men, woman → women, child → children, tooth → teeth, foot → feet, person → people |
| Same for one and many | D9b, D10a | fish, deer, moose, sheep |
| Quiz | D6a, D13 | puppy, box, foot 의 복수형 (3초 생각할 시간) |
| Great job | | 규칙 6가지 정리 |

- 그림: 교재 D01 삽화를 그대로 썼어요 (`img/`, 흰 바탕만 투명하게). 양은 교재에 그림이 없어 코드로 간단히 그렸어요
- 글꼴: [Fredoka](https://fonts.google.com/specimen/Fredoka)(제목·낱말), [Andika](https://software.sil.org/andika/)(문장·자막 — 처음 글을 배우는 어린이용 글꼴), 둘 다 OFL
- 복수형이 만들어지는 모습: 남는 부분은 그대로, 빠지는 글자(y, f, ouse…)는 빨갛게 떨어지고, 새로 붙는 글자는 하늘색으로 한 글자씩 들어와요
- 내레이션: Supertonic 3(sherpa-onnx, 온디바이스 소형 TTS) 영어 음성. 낱말 짝(Dog, dogs.)은 0.72배로 천천히, 뒤에 따라 말할 틈을 둠
- 효과음·배경음(잔잔한 우쿨렐레 느낌)은 `tools/make_audio.py`에서 합성 (외부 음원 없음)
- 시각: `tools/make_audio.py`가 문장마다 음성을 만들고 실제 길이로 `timeline.js`를 써요. 화면은 그 시각을 따라 움직여요

## 편집기

공용 영상 편집기(`../video-editor.html`)에서 이 영상의 장면을 넣고 빼거나, 화면 글자·자막·색을 고칠 수 있어요. 자막을 바꿔도 내레이션 음성은 그대로예요.

## 고치기·렌더링

- 내레이션 문장·예시 낱말·쉼: `tools/make_audio.py`의 `SCRIPT` (고친 뒤 다시 실행하면 `timeline.js`와 소리가 같이 바뀜)
- 화면 글자·색 기본값: `content.js`
- 장면 그림: `index.html`

```bash
npm install && pip install sherpa-onnx soundfile numpy scipy
TTS_MODEL_DIR=/path/to/sherpa-onnx-supertonic-3-tts-int8-2026-05-11 python3 tools/make_audio.py   # timeline.js, audio/mix.wav
export FFMPEG=$(python3 -c "import imageio_ffmpeg as i; print(i.get_ffmpeg_exe())")
node render.mjs                      # out/english_nouns.mp4
```
