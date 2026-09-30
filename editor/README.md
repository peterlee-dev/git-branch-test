# 재능교육 영상 편집기

`video-editor.html`에서 장면을 이어 붙여 새 영상을 만들어요. 편집본은 장면(클립)을 차례로 놓은 목록이에요.

- **영상 장면**: 이 저장소 영상 9개의 장면 어느 것이든 넣기, 빼기, 순서 바꾸기(끌기), 앞뒤 자르기(양 끝 끌기), 복제, 재생 위치에서 나누기. 장면을 옮기면 그 구간의 소리도 함께 옮겨져서 장면 안에서는 화면과 소리가 맞아요.
- **새 장면**: 제목 카드, 문구 카드(줄마다 차례로), 이미지 카드(천천히 확대 + 설명), 암전. 글자·색·길이를 고쳐요. 소리는 없어요.
- **전환**: 장면마다 들어올 때 컷 · 페이드(검은 화면) · 디졸브(겹쳐 바뀜)와 길이를 고르면 소리도 같은 길이로 이어져요.
- **영상 내용 고치기**: 영상 장면을 고르면 그 영상의 문구·색 탭이 나와요. 같은 영상에서 온 장면에 모두 반영돼요. 겹쳐 나오는 문구는 타임라인의 문구 막대를 끌어 시간을 옮겨요.
- 되돌리기, 브라우저 자동 저장, 작업 파일(JSON) 저장·불러오기, 브라우저에서 바로 MP4 내보내기

작업 파일 형식(버전 2): `{ "kind": "jei-video-project", "version": 2, "clips": [...], "sources": { "영상 id": 문구·색 } }`.
클립은 `{ type: "video", src, in, out, tr }` 또는 `{ type: "title" | "text" | "image" | "black", dur, props, tr }`, `tr` 은 `{ type: "cut" | "fade" | "dissolve", dur }`. 버전 1(영상 하나의 문구·색) 파일도 불러와져요.

## 여는 법

편집기는 영상 페이지를 iframe으로 열어서 파일을 직접 여는 `file://` 로는 동작하지 않아요. 저장소 맨 위에서 로컬 서버를 띄우세요.

```bash
python3 -m http.server 8000
# 브라우저에서 http://localhost:8000/video-editor.html
```

미리보기와 내보내기의 소리는 각 영상 폴더의 `audio/mix.wav`를 써요(없으면 무음). 소리 파일은 저장소에 없으니 영상 폴더의 README대로 먼저 만들어 두세요.

## 저장한 작업 파일로 렌더링

```bash
node editor/render.mjs 작업파일.json --out out/edit.mp4    # 편집본 전체 (장면·전환·소리 포함)
cd <영상 폴더> && node render.mjs --project 작업파일.json  # 영상 하나를 문구·색만 바꿔서 (버전 1 파일)
```

`editor/render.mjs` 는 저장소 맨 위를 잠깐 로컬 서버로 열고 편집기 페이지에서 한 장씩 그려요. 영상 폴더 하나 이상에서 `npm install`, 쓰는 영상의 `audio/mix.wav`, `ffmpeg`(또는 `FFMPEG` 환경 변수)가 필요해요.

## 영상 추가하기

영상 폴더에 `content.js`, `schema.js`를 두고 페이지에서 `window.VIDEO`를 내보낸 뒤 `editor/videos.js` 목록에 넣으면 돼요. 자세한 규칙은 [PROTOCOL.md](PROTOCOL.md)에 있어요.

`vendor/mp4-muxer.js`는 MIT 라이선스([mp4-muxer](https://github.com/Vanilagy/mp4-muxer))예요.
