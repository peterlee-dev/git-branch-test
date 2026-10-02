# 사내 TTS로 내레이션 만들기 (회사 PC + 클라우드 나눠서)

사내 TTS API(`/editor/sound/tts`)는 회사 PC에서만 닿아요. 그래서 **음성만 회사 PC에서 만들고**, 영상 조립·렌더는 지금처럼 클라우드(또는 아무 PC)에서 해요.

쓸 수 있는 영상: `science-animals`, `photosynthesis`, `math-100`, `pythagoras` (한국어), `english-nouns` (영어)

## 회사 PC에서 (처음 한 번)

1. 이 저장소를 받고 작업 브랜치로 가요
   ```bash
   git clone https://github.com/peterlee-dev/git-branch-test.git && cd git-branch-test
   git checkout claude/jaenung-promo-video-n91oud
   ```
2. `tools/jei_tts.example.json`을 `tools/jei_tts.local.json`으로 복사해서 채워요. 이 파일은 저장소에 올라가지 않아요 (토큰은 여기에만)
   - `url`: `https://<사내 서버>/editor/sound/tts`
   - `headers`: 인증이 필요하면 헤더 (예: `{"Authorization": "Bearer ..."}`), 필요 없으면 `{}`
   - `type`: 입력 타입의 텍스트 값 (API 문서의 Enum 중 텍스트 쪽)
   - `voice`: 음성 번호 (예: 10)
   - `modeldivision`: 모델 언어 값. 한국어 영상은 `ko`, 영어 영상은 `en` 자리의 값을 써요
3. 한 문장으로 설정을 확인해요 → `tools/jei_tts_test.mp3`를 들어 보세요
   ```bash
   python3 tools/jei_tts.py --test "안녕, 친구들! 오늘은 동물 관찰 일기를 함께 써 볼 거예요."
   ```

파이썬 3만 있으면 돼요 (추가 설치 없음).

## 영상 하나 만들 때

```bash
git pull
python3 tools/jei_tts.py science-animals          # <영상>/voice/script.json 의 문장 중 빠진 것만 만듦
git add science-animals/voice && git commit -m "과학 F01 사내 TTS 음성" && git push
```

- 문장 목록(`voice/script.json`)은 클라우드에서 대본을 고칠 때마다 다시 만들어 올려 둬요
- 목소리 번호를 바꿨다면 `--voice 12 --force`로 전부 다시 만들어요

## 영상 조립 (클라우드)

```bash
TTS_ENGINE=jei python3 science-animals/tools/make_audio.py   # 음성 길이로 timeline.js, audio/mix.wav
node science-animals/render.mjs
```

음성이 빠진 문장이 있으면 시각표·소리 파일을 건드리지 않고 멈추고, 빠진 문장을 `voice/script.json`에 적어요.

## 파일

- `tools/jei_tts.py`: 회사 PC에서 사내 TTS를 부르는 스크립트
- `tools/voicebank.py`: 영상의 `make_audio.py`가 `TTS_ENGINE=jei`일 때 PC에서 만든 음성(`<영상>/voice/<문장키>.mp3`)을 읽게 해 주는 모듈. 문장키는 문장 글자의 해시라서, 문장을 고치면 그 줄만 다시 만들면 돼요
