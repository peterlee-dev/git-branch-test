"""교육플랫폼팀 30초 홍보 영상 사운드트랙: 120BPM 비트 + 효과음 (모두 numpy 로 합성, 외부 음원 없음)

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

def place(buf, t, x, g=1.0):
    o = int(t * SR)
    if o >= len(buf): return
    n = min(len(x), len(buf) - o); buf[o:o + n] += x[:n] * g

def main():
    music = np.zeros(int(DURATION * SR)); fx = np.zeros_like(music)
    # 코드 진행 (A minor: Am - F - C - G), 한 마디 = 2초
    prog = [(110.0, [220, 261.6, 329.6]), (87.3, [174.6, 220, 261.6]), (130.8, [261.6, 329.6, 392]), (98.0, [196, 246.9, 293.7])]
    for bar in range(15):
        t0 = bar * 2.0; root, chord = prog[bar % 4]
        place(music, t0, pad(chord, 2.1), 1.0)
        full = 2.0 <= t0 < 25.0            # 4초 전까지는 인트로(패드+하이햇만), 25초부터 엔딩
        for b in range(4):
            tb = t0 + b * BEAT
            if t0 >= 4 and t0 < 25: place(music, tb, kick(), .9)
            if t0 >= 4 and t0 < 25 and b in (1, 3): place(music, tb, clap(), .8)
            place(music, tb + BEAT / 2, hat(b == 3), .8 if t0 >= 2 else .4)
            if t0 >= 4 and t0 < 25: place(music, tb, bass(root, BEAT * .9), .9); place(music, tb + BEAT * .75, bass(root * 2, BEAT * .2), .4)
    place(music, 2.0, riser(2.0), .6)                                  # 드롭 직전 상승음
    place(music, 25.0, kick(), 1.0); place(music, 25.0, sfx_sparkle(), .8)
    place(music, 25.0, pad([220, 261.6, 329.6, 440], 4.9), 1.6)
    # 효과음
    def key():                                        # 키보드 타건음
        d = .03; n = rs.randn(int(d * SR)); return n * env_exp(d, 140) * .6
    for i in range(27): place(fx, .3 + i * 1.1 / 27, key(), .5 + .3 * rs.rand())
    for t in [3.55, 7.55, 11.55, 24.6]: place(fx, t, sfx_whoosh(.45), .9)
    for t in [4.0, 15.7, 20.0]:                        # 글리치
        for j in range(6): place(fx, t + j * .03, sfx_tick(2400 - j * 200), .6)
    for i in range(4): place(fx, 4.6 + i * .45, sfx_pop(520 + i * 90), .7)
    for i in range(12): place(fx, 5.3 + i * .18, sfx_tick(1600), .25)
    for i, t in enumerate([9.2, 9.8, 10.4, 10.9]): place(fx, t, sfx_whoosh(.3), .4); place(fx, t + .45, sfx_tick(900), .8)
    place(fx, 11.2, sfx_ding(988), .7)
    for i in range(20): place(fx, 12.3 + i * .06, sfx_pop(700 + i * 30), .25)
    place(fx, 13.2, sfx_sparkle(), .6)
    place(fx, 16.5, sfx_whoosh(.5), .5); place(fx, 17.0, sfx_whoosh(.5), .5); place(fx, 17.8, sfx_soft_chime(880) if 'sfx_soft_chime' in globals() else sfx_ding(880), .5)
    for i in range(30): place(fx, 21.0 + i * 1.4 / 30, key(), .45 + .3 * rs.rand())
    place(fx, 22.4, sfx_pop(900), .8)
    for i in range(5): place(fx, 22.7 + i * .22, sfx_tick(1300 + i * 150), .6)
    place(fx, 23.8, sfx_sparkle(), .6)
    place(fx, 25.5, sfx_ding(784), .7); place(fx, 25.8, sfx_ding(1046.5), .7); place(fx, 26.6, sfx_sparkle(), .7)
    mix = music / max(1e-6, np.abs(music).max()) * .75 + fx / max(1e-6, np.abs(fx).max()) * .35
    tt = np.arange(len(mix)) / SR
    mix *= np.minimum(1, tt / .05) * np.clip((DURATION - tt) / 1.2, 0, 1)   # 끝 1.2초 페이드아웃
    mix = np.tanh(mix * 1.2) / np.tanh(1.2)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    sf.write(OUT, np.stack([mix, mix], 1), SR, subtype='PCM_16')
    print('완료:', os.path.normpath(OUT))

if __name__ == '__main__':
    main()
