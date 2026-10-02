# 재능그룹 홍보 영상 (모션그래픽)

재능그룹 홈페이지(jeigroup.com)의 그룹 소개와 계열사·패밀리 사이트를 바탕으로 만든 52초 그룹 홍보 영상이에요.

- 52초, 1920×1080, 30fps. 재능 레드와 사업 부문별 색 5가지, 계열사마다 직접 그린 선 아이콘
- 폰트: Noto Sans KR · Inter (SIL OFL, `fonts/`에 포함)
- 사운드: 120BPM 비트(C–G–Am–F)와 효과음을 `tools/make_audio.py`에서 합성 (외부 음원 없음). 장면 전환과 카드 등장은 박자에 맞춤

| 시간 | 장면 | 내용 |
|---|---|---|
| 0–4s | 비전 | A Better Life Through Better Education · 보다 나은 교육을 통한 보다 나은 삶 |
| 4–8s | 그룹 소개 | SINCE 1977 · 어린이부터 성인까지, 종합교육문화기업 · 교육·출판·방송·IT·인쇄·유통·문화 |
| 8–14s | 01 교육·출판 | 재능교육 (재능스스로방문학습, 재능스스로러닝센터, 생각하는피자, 출판) |
| 14–20s | 02 방송·IT | 재능TV, JEI English TV, 재능e아카데미 |
| 20–26s | 03 인쇄·유통·임대 | 재능인쇄, 재능유통, 제이플라츠 |
| 26–32s | 04 문화·생활 | JCC, 산청율수원, 수국작가촌 |
| 32–38s | 05 연수·학교법인 | 재능셀프러닝, 재능대학교, 재능고등학교, 재능중학교 |
| 38–44s | 계열사 연결도 | 재능그룹 → 5개 부문 → 계열사 15곳 |
| 44–52s | 엔딩 | 재능그룹 · JEI GROUP · jeigroup.com |

## 사실 출처

작업 환경에서 jeigroup.com 에 직접 접속이 막혀 있어서, 아래 페이지들의 검색 결과 요약으로 확인했어요. 공개 전에 담당 부서 확인을 권해요.

- 그룹 소개·비전(A Better Life Through Better Education, 종합교육문화기업, Total Life Service): [재능그룹 개요](https://www.jeigroup.com/controller/company/summary.php?lang=en), [인재상](https://www.jeigroup.com/controller/people/)
- 사업 부문과 계열사 목록: [Subsidiaries](https://www.jeigroup.com/controller/business/?lang=en)
- 재능e아카데미: [재능그룹 재능e아카데미](https://www.jeigroup.com/controller/business/it.php?cid=163) · 재능TV: [재능TV](https://www.jeigroup.com/controller/business/broadcastingTv.php?cid=187) · JEI English TV: [국내 최초 영어교육채널](https://jeienglishtv.com/tv/programInfo.do)
- 제이플라츠: [재능그룹 제이플라츠](https://www.jeigroup.com/controller/business/lease.php?cid=127)
- JCC (안도 다다오 설계, 2015년 혜화동): [JCC 소개](https://www.jeijcc.org/intro.html) · 산청율수원 (2013년 개원 한옥스테이): [이투데이](https://www.etoday.co.kr/news/view/800584)
- 재능셀프러닝(재능교육연수원 약 3만 평): [재능셀프러닝](https://www.jeigroup.com/controller/business/training.php?cid=141)
- 재능대학교(1970), 재능고등학교(스마트시티 특성화), 재능중학교(1965): [재능대학교](https://www.jeigroup.com/controller/business/jeiu.php?cid=172), [재능중학교](https://www.jeigroup.com/controller/business/jeims.php?cid=174), [재능고등학교](https://www.jeigroup.com/controller/business/jeihs.php?lang=en)
- 재능유통·수국작가촌은 자세한 소개를 찾지 못해 설명을 일반적으로 적었어요 (`content.js`에서 바로 고칠 수 있어요)

## 고치기·렌더링

문구·색은 `content.js`, 장면은 `index.html`, 소리는 `tools/make_audio.py`에 있어요. 공용 영상 편집기(`../video-editor.html`)에서 **재능그룹 홍보**를 골라 문구와 색을 바꿀 수 있어요.

```bash
npm install && pip install numpy soundfile imageio-ffmpeg
node tools/export_events.mjs         # tools/events.json (화면의 카드 등장·전환 시각)
python3 tools/make_audio.py          # audio/mix.wav
export FFMPEG=$(python3 -c "import imageio_ffmpeg as i; print(i.get_ffmpeg_exe())")
node render.mjs                      # out/jei_group_promo.mp4
```
