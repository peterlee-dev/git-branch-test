"""수학 개념 영상용 내레이션(TTS) + 효과음 믹스 생성.

- 내레이션: Supertonic 3 (sherpa-onnx, 온디바이스 소형 TTS, 한국어)
- 효과음: numpy 로 직접 합성 (외부 음원 없음)

사용법:
  pip install sherpa-onnx soundfile numpy
  # 모델: https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/sherpa-onnx-supertonic-3-tts-int8-2026-05-11.tar.bz2
  TTS_MODEL_DIR=/path/to/sherpa-onnx-supertonic-3-tts-int8-2026-05-11 python3 tools/make_audio.py
  → audio/mix.wav 생성 후 `node render.mjs` 로 영상에 합성
"""
import os, sys
import numpy as np
import soundfile as sf

SR = 44100
DURATION = 114.0
VOICE_SID = 1          # Supertonic 3 음성 (0~4 여성, 5~9 남성)
BASE_SPEED = 1.0
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'audio', 'mix.wav')

# (시작 시각, 끝 시각[이 안에 끝나야 함], 읽을 문장) — 숫자는 읽는 방식대로 한글로 적음
NARRATION = [
    (1.0, 6.6, '수학 일 학년 이 학기, 백까지의 수! 단원 개념을 함께 정리해 볼까요?'),
    (7.5, 8.6, '세어 볼까요?'),
    (8.65, 9.4, '십!'), (9.45, 10.2, '이십!'), (10.25, 11.0, '삼십!'),
    (11.05, 11.8, '사십!'), (11.85, 12.6, '오십!'), (12.65, 13.4, '육십!'),
    (13.5, 16.0, '십 개씩 묶음 여섯 개를 육십이라고 해요.'),
    (16.1, 19.2, '육십은 육십 또는 예순이라고 읽어요.'),
    (19.5, 23.4, '십 개씩 묶음 일곱 개는 칠십, 칠십 또는 일흔이에요.'),
    (23.5, 26.9, '십 개씩 묶음 여덟 개는 팔십, 팔십 또는 여든이에요.'),
    (27.1, 30.6, '십 개씩 묶음 아홉 개는 구십, 구십 또는 아흔이에요.'),
    (31.7, 36.0, '십 개씩 묶음 일곱 개와 낱개 세 개가 있어요.'),
    (36.1, 39.4, '이것을 칠십삼이라고 해요.'),
    (39.5, 44.4, '칠십삼은 칠십삼 또는 일흔셋이라고 읽어요.'),
    (45.7, 49.2, '구십보다 일만큼 더 작은 수는 팔십구예요.'),
    (49.3, 52.8, '구십보다 일만큼 더 큰 수는 구십일이에요.'),
    (53.4, 57.0, '오십일부터 백까지, 수의 순서를 알아볼까요?'),
    (57.1, 61.8, '오른쪽으로 한 칸 갈 때마다 일씩 커져요!'),
    (62.5, 65.2, '구십구보다 일만큼 더 큰 수는 얼마일까요?'),
    (65.3, 68.0, '낱개 열 개는 십 개씩 묶음 한 개! 그래서 백이에요.'),
    (68.1, 70.6, '백은 백이라고 읽어요.'),
    (71.7, 74.5, '오십육과 육십이, 어느 수가 더 클까요?'),
    (74.6, 77.0, '십 개씩 묶음의 수를 먼저 비교해요. 오는 육보다 작아요.'),
    (77.1, 80.4, '오십육은 육십이보다 작아요. 육십이는 오십육보다 커요.'),
    (80.9, 83.5, '구십사와 구십일은 십 개씩 묶음의 수가 같아요.'),
    (83.6, 86.0, '그럼 낱개의 수를 비교해요. 사는 일보다 커요.'),
    (86.1, 88.6, '구십사는 구십일보다 커요. 구십일은 구십사보다 작아요.'),
    (89.7, 92.6, '여섯 개와 일곱 개를 둘씩 짝을 지어 볼까요?'),
    (92.7, 95.2, '육은 남는 것이 없어요. 이런 수를 짝수라고 해요.'),
    (95.3, 97.5, '칠은 하나가 남아요. 이런 수를 홀수라고 해요.'),
    (97.9, 101.4, '이, 사, 육, 팔, 십처럼 둘씩 짝을 지을 때 남는 것이 없는 수는 짝수!'),
    (101.5, 105.6, '일, 삼, 오, 칠, 구처럼 둘씩 짝을 지을 때 하나가 남는 수는 홀수!'),
    (106.4, 109.0, '오늘 배운 개념을 다시 볼까요?'),
    (109.1, 112.6, '스스로 정리 끝! 참 잘했어요!'),
]

# ---------------------------------------------------------------- TTS
def load_tts():
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

# (시각, 소리, 볼륨)
def sfx_events():
    ev = []
    add = lambda t, s, v=1.0: ev.append((t, s, v))
    # 타이틀
    add(.2, sfx_boing(), .8); add(.9, sfx_whoosh(.45), .7); add(1.1, sfx_ding(784), .7); add(1.6, sfx_pop(620))
    for i in range(5): add(2.3 + i * .15, sfx_pop(700 + i * 60), .6)
    # 장면 전환
    for T in [6.95, 30.55, 44.55, 70.55, 88.55, 105.55]: add(T, sfx_whoosh(), .9)
    # 개념 1: 막대 쌓기 + 개수 세기
    starts = [8.2, 9.0, 9.8, 10.6, 11.4, 12.2, 20.0, 23.6, 27.2]
    for r, s in enumerate(starts):
        for i in range(10): add(s + i * .045, sfx_tick(1200 + i * 60), .35)
        if r < 6: add(s + .45, sfx_pop(500 + r * 70), .8)
    add(13.6, sfx_ding(880), .9); add(16.1, sfx_pop(600)); add(16.7, sfx_pop(660))
    for s in [19.9, 23.5, 27.1]: add(s + .1, sfx_pop(560)); add(s + .7, sfx_soft_chime(990), .6)
    # 개념 2
    for r in range(7):
        for i in range(10): add(32 + r * .25 + i * .045, sfx_tick(1200 + i * 60), .3)
    for j in range(3): add(34.4 + j * .12, sfx_pop(740 + j * 60), .8)
    add(36.2, sfx_ding(880), .9); add(39.6, sfx_pop(600)); add(40.2, sfx_pop(660))
    # 개념 3-a
    add(45.6, sfx_pop(600)); add(46.5, sfx_boing(), .8); add(47.2, sfx_pop(520)); add(48.7, sfx_boing(), .8); add(49.6, sfx_pop(700))
    add(46.8, sfx_soft_chime(660), .5); add(49.2, sfx_soft_chime(880), .5)
    # 개념 3-b: 수 배열표
    for k in range(9): add(53.3 + k * .07, sfx_pop(500 + k * 40), .35)
    for i in range(0, 50, 2): add(57.2 + i * 3.8 / 50, sfx_tick(900 + i * 25), .45)
    add(61.1, sfx_sparkle(), .6)
    # 개념 3-c: 100
    for r in range(9):
        for i in range(0, 10, 2): add(62.3 + r * .1 + i * .045, sfx_tick(1300 + i * 50), .22)
    for j in range(9): add(63.2 + j * .08, sfx_pop(700 + j * 30), .4)
    add(65.2, sfx_pop(900)); add(65.6, sfx_ding(1046.5), 1.0); add(66.0, sfx_sparkle(), .7); add(68.0, sfx_pop(620))
    # 개념 4
    for T, tags in [(71, 1), (80, 2)]:
        for g, st in enumerate([T + .3, T + .9]):
            for r in range(9 if T == 80 else 6):
                add(st + r * .12, sfx_tick(1400), .2)
        add(T + 1.6, sfx_pop(560)); add(T + 2.1, sfx_pop(620))
        add(T + 3.4, sfx_soft_chime(660), .5); add(T + 3.7, sfx_pop(700))
        if tags == 2: add(T + 5.2, sfx_soft_chime(780), .5); add(T + 5.5, sfx_pop(760))
        add(T + (7 if tags == 2 else 5.6), sfx_ding(988), .9)
    # 개념 5
    for i in range(7): add(89.6 + i * .08, sfx_pop(640 + i * 30), .45)
    add(91.0, sfx_whoosh(.9), .4)
    add(92.3, sfx_soft_chime(784), .5); add(93.1, sfx_ding(1046.5), .8)
    add(95.2, sfx_wobble(), .8); add(95.7, sfx_ding(784), .8)
    for base, st in [(98.1, 0), (101.6, 1)]:
        add(base, sfx_pop(600))
        for i in range(5): add(base + .5 + i * .3, sfx_pop((660 if st == 0 else 520) + i * 50), .7)
    # 정리
    add(106.3, sfx_boing(), .8)
    for i in range(5): add(107 + i * .3, sfx_pop(600 + i * 70), .7)
    add(109.0, sfx_sparkle(), .9); add(109.2, sfx_ding(1046.5), .7)
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
    for start, end, line in NARRATION:
        x = say(line, BASE_SPEED)
        clips.append(x)
        windows.append((start, end, len(x) / SR + .35))
    warp = build_warp(windows)
    total = v2r(DURATION, warp)
    with open(os.path.join(HERE, '..', 'warp.js'), 'w') as fp:
        fp.write('// tools/make_audio.py 가 생성: 내레이션 길이에 맞춰 늘린 구간 [원본 시작, 원본 끝, 배율]\n')
        fp.write('window.WARP = ' + str([list(w) for w in warp]) + ';\n')
    voice = np.zeros(int(total * SR), np.float32)
    for (start, end, line), x in zip(NARRATION, clips):
        rs = v2r(start, warp)
        print(f'{rs:7.2f}s  {len(x) / SR:4.2f}s  {line}')
        place(voice, rs, x, 1.0)
    voice *= .85 / max(1e-6, np.abs(voice).max())

    fx = np.zeros_like(voice)
    for t, snd, v in sfx_events(): place(fx, v2r(t, warp), snd.astype(np.float32), v)
    fx *= .32 / max(1e-6, np.abs(fx).max())

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
