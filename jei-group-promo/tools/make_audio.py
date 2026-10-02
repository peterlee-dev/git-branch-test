"""재능그룹 홍보 영상 사운드트랙: 120BPM 비트 + 효과음 (모두 numpy 로 합성, 외부 음원 없음)
효과음 시각은 화면에서 뽑은 tools/events.json (node tools/export_events.mjs) 을 따름

사용법: python3 tools/make_audio.py  → audio/mix.wav 생성 후 `node render.mjs`
"""
import os
import numpy as np
import soundfile as sf

SR = 44100
DURATION = 52.0
BPM = 120
BEAT = 60 / BPM
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'audio', 'mix.wav')
rs = np.random.RandomState(3)

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

def kick():
    d = .35; tt = t_(d); f = 45 + 110 * np.exp(-tt * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9) * 1.0
def hat(open_=False):
    d = .18 if open_ else .05; n = rs.randn(int(d * SR)); n = np.diff(n, prepend=0)
    return n * env_exp(d, 18 if open_ else 70) * .25
def clap():
    d = .2; n = rs.randn(int(d * SR)); e = np.zeros(len(n))
    for o in [0, .012, .024]: i = int(o * SR); e[i:] += np.exp(-np.arange(len(n) - i) / SR * 30)
    y = np.convolve(n, np.ones(6) / 6, 'same'); return y * e * .35
def bass(f, d):
    tt = t_(d); x = np.sin(2 * np.pi * f * tt) + .35 * np.sin(2 * np.pi * 2 * f * tt)
    return x * np.minimum(1, tt / .01) * np.exp(-tt * 3.2) * .45
def pad(freqs, d):
    tt = t_(d); x = sum(np.sin(2 * np.pi * f * tt + i) + .3 * np.sin(2 * np.pi * f * 2.003 * tt) for i, f in enumerate(freqs))
    return x / len(freqs) * np.minimum(1, tt / .8) * np.minimum(1, (d - tt) / .8) * .18
def riser(d):
    tt = t_(d); n = rs.randn(len(tt)); y = np.zeros_like(n); acc = 0.0
    for i in range(len(n)):
        a = .01 + .3 * (tt[i] / d) ** 2; acc += a * (n[i] - acc); y[i] = acc
    return y * (tt / d) ** 2 * .9

def place(buf, t, x, g=1.0):
    o = int(t * SR)
    if o >= len(buf): return
    n = min(len(x), len(buf) - o); buf[o:o + n] += x[:n] * g

def main():
    import json
    music = np.zeros(int(DURATION * SR)); fx = np.zeros_like(music)
    # C - G - Am - F (한 마디 2초에 코드 하나). 4~44초는 비트, 그 앞뒤는 패드만
    prog = [(130.81, [261.63, 329.63, 392.0]), (98.0, [246.94, 293.66, 392.0]), (110.0, [220.0, 261.63, 329.63]), (87.31, [220.0, 261.63, 349.23])]
    for bar in range(int(DURATION // 2)):
        t0 = bar * 2.0; root, chord = prog[bar % 4]
        place(music, t0, pad(chord, 2.1), .9 if 4 <= t0 < 44 else 1.1)
        for b in range(4):
            tb = t0 + b * BEAT
            on = 4 <= t0 < 44
            if on: place(music, tb, kick(), .85)
            if on and b in (1, 3): place(music, tb, clap(), .6)
            place(music, tb + BEAT / 2, hat(b == 3), .7 if on else .25)
            if on: place(music, tb, bass(root, BEAT * .9), .8); place(music, tb + BEAT * .75, bass(root * 2, BEAT * .2), .35)
    place(music, 2.0, riser(2.0), .5); place(music, 42.0, riser(2.0), .5)       # 비트 시작·엔딩 직전 상승음
    place(music, 44.0, kick(), 1.0); place(music, 44.0, pad([261.63, 329.63, 392.0, 523.25], 7.5), 1.6)
    ev = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'events.json')))
    for e in ev:
        t, k, i = e['t'], e['type'], e['info']
        if k == 'wipe': place(fx, t - .05, sfx_whoosh(.5), .8)
        elif k == 'slam': place(fx, t, sfx_ding(784 if t < 44 else 523.25), .5)
        elif k == 'card': place(fx, t, sfx_pop(520 + i * 90), .55)
        elif k == 'chip': place(fx, t, sfx_tick(1400 + i * 120), .4)
        elif k == 'tick': place(fx, t, sfx_tick(1500 + (int(i) % 7) * 80), .35)
        elif k == 'node': place(fx, t, sfx_tick(1700 + (int(i) % 8) * 60), .22)
    place(fx, 44.25, sfx_sparkle(), .7)
    tt = np.arange(len(music)) / SR
    mix = music * .55 + fx * .5
    mix *= np.minimum(1, tt / .05) * np.clip((DURATION - tt) / 1.8, 0, 1)
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    mix = mix / (np.abs(mix).max() + 1e-9) * .89
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'audio', 'mix.wav')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sf.write(out, np.stack([mix, mix], 1).astype(np.float32), SR, subtype='PCM_16')
    print(f'완료: {os.path.normpath(out)} ({DURATION}초)')

if __name__ == '__main__':
    main()
