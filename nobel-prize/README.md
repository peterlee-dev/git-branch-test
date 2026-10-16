# 노벨상이 궁금해요 (어린이 교양 설명 영상)

교원 빨간펜 QR 영상 「솔루토이 위인 노벨」(kyowonedu.com QR `9201900000195`, 2분 50초)을 참고해 **새로 만든** 영상이에요. 원본과 같은 순서로 같은 사실을 전하지만, 내레이션 문장·그림·시리즈 이름은 모두 새로 만들었어요(원본의 대본과 '지식콕' 이름은 쓰지 않았어요).

- 2분 52초, 1920×1080, 30fps. 글꼴: Jua(주아체)·Noto Sans KR (SIL OFL)
- 단색 배경의 플랫 일러스트 스타일. 인물(아인슈타인·김대중·밥 딜런·말랄라·노벨·마리 퀴리 등), 노벨 메달, 분야 아이콘, 지구본은 모두 `index.html`에서 코드로 그려요
- 목소리: Qwen3-TTS (Apache 2.0), DGX의 TTS API. VoiceDesign으로 지은 밝은 여성 내레이터 후보 4개 중 하나(`audio/voice_ref.wav`)를 골라 Base 모델로 복제해서 모든 문장을 같은 목소리로 읽어요
- 효과음(뿅, 반짝, 휙, 팡파르, 도장, 자물쇠)과 마림바 느낌의 배경음은 `tools/make_audio.py`에서 합성해요. 배경음은 말할 때 작아져요
- 사실 확인: 첫 시상 1901년, 경제학상 1969년부터, 한 분야 최대 3명, 평화상은 단체도 받을 수 있음, 추천 기록은 50년 비공개, 1974년부터 세상을 떠난 사람에게는 주지 않음(발표 뒤 세상을 떠나면 그대로 수여), 시상식은 노벨이 세상을 떠난 12월 10일

| 장면 | 내용 |
|---|---|
| 네 사람의 공통점 | 색 기둥 4개가 떨어지며 네 사람 등장, 나라 이름표 → "?" → 힌트: 다이너마이트와 노벨 → 메달을 목에 걸고 "노벨 ○○상" → 빛나는 메달 |
| 제목 | 지식 한 스푼 · 노벨상이 궁금해요! |
| 노벨의 유언 | 유언장을 쓰는 노벨, 생각 구름(재산 → 상 → 인류에게 도움) → 1901 · "첫 노벨상!" 도장 |
| 여섯 분야 | 분야 카드 5장이 하나씩, 경제학(1969~)이 더해져 6장 |
| 심사 과정 | 위쪽 단계 표시(추천 → 검토 → 결정 → 비밀). 지구 둘레 전문가들의 추천서, 체크리스트와 돋보기, "수상자" 도장, 자물쇠와 50년 고리 |
| 수상 인원 | 한 명? → 최대 3명 · 수상자 없음 → 개인과 단체(평화상) |
| 누구나 | 지구본과 여러 나라 사람들, 마리 퀴리의 두 번의 수상(1903 물리학상, 1911 화학상) |
| 세상을 떠난 사람은? | 메달 상자와 흐린 실루엣, 발표(10월) → 시상식(12월 10일) 시간선, "확정" 자물쇠 |
| 마무리 | 시상식 무대와 12월 10일 달력, 메달 둘레의 수상자 얼굴들, 평화·발전, 별을 보는 아이들과 제목 |

## 고치기·렌더링

- 대사·장면 순서·효과음 시각: `tools/make_audio.py`의 `SCRIPT`, `SFX` (다시 실행하면 `timeline.js`와 `audio/mix.wav`가 같이 바뀌고, 바뀐 문장만 새로 읽혀요)
- 그림·움직임: `index.html`의 `SC.hook` ~ `SC.outro`, 인물 생김새는 `LOOK`
- 글자·색: `content.js` (영상 편집기 `../video-editor.html`에서도 고칠 수 있어요)

```bash
npm install
export FFMPEG=/path/to/ffmpeg            # 예: ../math-di-improvement-v2/node_modules/ffmpeg-static/ffmpeg
python3 tools/make_audio.py --design     # (처음 한 번) 목소리 후보 → audio/voice_cands/, 골라서 voice_ref.wav 로
python3 tools/make_audio.py              # 음성(TTS_URL, 기본 http://192.168.51.8:8095)·시각표·믹스
export CHROMIUM="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
node render.mjs --workers 6              # out/nobel_prize.mp4
node tools/snap.mjs out/snaps 12 60 140  # 확인용: 지정한 시각의 프레임 PNG
```
