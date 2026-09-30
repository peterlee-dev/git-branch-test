// 영상 편집기(../video-editor.html)에 보여 줄 칸 설명. 규칙: ../editor/PROTOCOL.md
// 영상은 120BPM 격자(초)로 짜고 곡의 박 길이에 맞게 늘이므로(song.js) 여기 시각도 같은 비율로 바꿔서 씀
(() => {
const SONG = window.SONG || { beat: .5 }, TK = SONG.beat / .5;
const g = x => +(x * TK).toFixed(3);                       // 격자 시각 → 실제 시각(초)
const Q = x => Math.round(x / .25 + 1e-6) * .25;           // index.html 의 Q() 와 같음 (8분음표 격자)
const DISP = "'Black Han Sans'", KR = "'Noto Sans KR'", EN = "'Inter'", MONO = "'JetBrains Mono'";
const txt = (path, label, at, fit) => ({ path, label, type: 'text', ...(at != null ? { at } : {}), ...(fit ? { fit } : {}) });
const col = (path, label, desc, at) => ({ path, label, desc, type: 'color', at });
window.SCHEMA = {
 id: 'edu-platform-team',
 title: '교육플랫폼팀 홍보',
 duration: 34 * TK, fps: 30,
 audio: ['audio/mix.wav', 'audio/mix.mp3'],
 audioFade: { in: 0.3, out: 2 },
 scenes: [
  { start: 0, end: g(4), label: '인트로 · 우리는 교육플랫폼팀!' },
  { start: g(4), end: g(8), label: '파이프라인' },
  { start: g(8), end: g(12), label: '저작도구 · 발행' },
  { start: g(12), end: g(16), label: '양산 ×128' },
  { start: g(16), end: g(20), label: '웹도! 앱도!' },
  { start: g(20), end: g(25), label: 'AI랑 같이', dark: true },
  { start: g(25), end: g(34), label: '엔딩 · 교육의 미래를, 코드로.' },
 ],
 sounds: [
  { t: g(2), label: '곡 드롭 · 색종이', big: true },
  ...[3.55, 7.55, 11.55, 15.55, 19.55, 24.6].map(s => ({ t: g(Q(s)), label: '장면 전환' })),
  ...[5, 5.5, 6, 6.5].map(s => ({ t: g(s), label: '공 통통' })),
  ...[9, 9.5, 10, 10.5].map(s => ({ t: g(s), label: '블록 착지' })),
  { t: g(11), label: '발행 도장', big: true },
  { t: g(22.75), label: '문항 카드 · 색종이' },
  { t: g(25.5), label: '열정 ON', big: true },
  { t: g(29), label: '마지막 색종이' },
 ],
 tabs: [{ id: 'text', label: '문구' }, { id: 'color', label: '색' }],
 groups: [
  { tab: 'text', title: '인트로', at: g(3), fields: [
   txt('intro.hello', '위 스티커 (코드 글씨)', g(1), { size: 40, weight: 400, family: MONO, max: 1740 }),
   txt('intro.we', '첫 줄', g(1.5), { size: 120, weight: 400, family: DISP, max: 1800 }),
   txt('intro.team', '팀 이름 (크게)', g(3), { size: 210, weight: 400, family: DISP, max: 1800 })] },
  { tab: 'text', title: '파이프라인', at: g(7.3), note: '제목 두 부분은 한 줄로 이어 붙어요 (왼쪽 200px 에서 시작).', fields: [
   txt('pipeline.title1', '제목 앞부분', g(7.3), { size: 120, weight: 400, family: DISP, max: 900 }),
   txt('pipeline.title2', '제목 뒷부분 (빨강)', g(7.3), { size: 120, weight: 400, family: DISP, max: 700 }),
   ...[0, 1, 2, 3].map(i => txt(`pipeline.nodes.${i}`, `단계 ${i + 1}`, g(7.3), { size: 52, weight: 400, family: DISP, max: 270 })),
   txt('pipeline.tag', '작은 스티커', g(7.3)),
   txt('pipeline.caption', '아래 스티커', g(7.3), { size: 44, weight: 400, family: DISP, max: 1740 })] },
  { tab: 'text', title: '저작도구', at: g(11.3), fields: [
   txt('authoring.title', '제목', g(11.3), { size: 96, weight: 400, family: DISP, max: 1800 }),
   txt('authoring.window', '창 제목', g(11.3)),
   ...[0, 1, 2, 3].flatMap(i => [
    txt(`authoring.blocks.${i}.label`, `블록 ${i + 1} 이름표`, g(11.3), { size: 28, weight: 400, family: DISP, max: 100 }),
    txt(`authoring.blocks.${i}.body`, `블록 ${i + 1} 내용`, g(11.3), { size: i === 0 ? 50 : 34, weight: 400, family: DISP, max: 880 })]),
   txt('authoring.stamp', '도장 글자', g(11.3), { size: 70, weight: 400, family: DISP, max: 230 })] },
  { tab: 'text', title: '양산', at: g(15.5), note: '제목 두 부분은 한 줄로 이어 붙어요 (왼쪽 200px 에서 시작, 오른쪽 위에 ×128 숫자).', fields: [
   txt('scale.title1', '제목 앞부분', g(15.5), { size: 96, weight: 400, family: DISP, max: 800 }),
   txt('scale.title2', '제목 뒷부분 (노랑)', g(15.5), { size: 96, weight: 400, family: DISP, max: 520 }),
   txt('scale.caption', '아래 스티커', g(15.5), { size: 44, weight: 400, family: DISP, max: 1740 })] },
  { tab: 'text', title: '웹 · 앱', at: g(19.3), fields: [
   txt('multi.web', '왼쪽 제목', g(19.3), { size: 130, weight: 400, family: DISP, max: 900 }),
   txt('multi.app', '오른쪽 제목', g(19.3), { size: 130, weight: 400, family: DISP, max: 900 }),
   txt('multi.screenTitle', '화면 속 제목', g(19.3)),
   ...[0, 1, 2].map(i => txt(`multi.lessons.${i}`, `화면 속 학습 ${i + 1}`, g(19.3))),
   txt('multi.caption', '아래 스티커', g(19.3), { size: 44, weight: 400, family: DISP, max: 1740 })] },
  { tab: 'text', title: 'AI', at: g(24), fields: [
   txt('ai.title1', '첫 줄', g(24), { size: 120, weight: 400, family: DISP, max: 1800 }),
   txt('ai.title2', '둘째 줄 (분홍)', g(24), { size: 140, weight: 400, family: DISP, max: 1800 }),
   { path: 'ai.prompt', label: '말풍선 요청 (한 글자씩 타이핑)', type: 'text', at: g(24), fit: { size: 52, weight: 400, family: DISP, max: 940 } },
   ...[0, 1, 2, 3, 4].map(i => txt(`ai.cards.${i}`, `문항 카드 ${i + 1}`, g(24), { size: 44, weight: 800, family: EN, max: 190 })),
   txt('ai.caption', '아래 스티커', g(24), { size: 40, weight: 400, family: DISP, max: 1740 })] },
  { tab: 'text', title: '엔딩', at: g(31), fields: [
   txt('ending.passion', '스위치 옆 글자', g(31), { size: 130, weight: 400, family: DISP, max: 560 }),
   txt('ending.off', '스위치 꺼짐', g(25.3)), txt('ending.on', '스위치 켜짐', g(31)),
   txt('ending.line1', '큰 문구 첫 줄', g(31), { size: 150, weight: 400, family: DISP, max: 1800 }),
   txt('ending.line2', '큰 문구 둘째 줄', g(31), { size: 190, weight: 400, family: DISP, max: 1800 }),
   txt('ending.team', '팀 이름 스티커', g(31), { size: 50, weight: 400, family: DISP, max: 1740 }),
   txt('ending.roles', '맨 아래 작은 영문', g(31)),
   txt('ending.cta', '오른쪽 아래 스티커 (코드 글씨)', g(31), { size: 34, weight: 400, family: MONO, max: 820 })] },
  { tab: 'color', title: '배경 · 강조색', note: '장면 배경이 레드 → 크림 → 노랑 → 파랑 → 민트 → 먹색 → 레드 순서로 바뀌어요. 같은 색이 글자·스티커·색종이에도 쓰여요.', fields: [
   col('colors.red', '레드', '인트로·엔딩 배경, 강조 글자', g(3)),
   col('colors.cream', '크림', '파이프라인 배경', g(7)),
   col('colors.yellow', '노랑', '저작도구 배경, 팀 이름 글자, 공', g(11)),
   col('colors.blue', '파랑', '양산 배경, AI 로봇', g(15)),
   col('colors.mint', '민트', '웹·앱 배경', g(19)),
   col('colors.ink', '먹색', 'AI 배경, 글자 테두리·검은 글자', g(24)),
   col('colors.pink', '분홍', '장식·카드·"더 빠르게!"', g(24)),
   col('colors.purple', '보라', '해설 블록, 문항 카드 5', g(11.3)),
   col('colors.white', '흰색', '흰 글자·스티커·테두리', g(3)),
   col('colors.toggleOff', '꺼진 스위치', '엔딩 스위치가 켜지기 전 색', g(25.3))] },
 ],
 locked: '장면 순서·길이, 글자가 떨어지는 박자, 화면 흔들림은 배경음(CELEBRATION)의 박자·드롭에 맞춰 짜여 있어서 고칠 수 없어요. 단계·블록·카드 개수도 효과음 자리와 묶여 있어서 그대로예요.',
 warnings: ['글자를 길게 바꾸면(9자 이상) 글자가 더 빠른 간격으로 떨어지고, 너무 길면 장면이 바뀌기 전에 다 못 떨어질 수 있어요.', '곡 음원(audio/)은 저장소에 없어요. 없으면 편집기에서 무음으로 재생돼요.'],
};
})();
