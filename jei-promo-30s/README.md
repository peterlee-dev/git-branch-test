# 재능교육 30초 홍보 영상 (모션그래픽)

- 30초, 1920×1080, 30fps, 레드 #E60012 / 블랙. 폰트: Noto Sans KR + Inter (`fonts/`에 포함)
- 사운드트랙: 120BPM 비트와 효과음을 `tools/make_audio.py`에서 코드로 합성 (외부 음원 없음). 장면 전환은 마디(2초)에 맞춤

| 시간 | 장면 | 내용 |
|---|---|---|
| 0–4s | 훅 | AI 시대에도 결국, 스스로. |
| 4–8s | 교육 50년 | 1977 → 2027 연도 카운터, 1981 재능산수로 시작한 스스로학습 |
| 8–14s | 스스로학습시스템 | 스스로 생각하고 / 풀고 / 자란다, 개인별·능력별 학습 |
| 14–20s | 수상 | 스스로학습시스템 18년 연속 대한민국 퍼스트브랜드 대상, 생각하는피자 13년 연속 소비자 선정 최고의 브랜드 대상 |
| 20–25s | 글로벌 | 1992년 미국 진출, 캐나다·중국·일본·호주·뉴질랜드 |
| 25–30s | 엔딩 | 재능교육 · AI 시대에도 결국, 스스로. · jei.com |

## 사실 출처

- 슬로건 "AI시대에도 결국, 스스로": [재능교육 홈페이지](https://www.jei.com/) 제목
- 스스로학습시스템 18년 연속 대한민국 퍼스트브랜드 대상 (2026, 한국소비자포럼): [네이트 뉴스](https://news.nate.com/view/20260107n33259)
- 생각하는피자 13년 연속 소비자 선정 최고의 브랜드 대상 (2026, 중앙일보·포브스코리아): [시민일보](https://www.siminilbo.co.kr/news/newsview.php?ncode=1160276545167802)
- 1977년 창립, 1981년 재능산수로 교육사업 시작, 1992년 미국 진출과 해외 국가: [서울경제](https://m.sedaily.com/amparticle/10696320), [Global JEI](https://www.jeigroup.com/controller/business/global.php?cid=142)

## 영상 편집기로 고치기

저장소 맨 위 `video-editor.html`에서 이 영상을 고르면 코드를 몰라도 고칠 수 있어요 (규칙: `editor/PROTOCOL.md`).

- 고칠 수 있는 것: 화면의 모든 문구(훅, 교육 50년, 스스로학습시스템 세 줄, 수상 두 개, 나라 이름 6개, 엔딩 슬로건·주소, 위쪽 고정 표기), 연도 카운터의 시작·끝 연도, 수상 횟수 숫자, 색 9가지 (기본값은 `content.js`, 칸 설명은 `schema.js`)
- 고칠 수 없는 것: 장면 순서·길이, 글자가 나오는 시각, 움직임, 음악. 비트와 효과음이 장면 전환·글자 등장에 맞춰 만들어져 있어서예요. 줄 수(3줄)·수상 수(2개)·나라 수(6개)도 소리 횟수에 맞춰 고정이에요.

편집기에서 저장한 작업 파일(JSON)은 이렇게 렌더링해요.

```bash
node render.mjs --project 파일.json
```

## 수정·렌더링

문구·색 기본값은 `content.js`에, 타이밍과 그리는 코드는 `index.html`의 `s1`~`s6` 함수에, 비트와 효과음은 `tools/make_audio.py`에 있습니다.

```bash
npm install && pip install numpy soundfile imageio-ffmpeg
python3 tools/make_audio.py          # audio/mix.wav
export FFMPEG=$(python3 -c "import imageio_ffmpeg as i; print(i.get_ffmpeg_exe())")
node render.mjs                      # out/jei_promo_30s.mp4
```
