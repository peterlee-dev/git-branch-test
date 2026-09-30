"""교육플랫폼팀 30초 홍보 영상 사운드트랙: 통통 튀는 120BPM 비트 + 마림바 멜로디 + 효과음 (모두 numpy 로 합성, 외부 음원 없음)

사용법: python3 tools/make_audio.py  → audio/mix.wav 생성 후 `node render.mjs`
"""
import os
import numpy as np
import soundfile as sf

SR = 44100
DURATION = 30.0
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

def marimba(f, d=.45):
    tt = t_(d); x = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 9) + .35 * np.sin(2 * np.pi * f * 4 * tt) * np.exp(-tt * 30)
    return x * np.minimum(1, tt / .002) * .5
def shaker():
    d = .07; n = rs.randn(int(d * SR)); n = np.diff(n, prepend=0); return n * np.sin(np.linspace(0, np.pi, len(n))) ** 2 * .18
def boing(f0=220, f1=660, d=.28):
    tt = t_(d); f = np.geomspace(f0, f1, len(tt)); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 7) * .6

def place(buf, t, x, g=1.0):
    o = int(t * SR)
    if o >= len(buf): return
    n = min(len(x), len(buf) - o); buf[o:o + n] += x[:n] * g

def main():
    music = np.zeros(int(DURATION * SR)); fx = np.zeros_like(music)
    # 밝은 장조 진행 (C - G - Am - F), 한 마디 = 2초
    prog = [(130.8, [261.6, 329.6, 392.0]), (98.0, [196.0, 246.9, 293.7]), (110.0, [220.0, 261.6, 329.6]), (87.3, [174.6, 220.0, 261.6])]
    SCALE = [523.25, 587.33, 659.25, 783.99, 880.0, 1046.5]          # C 장조 5음 음계
    MEL = [0, 2, 4, 2, 5, 4, 2, 0, 1, 2, 4, 5, 4, 2, 1, 2]              # 16분음표 두 마디 멜로디 패턴
    for bar in range(15):
        t0 = bar * 2.0; root, chord = prog[bar % 4]
        place(music, t0, pad(chord, 2.1), .7)
        for b in range(4):
            tb = t0 + b * BEAT
            drums = 4 <= t0 < 25 or t0 >= 26
            if drums or t0 >= 2: place(music, tb, kick(), .9 if drums else .5)
            if drums and b in (1, 3): place(music, tb, clap(), .8)
            for s16 in range(4): place(music, tb + s16 * BEAT / 4, shaker(), .7 if drums else .35)
            if drums: place(music, tb, bass(root, BEAT * .45), .9); place(music, tb + BEAT / 2, bass(root * 2, BEAT * .3), .6)
        if t0 >= 2:                                   # 통통 튀는 마림바
            for i in range(16):
                if (i + bar) % 5 == 4: continue
                place(music, t0 + i * BEAT / 2 * .5 * 2 / 2, marimba(SCALE[(MEL[i] + bar) % len(SCALE)]), .55)
    place(music, 3.0, riser(1.0), .5)
    # 효과음 (장면 전환·등장에 맞춤)
    for t in [3.55, 7.55, 11.55, 15.55, 19.55, 24.6]: place(fx, t, sfx_whoosh(.45), .9)
    place(fx, .3, sfx_pop(800), .7)
    for i in range(3): place(fx, .6 + i * .05, boing(260 + i * 60, 700 + i * 80), .5)
    for i in range(7): place(fx, 1.1 + i * .07 + .3, sfx_pop(520 + i * 70), .6)
    place(fx, 1.8, sfx_sparkle(), .8)
    for i in range(4): place(fx, 4.5 + i * .25, sfx_pop(600 + i * 90), .7)
    for i in range(4): place(fx, 5.0 + i * .5, boing(300, 900, .22), .7)
    place(fx, 6.2, sfx_pop(900), .6)
    for i, t in enumerate([8.8, 9.3, 9.8, 10.3]): place(fx, t + .32, kick(), .5); place(fx, t + .32, sfx_pop(500 + i * 80), .6)
    place(fx, 10.9, kick(), 1.0); place(fx, 10.9, clap(), .9); place(fx, 11.0, sfx_sparkle(), .7)
    for i in range(8): place(fx, 12.4 + i * BEAT, sfx_pop(600 + i * 60), .6)
    for i, t in enumerate([16.3, 16.7]): place(fx, t, boing(250, 800), .7)
    for i in range(8): place(fx, 16 + i * BEAT, sfx_tick(1800 - (i % 2) * 400), .35)
    place(fx, 18.2, sfx_pop(760), .6)
    place(fx, 20.9, boing(400, 1200, .3), .7)
    for i in range(24): place(fx, 21.3 + i * 1.2 / 24, sfx_tick(2200 + (i % 3) * 300), .3)
    for i in range(5): place(fx, 22.7 + i * .2, sfx_pop(700 + i * 90), .7)
    place(fx, 22.7, sfx_sparkle(), .6)
    place(fx, 25.1, sfx_pop(500), .7); place(fx, 25.5, sfx_tick(1200), 1.0); place(fx, 25.6, sfx_sparkle(), .9); place(fx, 25.6, clap(), .8)
    for i in range(6): place(fx, 26.0 + i * .05, sfx_pop(600 + i * 50), .4)
    for i in range(4): place(fx, 26.6 + i * .08, sfx_pop(800 + i * 60), .5)
    place(fx, 27.4, sfx_ding(1046.5), .7)
    mix = music / max(1e-6, np.abs(music).max()) * .75 + fx / max(1e-6, np.abs(fx).max()) * .35
    tt = np.arange(len(mix)) / SR
    mix *= np.minimum(1, tt / .05) * np.clip((DURATION - tt) / 1.2, 0, 1)   # 끝 1.2초 페이드아웃
    mix = np.tanh(mix * 1.2) / np.tanh(1.2)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    sf.write(OUT, np.stack([mix, mix], 1), SR, subtype='PCM_16')
    print('완료:', os.path.normpath(OUT))

if __name__ == '__main__':
    main()
