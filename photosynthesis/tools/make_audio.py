"""광합성 과학 영상용 내레이션(TTS) + 효과음 믹스 생성.

- 내레이션: Supertonic 3 (sherpa-onnx, 온디바이스 소형 TTS, 한국어)
- 효과음: numpy 로 직접 합성 (외부 음원 없음)

사용법:
  pip install sherpa-onnx soundfile numpy
  # 모델: https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/sherpa-onnx-supertonic-3-tts-int8-2026-05-11.tar.bz2
  TTS_MODEL_DIR=/path/to/sherpa-onnx-supertonic-3-tts-int8-2026-05-11 python3 tools/make_audio.py
  → audio/mix.wav, timeline.js 생성 후 `node render.mjs` 로 영상에 합성
"""
import os, sys, json
import numpy as np
import soundfile as sf

SR = 44100
DURATION = 148.0
VOICE_SID = 1          # Supertonic 3 음성 (0~4 여성, 5~9 남성)
PAUSE = 0.6            # 문장 뒤 쉬는 시간(초)
BASE_SPEED = 0.9        # 약간 천천히
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'audio', 'mix.wav')

# (시작, 끝[이 안에 끝나야 함], 읽을 문장, 화면 자막) — 읽을 문장은 발음대로 한글로 적음
# 자막이 None 이면 읽을 문장을 그대로 자막으로 씀
NARRATION = [
    (0.8, 5.8, '광합성! 식물은 어떻게 스스로 양분을 만들까요?', None),
    (7.6, 11.0, '식물은 우리처럼 밥을 먹지 않아요.', None),
    (11.3, 15.0, '그런데도 쑥쑥 자라요. 어떻게 된 걸까요?', None),
    (15.6, 21.2, '비밀은 잎에서 스스로 양분을 만드는 광합성이에요!', None),
    (22.6, 26.2, '광합성에는 세 가지 재료가 필요해요. 빛, 물, 이산화탄소예요.', None),
    (26.6, 31.0, '먼저 빛! 잎은 햇빛을 받아요.', None),
    (31.6, 37.0, '물은 뿌리에서 흡수해서, 줄기를 따라 잎까지 올라가요.', None),
    (37.6, 43.4, '이산화탄소는 잎 뒷면의 작은 구멍, 기공으로 들어와요.', None),
    (43.8, 47.6, '이렇게 재료가 모두 잎에 모였어요.', None),
    (48.6, 52.8, '잎을 아주 크게 확대해 볼까요?', None),
    (53.2, 58.0, '잎의 세포 속에는 초록색 알갱이, 엽록체가 있어요.', None),
    (58.6, 64.6, '엽록체 안의 엽록소가 빛을 흡수해서, 광합성이 일어나요.', None),
    (68.6, 73.2, '엽록체에서 물과 이산화탄소가 빛에너지를 만나면,', None),
    (73.6, 79.0, '포도당과 산소가 만들어져요.', None),
    (79.6, 87.0, '식으로 쓰면, 이산화탄소 더하기 물, 빛에너지를 받아 포도당 더하기 산소예요.', '이산화탄소 + 물 → (빛에너지) → 포도당 + 산소'),
    (87.6, 91.6, '이것이 바로 광합성이에요!', None),
    (92.6, 98.2, '포도당은 식물이 자라고 살아가는 데 쓰는 양분이에요.', None),
    (98.7, 104.2, '쓰고 남은 포도당은 녹말로 바뀌어 저장돼요.', None),
    (104.7, 111.0, '산소는 기공을 통해 공기 중으로 나가요. 우리가 숨 쉬는 산소예요.', None),
    (112.6, 117.2, '광합성은 언제나 똑같이 일어나지는 않아요.', None),
    (117.6, 124.2, '빛이 세질수록 광합성량이 늘어나다가, 어느 정도가 되면 더 늘지 않아요.', None),
    (124.6, 131.2, '이산화탄소 농도와 온도도 영향을 줘요. 온도는 너무 낮아도, 너무 높아도 좋지 않아요.', None),
    (132.6, 137.6, '정리해 볼까요? 식물은 빛, 물, 이산화탄소로 포도당과 산소를 만들어요.', None),
    (138.6, 144.0, '광합성 덕분에 식물도 자라고, 우리도 숨 쉴 수 있어요!', None),
]

# ---------------------------------------------------------------- TTS
def load_tts():
    if os.environ.get('TTS_ENGINE') == 'jei':      # 회사 PC 에서 사내 TTS 로 만든 음성 (../tools/voicebank.py, ../tools/jei_tts.py)
        sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools')); import voicebank
        return voicebank.load(os.path.join(HERE, '..'), SR, trim, lang='ko')
    import sherpa_onnx as s
    d = os.environ.get('TTS_MODEL_DIR')
    if not d or not os.path.isdir(d):
        sys.exit('TTS_MODEL_DIR 에 Supertonic 3 모델 폴더를 지정하세요.')
    j = lambda f: os.path.join(d, f)
    cfg = s.OfflineTtsConfig(model=s.OfflineTtsModelConfig(
        supertonic=s.OfflineTtsSupertonicModelConfig(
            duration_predictor=j('duration_predictor.int8.onnx'), text_encoder=j('text_encoder.int8.onnx'),
            vector_estimator=j('vector_estimator.int8.onnx'), vocoder=j('vocoder.int8.onnx'),
            tts_json=j('tts.json'), unicode_indexer=j('unicode_indexer.bin'), voice_style=j('voice.bin')),
        num_threads=4))
    tts = s.OfflineTts(cfg)

    def say(text, speed):
        g = s.GenerationConfig()
        g.sid, g.speed, g.num_steps, g.extra = VOICE_SID, speed, 8, {'lang': 'ko'}
        a = tts.generate(text, g)
        x = np.asarray(a.samples, dtype=np.float32)
        if a.sample_rate != SR:
            n = int(len(x) * SR / a.sample_rate)
            x = np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)
        return trim(x)
    return say

def trim(x, thr=0.01):
    idx = np.where(np.abs(x) > thr)[0]
    if len(idx) == 0: return x
    a, b = max(0, idx[0] - int(.02 * SR)), min(len(x), idx[-1] + int(.06 * SR))
    return x[a:b]

# ---------------------------------------------------------------- SFX 합성
t_ = lambda d: np.arange(int(d * SR)) / SR
def env_exp(d, k): return np.exp(-t_(d) * k)
def sweep(f0, f1, d):
    f = np.geomspace(f0, f1, int(d * SR)); return np.sin(2 * np.pi * np.cumsum(f) / SR)

def sfx_pop(f=520):          # 뿅: 블록/알약 등장
    d = .12; return sweep(f * 1.8, f, d) * env_exp(d, 38) * .9
def sfx_tick(f=1500):        # 딸깍: 블록 쌓기
    d = .045; return (np.sin(2 * np.pi * f * t_(d)) * .7 + np.random.RandomState(1).randn(int(d * SR)) * .15) * env_exp(d, 90)
def sfx_ding(f=880, d=1.1):  # 띵: 정답/숫자 공개
    tt = t_(d); x = sum(a * np.sin(2 * np.pi * f * m * tt) * np.exp(-tt * k) for m, a, k in [(1, 1, 3.2), (2.0, .35, 5), (3.01, .18, 8), (4.2, .08, 12)])
    return x * np.minimum(1, tt / .004) * .6
def sfx_sparkle():           # 반짝: 도-미-솔-도
    out = np.zeros(int(1.2 * SR))
    for i, f in enumerate([1046.5, 1318.5, 1568, 2093]):
        s = sfx_ding(f, .8) * .6; o = int(i * .07 * SR); out[o:o + len(s)] += s[:len(out) - o]
    return out
def sfx_whoosh(d=.5):        # 슉: 장면 전환
    rs = np.random.RandomState(7); n = rs.randn(int(d * SR))
    tt = t_(d); w = np.clip((np.sin(np.pi * tt / d)) ** 2, 0, 1)
    # 가변 저역통과 (이동평균 길이를 시간에 따라 바꿈)
    y = np.zeros_like(n); acc = 0.0
    for i in range(len(n)):
        a = .02 + .25 * w[i]; acc += a * (n[i] - acc); y[i] = acc
    return y * w * 1.6
def sfx_boing():             # 폴짝: 캐릭터 점프
    d = .32; tt = t_(d); f = 260 + 520 * (tt / d) + 25 * np.sin(2 * np.pi * 18 * tt)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(d, 7) * .7
def sfx_wobble():            # 뾰로롱: 하나가 남음
    out = np.zeros(int(.5 * SR))
    for i, f in enumerate([700, 560, 700, 560]):
        s = sfx_pop(f) * .8; o = int(i * .1 * SR); out[o:o + len(s)] += s
    return out
def sfx_soft_chime(f=660):   # 은은한 강조
    return sfx_ding(f, .9) * .5

def sfx_drip():              # 똑: 물방울
    d = .18; return sweep(1100, 420, d) * env_exp(d, 22) * .8
def sfx_bubble():            # 보글: 산소 방울
    d = .16; return sweep(380, 900, d) * env_exp(d, 20) * .7
def sfx_grow():              # 쑥: 식물이 자람
    d = .6; tt = t_(d); f = 240 + 380 * (tt / d) ** 1.5
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, tt / .05) * env_exp(d, 4.5) * .55

# (시각, 소리, 볼륨)
def sfx_events():
    ev = []
    add = lambda t, s, v=1.0: ev.append((t, s, v))
    # 타이틀
    add(.3, sfx_whoosh(.5), .7); add(.8, sfx_grow(), .9); add(2.2, sfx_pop(620)); add(2.9, sfx_sparkle(), .7)
    # 종이 장면 전환
    for T in [7, 22, 48, 68, 92, 112, 132]: add(T - .5, sfx_whoosh(.9), .8)
    # 궁금해요
    add(7.7, sfx_pop(540)); add(9.2, sfx_wobble(), .8); add(11.4, sfx_grow(), .9)
    for s in [12.4, 13.2, 14.0]: add(s, sfx_pop(700), .7)
    add(15.7, sfx_sparkle(), .9); add(16.3, sfx_ding(880), .8); add(17.0, sfx_pop(620))
    # 재료
    for i, s in enumerate([22.8, 23.5, 24.2]): add(s, sfx_pop(560 + i * 90), .8)
    add(26.7, sfx_sparkle(), .8); add(27.6, sfx_soft_chime(880), .5)
    for i in range(6): add(31.7 + i * .85, sfx_drip(), .7)
    add(31.6, sfx_soft_chime(660), .5)
    for i in range(5): add(37.7 + i * .9, sfx_pop(500 + i * 50), .5)
    add(39.6, sfx_pop(760)); add(40.0, sfx_soft_chime(990), .6); add(43.9, sfx_ding(784), .7)
    # 장소
    add(48.7, sfx_pop(600)); add(50.0, sfx_soft_chime(880), .5)
    add(53.3, sfx_pop(640))
    for i in range(6): add(54.2 + i * .5, sfx_pop(520 + i * 40), .5)
    add(58.7, sfx_pop(700)); add(60.0, sfx_sparkle(), .8); add(62.0, sfx_soft_chime(990), .5)
    # 반응
    add(68.7, sfx_pop(600))
    for i in range(5): add(69.5 + i * 1.0, sfx_pop(480 + i * 40), .4)
    add(73.7, sfx_ding(988), .9)
    for i in range(4): add(74.2 + i * .9, sfx_bubble(), .6)
    for s in [80.6, 81.4, 82.2, 83.2, 84.4, 85.2, 86.0]: add(s, sfx_pop(560 + (s % 5) * 40), .8)
    add(86.6, sfx_pop(760), .6); add(87.7, sfx_sparkle(), .9); add(88.0, sfx_ding(1046.5), .7)
    # 결과
    add(92.7, sfx_ding(880), .8); add(93.6, sfx_pop(640)); add(95.0, sfx_grow(), .8)
    for i in range(6): add(99.0 + i * .5, sfx_pop(560 + i * 50), .7)
    add(102.4, sfx_ding(784), .7)
    for i in range(8): add(104.9 + i * .7, sfx_bubble(), .7)
    add(108.0, sfx_soft_chime(880), .5)
    # 영향
    for i, s in enumerate([112.8, 113.6, 114.4]): add(s, sfx_pop(560 + i * 90), .8)
    add(118.4, sfx_whoosh(.9), .3); add(121.5, sfx_ding(988), .7)
    add(124.8, sfx_pop(620)); add(125.6, sfx_pop(700)); add(129.0, sfx_soft_chime(880), .5)
    # 정리
    add(132.8, sfx_pop(620))
    for i, s in enumerate([133.4, 134.2, 135.0]): add(s, sfx_pop(540 + i * 60), .7)
    add(136.0, sfx_pop(700)); add(136.6, sfx_pop(760))
    add(138.8, sfx_sparkle(), .9); add(139.2, sfx_ding(1046.5), .8)
    for i in range(6): add(140.0 + i * .7, sfx_bubble(), .6)
    return ev

# ---------------------------------------------------------------- mix
def place(buf, t, x, gain):
    o = int(t * SR)
    if o >= len(buf): return
    n = min(len(x), len(buf) - o); buf[o:o + n] += x[:n] * gain

def build_warp(windows):
    """내레이션이 들어갈 자리가 모자란 구간만 화면 시간을 늘림. [(vs, ve, factor)]"""
    warp = []
    for vs, ve, need in windows:
        f = need / (ve - vs)
        if f > 1.001: warp.append((vs, ve, round(f, 4)))
    return warp

def v2r(v, warp):
    """영상 원본 시간(visual) → 실제 재생 시간(real)"""
    r = v
    for vs, ve, f in warp:
        if v > vs: r += (min(v, ve) - vs) * (f - 1)
    return r

def main():
    say = load_tts()
    clips, windows = [], []
    for start, end, line, _ in NARRATION:
        x = say(line, BASE_SPEED)
        clips.append(x)
        windows.append((start, end, len(x) / SR + PAUSE))
    warp = build_warp(windows)
    total = v2r(DURATION, warp)
    subs = [[s, e, sub if sub else line] for (s, e, line, sub) in NARRATION]
    with open(os.path.join(HERE, '..', 'timeline.js'), 'w') as fp:
        fp.write('// tools/make_audio.py 가 생성: 직접 고치지 말고 NARRATION 을 고친 뒤 다시 실행하세요\n')
        fp.write('// WARP: 내레이션 길이에 맞춰 늘린 구간 [원본 시작, 원본 끝, 배율]\n')
        fp.write('window.WARP = ' + json.dumps([list(w) for w in warp]) + ';\n')
        fp.write('// SUBS: 화면 자막 [원본 시작, 원본 끝, 문구]\n')
        fp.write('window.SUBS = ' + json.dumps(subs, ensure_ascii=False, indent=0) + ';\n')
    voice = np.zeros(int(total * SR), np.float32)
    for (start, end, line, _), x in zip(NARRATION, clips):
        rs = v2r(start, warp)
        print(f'{rs:7.2f}s  {len(x) / SR:4.2f}s  {line}')
        place(voice, rs, x, 1.0)
    voice *= .85 / max(1e-6, np.abs(voice).max())

    fx = np.zeros_like(voice)
    for t, snd, v in sfx_events(): place(fx, v2r(t, warp), snd.astype(np.float32), v)
    fx *= .3 / max(1e-6, np.abs(fx).max())

    # 내레이션이 나올 때 효과음 살짝 줄이기 (사이드체인 덕킹)
    win = int(.05 * SR)
    lvl = np.convolve(np.abs(voice), np.ones(win) / win, 'same')
    duck = 1 - .45 * np.clip(lvl / .05, 0, 1)
    mix = voice + fx * duck
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)          # 부드러운 리미터
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    sf.write(OUT, np.stack([mix, mix], 1), SR, subtype='PCM_16')
    print(f'완료: {os.path.normpath(OUT)}  (영상 길이 {total:.1f}s, 늘린 구간 {len(warp)}개)')

if __name__ == '__main__':
    main()
