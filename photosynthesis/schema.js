// 영상 편집기(../video-editor.html)에 보여 줄 칸 설명. 규칙: ../editor/PROTOCOL.md
// 이 영상의 장면 시각은 '원본 시각'(내레이션에 맞춰 늘리기 전)으로 적혀 있어서, index.html 과 같은 방법(WARP)으로 실제 시각으로 바꿈
(() => {
const WARP = window.WARP || [], SUBS = window.SUBS || [];
const v2r = v => WARP.reduce((r, [vs, ve, f]) => v > vs ? r + (Math.min(v, ve) - vs) * (f - 1) : r, v);
const R = v => Math.round(v2r(v) * 100) / 100;
const JUA = "'Jua', 'Noto Sans KR'";
const fit = (size, max) => ({ size, weight: 400, family: JUA, spacing: 0, max });
const tx = (path, label, at, f, more = {}) => ({ path, label, type: 'text', at: R(at), ...(f ? { fit: f } : {}), ...more });
const col = (path, label, desc, at) => ({ path, label, desc, type: 'color', at: R(at) });
const B = [0, 7, 22, 48, 68, 92, 112, 132, 148];
const SCENE_NAMES = ['타이틀', '궁금해요', '광합성의 재료', '광합성이 일어나는 곳', '광합성 식', '광합성의 결과', '영향을 주는 요인', '정리'];
const TRANS_T = [7, 22, 48, 68, 92, 112, 132];
const SECTION_T = [7.5, 22, 48, 68, 92, 112];

window.SCHEMA = {
 id: 'photosynthesis',
 title: '광합성 종이공예 과학 영상',
 duration: v2r(148), fps: 30,
 audio: ['audio/mix.wav', 'audio/mix.mp3'],
 audioFade: { in: 0.3, out: 2 },
 scenes: SCENE_NAMES.map((label, i) => ({ start: R(B[i]), end: i === SCENE_NAMES.length - 1 ? v2r(148) : R(B[i + 1]), label })),
 sounds: TRANS_T.map(T => ({ t: R(T - .5), label: '종이 넘김' })),
 tabs: [{ id: 'sub', label: '자막' }, { id: 'text', label: '화면 글자' }, { id: 'color', label: '색' }],
 groups: [
  { tab: 'sub', title: '내레이션 자막', note: '자막 문구만 바꿀 수 있어요. 나오는 시각과 내레이션 음성은 그대로예요.',
   fields: SUBS.map((s, i) => tx(`subtitles.${i}`, `${i + 1}번 (${R(s[0]).toFixed(1)}초)`, (s[0] + s[1]) / 2, fit(46, 1700))) },

  { tab: 'text', title: '타이틀', at: R(4), fields: [
   tx('title.main', '제목', 4, fit(220, 800)),
   tx('title.question', '제목 아래 질문', 4, fit(48, 1270)),
   tx('title.brand', '회사 이름 (처음·끝 오른쪽 아래)', 4, fit(34, 300))] },
  { tab: 'text', title: '궁금해요', at: R(19), fields: [
   tx('wonder.rice', '밥그릇 이름표', 10, fit(56, 600)),
   tx('wonder.name', '큰 이름표', 19, fit(110, 1700)),
   tx('wonder.answer', '큰 이름표 아래 설명', 19, fit(46, 1700))] },
  { tab: 'text', title: '여러 장면에 함께 쓰는 낱말', at: R(46), note: '한 번 고치면 이 낱말이 나오는 모든 장면에 함께 바뀌어요.', columns: 2, fields: [
   tx('terms.light', '빛', 30),
   tx('terms.water', '물', 36),
   tx('terms.co2', '이산화탄소', 46),
   tx('terms.lightEnergy', '빛에너지', 86),
   tx('terms.glucose', '포도당', 88),
   tx('terms.oxygen', '산소', 88),
   tx('terms.starch', '녹말', 104),
   tx('terms.stoma', '기공', 44),
   tx('terms.leaf', '잎', 51),
   tx('terms.cell', '세포', 57),
   tx('terms.chloroplast', '엽록체', 62),
   tx('terms.chlorophyll', '엽록소', 62)] },
  { tab: 'text', title: '광합성 식', at: R(89), fields: [
   tx('formula.chem', '화학식 (문자 뒤 숫자는 아래첨자로 써져요)', 89, fit(40, 1080)),
   tx('formula.o2', '산소 화학식 (결과 장면)', 108)] },
  { tab: 'text', title: '광합성의 결과', at: R(97), fields: [
   tx('result.use', '포도당의 쓰임', 97, fit(48, 1100)),
   tx('result.store', '녹말 저장 설명', 104, fit(50, 1700)),
   tx('result.breathe', '산소 설명', 110, fit(46, 760))] },
  { tab: 'text', title: '영향을 주는 요인', at: R(116), fields: [
   tx('factors.names.0', '요인 1', 116, fit(50, 420)),
   tx('factors.names.1', '요인 2', 116, fit(50, 420)),
   tx('factors.names.2', '요인 3', 116, fit(50, 420)),
   tx('factors.amount', '그래프 세로축', 123, fit(36, 460)),
   tx('factors.saturate', '빛 그래프 설명', 123, fit(48, 1200)),
   tx('factors.best', '온도 그래프 가운데', 131, fit(44, 600)),
   tx('factors.tooLow', '온도 그래프 왼쪽', 131, fit(34, 300)),
   tx('factors.tooHigh', '온도 그래프 오른쪽', 131, fit(34, 300))] },
  { tab: 'text', title: '정리', at: R(146), fields: [
   tx('summary.line', '위쪽 정리 문장', 146, fit(44, 1500)),
   tx('summary.ending', '마지막 문장', 146, fit(52, 1700))] },
  { tab: 'text', title: '왼쪽 위 장면 제목', at: R(20), fields: SECTION_T.map((T, i) => tx(`sections.${i}`, `${i + 1}번째`, T + 2, fit(46, 1200))) },
  { tab: 'text', title: '장면 전환 종이', at: R(22), note: '종이가 화면을 지나가는 1초 동안 크게 보여요.', columns: 2,
   fields: TRANS_T.map((T, i) => tx(`transitions.${i}`, `${i + 1}번째`, T, fit(190, 1800))) },

  { tab: 'color', title: '바탕', fields: [
   col('colors.sky', '하늘', '타이틀·재료·정리 장면 바탕, 산소 이름표', 4),
   col('colors.cream', '크림 종이', '궁금해요 장면 바탕', 12),
   col('colors.bgCell', '엽록체 장면 바탕', '', 57),
   col('colors.bgFormula', '광합성 식 장면 바탕', '', 89),
   col('colors.bgResult', '결과 장면 바탕', '', 97),
   col('colors.bgFactor', '요인 장면 바탕', '', 116)] },
  { tab: 'color', title: '글자·이름표', fields: [
   col('colors.ink', '글자·선', '모든 글자, 그래프 축, 해 얼굴', 30),
   col('colors.white', '흰 종이', '이름표, 자막 상자, 구름', 30),
   col('colors.grayPaper', '회색 종이', '이산화탄소 이름표, 온도 설명', 46),
   col('colors.brand', '회사 색', '재능교육 이름표, 장면 제목 옆 네모', 4)] },
  { tab: 'color', title: '식물', fields: [
   col('colors.green', '잎', '잎, 언덕, 엽록체 속', 4),
   col('colors.leafAlt', '잎 (번갈아)', '식물의 한 칸 건너 잎', 4),
   col('colors.greenDark', '짙은 초록', '줄기, 제목 글자, 엽록체 알갱이', 4),
   col('colors.greenLight', '연한 초록', '언덕, 기공 확대, 엽록체 이름표', 4),
   col('colors.cell', '세포 안', '', 57),
   col('colors.cellWall', '세포벽', '', 57),
   col('colors.chloroplast', '엽록체 테두리', '', 62),
   col('colors.chlorophyllTag', '엽록소 이름표', '', 62),
   col('colors.soil', '흙', '화분 흙, 뿌리 장면 땅', 30),
   col('colors.root', '뿌리', '', 36)] },
  { tab: 'color', title: '재료·결과물', fields: [
   col('colors.sun', '해·빛', '해, 반짝이, 노란 이름표', 30),
   col('colors.sunDark', '진한 주황', '햇살, 화살표', 89),
   col('colors.water', '물', '물방울, 물 이름표', 36),
   col('colors.red', '빨강', '산소 원자, 그래프 선, 물음표, 온도계', 123),
   col('colors.gray', '탄소 원자', '', 46),
   col('colors.pink', '포도당', '포도당 분자·이름표, 전환 종이', 89),
   col('colors.starch', '녹말', '', 104),
   col('colors.kraft', '크라프트지', '장면 전환 종이', 7),
   col('colors.skyDark', '진한 하늘', '장면 전환 종이', 68),
   col('colors.magnifier', '돋보기', '', 51),
   col('colors.skin', '얼굴', '숨 쉬는 아이', 110)] },
 ],
 locked: '장면 순서와 길이, 움직임, 내레이션과 효과음, 자막이 나오는 시각은 고칠 수 없어요. 소리가 화면에 맞춰 만들어져 있어서예요. 밥그릇·기공·머리카락 같은 작은 그림의 색도 그대로예요.',
 warnings: [
  '자막을 바꿔도 내레이션 음성은 그대로예요. 목소리까지 바꾸려면 tools/make_audio.py 의 NARRATION 을 고쳐 소리를 다시 만들어야 해요.',
  '광합성 식처럼 과학 내용이 담긴 글자는 바꾼 뒤 내용이 맞는지 꼭 다시 확인해 주세요.',
 ],
};
})();
