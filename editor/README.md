# 재능교육 영상 편집기

`video-editor.html` 하나로 이 저장소의 모든 영상을 편집해요. 위쪽에서 영상을 고르면 그 영상에서 고칠 수 있는 칸이 오른쪽에 나와요.

- 미리보기: 재생, 한 프레임씩 이동, 타임라인에서 장면으로 이동
- 칸을 고치면 바로 반영, 칸을 누르면 그 값이 보이는 순간으로 이동
- 글자가 넘칠 것 같으면 경고
- 겹쳐 나오는 문구가 있는 영상은 타임라인 막대를 끌어 시간을 바꿈
- 되돌리기, 영상마다 브라우저 자동 저장
- 작업 파일(JSON) 저장·불러오기, 브라우저에서 바로 MP4 내보내기

## 여는 법

편집기는 영상 페이지를 iframe으로 열어서 파일을 직접 여는 `file://` 로는 동작하지 않아요. 저장소 맨 위에서 로컬 서버를 띄우세요.

```bash
python3 -m http.server 8000
# 브라우저에서 http://localhost:8000/video-editor.html
```

미리보기와 내보내기의 소리는 각 영상 폴더의 `audio/mix.wav`를 써요(없으면 무음). 소리 파일은 저장소에 없으니 영상 폴더의 README대로 먼저 만들어 두세요.

## 저장한 작업 파일로 렌더링

```bash
cd <영상 폴더> && node render.mjs --project 작업파일.json
```

## 영상 추가하기

영상 폴더에 `content.js`, `schema.js`를 두고 페이지에서 `window.VIDEO`를 내보낸 뒤 `editor/videos.js` 목록에 넣으면 돼요. 자세한 규칙은 [PROTOCOL.md](PROTOCOL.md)에 있어요.

`vendor/mp4-muxer.js`는 MIT 라이선스([mp4-muxer](https://github.com/Vanilagy/mp4-muxer))예요.
