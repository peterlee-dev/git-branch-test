// 영상 편집기(../video-editor.html)에 보여 줄 칸 설명. 규칙: ../editor/PROTOCOL.md
window.SCHEMA = {
 id: 'hangang-walk',
 title: '한강 다리 산책',
 duration: 15, fps: 30,
 audio: ['audio/mix.wav', 'audio/mix.mp3'],
 audioFade: { in: 0.3, out: 2 },
 scenes: [
  { start: 0, end: 0.8, label: '페이드 인', dark: true },
  { start: 0.8, end: 14.2, label: '해 질 녘 다리 인도를 따라 옆으로 걷기' },
  { start: 14.2, end: 15, label: '페이드 아웃', dark: true },
 ],
 sounds: [1.2, 4.1, 6.8, 9.9, 12.6].map(t => ({ t: t + 1.5, label: '지나가는 차' })),
 tabs: [{ id: 'sky', label: '하늘' }, { id: 'light', label: '빛' }, { id: 'water', label: '물' }, { id: 'film', label: '화면 느낌' }],
 groups: [
  { tab: 'sky', title: '하늘 색', at: 7, note: '위에서 아래로 세 가지 색이 부드럽게 이어져요.', fields: [
   { path: 'sky.zenith', label: '하늘 꼭대기', desc: '화면 맨 위 짙은 하늘', type: 'color' },
   { path: 'sky.mid', label: '하늘 중간', desc: '빌딩 위쪽 보랏빛 하늘', type: 'color' },
   { path: 'sky.horizon', label: '지평선 노을', desc: '산 능선 바로 위 분홍빛', type: 'color' }] },
  { tab: 'sky', title: '해', at: 7, fields: [
   { path: 'sky.sunHalo', label: '노을 번짐', desc: '오른쪽 해 주변으로 넓게 퍼지는 빛', type: 'color' },
   { path: 'sky.sunCore', label: '해 빛무리', desc: '해 바로 둘레의 밝은 빛', type: 'color' }] },
  { tab: 'sky', title: '구름', at: 7, fields: [
   { path: 'sky.cloudLit', label: '해 쪽 구름', desc: '햇빛을 받은 구름', type: 'color' },
   { path: 'sky.cloudShade', label: '그늘진 구름', desc: '해에서 먼 쪽 구름', type: 'color' },
   { path: 'sky.cloudOpacity', label: '구름 진하기', type: 'number', min: 0, max: 1, step: 0.05 },
   { path: 'sky.cloudCover', label: '구름 양', desc: '클수록 하늘을 더 많이 덮어요', type: 'number', min: 0.2, max: 0.7, step: 0.02 }] },
  { tab: 'sky', title: '안개', at: 7, fields: [
   { path: 'sky.fog', label: '먼 풍경 안개', desc: '강 건너 빌딩·산이 물드는 색', type: 'color' }] },
  { tab: 'light', title: '해와 하늘빛', at: 7, note: '다리 난간·기둥·빌딩 벽에 비치는 빛이에요.', fields: [
   { path: 'light.sun', label: '햇빛', type: 'color' },
   { path: 'light.sunIntensity', label: '햇빛 세기', type: 'number', min: 0, max: 4, step: 0.1 },
   { path: 'light.skyFill', label: '위에서 오는 하늘빛', type: 'color' },
   { path: 'light.groundFill', label: '아래에서 오는 반사광', type: 'color' },
   { path: 'light.fillIntensity', label: '하늘빛 세기', type: 'number', min: 0, max: 2, step: 0.05 }] },
  { tab: 'light', title: '가로등', at: 3, fields: [
   { path: 'lamps.glow', label: '전구 빛', desc: '가로등 머리의 밝은 점', type: 'color' },
   { path: 'lamps.halo', label: '빛 번짐', desc: '전구 주변의 넓은 빛', type: 'color' },
   { path: 'lamps.pool', label: '바닥 불빛', desc: '보도블록에 떨어진 둥근 빛', type: 'color' },
   { path: 'lamps.light', label: '비추는 빛', desc: '난간·기둥에 닿는 빛의 색', type: 'color' },
   { path: 'lamps.intensity', label: '비추는 빛 세기', type: 'number', min: 0, max: 60, step: 1 }] },
  { tab: 'light', title: '강 건너 창문', at: 7, fields: [
   { path: 'city.warmWindow', label: '따뜻한 창', desc: '주황빛으로 켜진 창 (대부분)', type: 'color' },
   { path: 'city.coolWindow', label: '하얀 창', desc: '푸르스름하게 켜진 창', type: 'color' },
   { path: 'city.windowBrightness', label: '창문 밝기', type: 'number', min: 0, max: 2, step: 0.05 }] },
  { tab: 'water', title: '강물', at: 7, fields: [
   { path: 'water.deep', label: '물 속 색', desc: '반사가 약한 가까운 수면의 바탕색', type: 'color' },
   { path: 'water.glint', label: '해 반사 반짝임', type: 'color' },
   { path: 'water.glintStrength', label: '반짝임 세기', type: 'number', min: 0, max: 5, step: 0.1 }] },
  { tab: 'film', title: '화면 느낌', at: 7, fields: [
   { path: 'film.bloom', label: '빛 번짐(블룸)', desc: '1 이 기본, 0 이면 번짐 없음', type: 'number', min: 0, max: 1.8, step: 0.05 },
   { path: 'film.warmTone', label: '따뜻한 색조', type: 'color' },
   { path: 'film.warmAmount', label: '따뜻한 색조 세기', type: 'number', min: 0, max: 0.6, step: 0.02 },
   { path: 'film.shadowTint', label: '전체 색 필터', desc: '흰색에 가까울수록 원래 색, 푸를수록 차가운 느낌', type: 'color' },
   { path: 'film.vignette', label: '가장자리 어둡게', type: 'number', min: 0, max: 1, step: 0.05 },
   { path: 'film.grain', label: '필름 입자', desc: '1 이 기본, 0 이면 입자 없음', type: 'number', min: 0, max: 3, step: 0.1 }] },
 ],
 locked: '걷는 속도와 흔들림, 카메라 방향, 해 위치, 풍경 배치, 영상 길이는 고칠 수 없어요. 배경음의 발소리가 초당 1.85걸음에 맞춰 만들어져 있어서예요.',
 warnings: ['3D 장면을 한 프레임마다 여러 번 그리는 무거운 영상이라 미리보기와 내보내기가 느릴 수 있어요. GPU가 없는 컴퓨터에서는 내보내기에 30분 가까이 걸려요.'],
};
