# 영상 편집기 연결 규칙 (v1)

`video-editor.html`(저장소 맨 위)은 영상 폴더의 `index.html`을 보이지 않는 iframe으로 열고, 아래 약속만으로 편집합니다.
영상마다 이 규칙을 지키면 편집기 코드는 고치지 않고 영상이 추가돼요. 영상 목록은 `editor/videos.js`.

## 영상 폴더에 필요한 것

### 1. `content.js` — 편집할 수 있는 값의 기본값

```js
window.CONTENT = { /* JSON 으로 저장될 수 있는 값만: 문자열, 숫자, 색(#RRGGBB), 배열, 객체 */ };
```

- 화면에 나오는 문구, 색, 겹쳐 나오는 글자의 시작·끝 시각처럼 **바꿔도 영상이 깨지지 않는 값**만 넣습니다.
- 색은 반드시 `#RRGGBB` 6자리 (편집기의 색 고르기 칸이 이 형식만 받음). 투명도가 필요하면 코드에서 `rgba(hex, a)` 도우미로 만듭니다.
- 기존 영상과 **완전히 같은 화면**이 나오도록 기본값을 정합니다 (리팩터링 전후 프레임이 같아야 함).

### 2. `schema.js` — 편집기에 보여 줄 칸 설명

```js
window.SCHEMA = {
  id: 'ai-math-trailer',                 // 폴더 이름과 같게
  title: '재능스스로AI수학 리뉴얼 예고편',
  duration: 45, fps: 30,
  audio: ['audio/mix.wav', 'audio/mix.mp3'],   // 영상 폴더 기준, 먼저 열리는 것 사용 (없으면 무음)
  audioFade: { in: 0.3, out: 2 },         // render.mjs 의 afade 와 같게 (없으면 0)
  scenes: [ { start: 0, end: 4.5, label: '암전 · 인트로', dark: true }, ... ],   // 타임라인 '장면' 줄 (편집 불가, 보기용)
  sounds: [ { t: 17, label: '브람', big: true }, ... ],                         // 타임라인 '소리' 줄 (보기용, 선택)
  timed: {                                // 선택: 시작·끝을 막대로 끌 수 있는 글자 목록
    path: 'cards', label: '문구', textKey: 'text', startKey: 'start', endKey: 'end', minLen: 0.4,
    fields: [ { key: 'text', label: '문구', type: 'text', fit: {...} }, { key: 'start', label: '시작(초)', type: 'number', step: 0.1 }, ... ]
  },
  tabs: [ { id: 'text', label: '문구' }, { id: 'color', label: '색' } ],   // timed 목록은 첫 탭 맨 위에 나옴
  groups: [
    { tab: 'text', title: '별자리 보상', at: 15, note: '선택: 칸 위 설명',
      fields: [ { path: 'reward.name', label: '별자리 이름', type: 'text', fit: { size: 36, weight: 300, family: "'Noto Sans KR'", spacing: 14, max: 1700 } } ] },
    { tab: 'color', title: '글자', fields: [ { path: 'colors.accent', label: '강조 글자', desc: '어디에 쓰이는지', type: 'color', at: 42.5 } ] },
  ],
  locked: '이 영상에서 고칠 수 없는 것과 이유 (한두 문장)',
  warnings: ['선택: 편집 전에 꼭 알아야 할 것. 예: 자막을 바꿔도 내레이션 음성은 그대로예요'],
};
```

- `type`: `text` | `textarea` | `number`(min, max, step) | `select`(options: [값...] 또는 [[값, 이름]...]) | `color`
- `at`: 그 값이 화면에 보이는 시각(초). 칸을 누르면 편집기가 그 순간으로 이동. 칸에 없으면 그룹의 `at` 사용.
- `fit`(선택): 글자가 화면 밖으로 넘칠 수 있는지 편집기가 재어 봄. `{ size, weight, family, spacing, max }` (px, 1920 기준).
- `path`: `content` 안의 위치를 점으로 연결 (`ui.0.copy`, `colors.star`).
- 그룹의 `columns: 2` 는 칸을 두 줄로 나란히 (짧은 단어 여러 개일 때).
- `timed.fields` 는 항목 하나의 칸(`key`). 글자 칸의 넘침 검사는 고정값 `fit` 또는 항목의 값을 쓰는 `fitFrom: { size: 'size', weight: 'weight', spacing: 'spacing' }` + `family`, `max`.
- `timed` 항목이 바뀌어도 소리는 그대로이므로, 소리에 묶이지 않은 글자(겹쳐 나오는 문구)만 `timed` 로 둡니다. 내레이션 자막처럼 소리에 묶인 글자는 `groups` 의 글자 칸으로만 둡니다.

### 3. `index.html` — 페이지가 내보내는 것

기존 약속(`window.draw(t)`, `window.DURATION`, `window.ready`, `?render` 에서 조작 막대 숨김)은 그대로 두고 아래를 더합니다.

```js
window.VIDEO = {
  schema: window.SCHEMA,
  defaults: DEFAULT_CONTENT,          // content.js 를 읽자마자 깊은 복사해 둔 것
  get content() { return C; },        // 지금 쓰는 값
  apply(content) { ... },             // 기본값 위에 content 를 덮어써 C 를 만들고, 캐시(미리 그린 텍스처 등)를 다시 만듦. 동기로 끝나야 함
  canvas: document.getElementById('c'),
};
```

- `apply` 뒤 `draw(t)` 한 번이면 바뀐 값이 반영돼야 합니다.
- 기본값과 합치는 규칙(누락된 칸은 기본값): 객체는 키마다, 배열은 새 배열 길이를 따르되 같은 자리의 기본 항목과 합침. `ai-math-trailer/trailer.js` 의 `merge()` 참고.
- `<script src="content.js">`, `<script src="schema.js">` 는 그리는 코드보다 먼저.

### 4. `render.mjs --project 파일.json`

편집기에서 저장한 작업 파일을 받아 `window.VIDEO.apply(project.content)` 후 렌더링.

## 작업 파일 형식

```json
{ "kind": "jei-video-project", "version": 1, "video": "ai-math-trailer", "content": { ... } }
```

## 하지 않는 것

- 장면 길이·순서, 카메라, 음악·내레이션 타이밍은 편집 대상이 아님 (소리가 화면에 맞춰 만들어져 있어서). 이런 값은 `content`에 넣지 않습니다.
