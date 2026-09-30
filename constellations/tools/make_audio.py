"""별자리 영상 사운드트랙: 앰비언트 패드 + 별 반짝임 + 카메라 이동음 (모두 numpy 로 합성, 외부 음원 없음)

사용법: python3 tools/make_audio.py  → audio/mix.wav 생성 후 `node render.mjs`
"""
import os
import numpy as np
import soundfile as sf

SR = 44100
DURATION = 30.0
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'audio', 'mix.wav')
rs = np.random.RandomState(7)

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

def pad(freqs, d, bright=.25):
    tt = t_(d); x = np.zeros(len(tt))
    for i, f in enumerate(freqs):
        for det in (-.3, .3):                       # 살짝 어긋난 두 음으로 넓게
            x += np.sin(2 * np.pi * (f + det) * tt + i) + bright * np.sin(2 * np.pi * 2 * (f + det) * tt)
    x /= len(freqs) * 2
    return x * np.minimum(1, tt / 1.5) * np.minimum(1, (d - tt) / 1.5)
def shimmer(f, d=2.2):                               # 별이 이어질 때 맑은 종소리
    tt = t_(d); x = sum(a * np.sin(2 * np.pi * f * m * tt) * np.exp(-tt * k) for m, a, k in [(1, 1, 2.2), (2.01, .4, 3.5), (3.02, .15, 5)])
    return x * np.minimum(1, tt / .003) * .5
def swell(d):                                        # 카메라 이동: 부드러운 바람
    tt = t_(d); n = rs.randn(len(tt)); y = np.zeros_like(n); acc = 0.0
    w = np.sin(np.pi * tt / d) ** 2
    for i in range(len(n)):
        a = .004 + .05 * w[i]; acc += a * (n[i] - acc); y[i] = acc
    return y * w * 5

def place(buf, t, x, g=1.0):
    o = int(t * SR)
    if o >= len(buf): return
    n = min(len(x), len(buf) - o); buf[o:o + n] += x[:n] * g

# 카메라 이동 구간 / 별자리 선이 그려지는 시각 (index.html 의 CAM, CONST 와 같음)
MOVES = [(0, 3.6), (3.6, 4.8), (8.2, 9.2), (10.6, 11.8), (15.8, 17.4), (21.8, 23.6), (26.8, 28.8)]
LINES = [(5.0, 2.2, 7), (8.9, 1.2, 2), (11.8, 1.6, 4), (17.4, 2.0, 8), (23.6, 1.2, 4), (24.4, 1.4, 3)]
PENTA = [523.25, 587.33, 659.25, 783.99, 880.0, 1046.5, 1174.7, 1318.5]    # C 장조 5음 음계

def main():
    music = np.zeros(int(DURATION * SR)); fx = np.zeros_like(music)
    chords = [[130.8, 196.0, 261.6, 329.6], [110.0, 164.8, 220.0, 329.6], [87.3, 130.8, 174.6, 261.6], [98.0, 146.8, 196.0, 293.7]]
    for i in range(6):                                # 5초마다 코드 (C - Am - F - G …)
        place(music, i * 5.0 - .5 if i else 0, pad(chords[i % 4], 6.5), 1.0)
    for s, e in MOVES: place(fx, s, swell(max(.8, e - s)), .55)
    for s, d, n in LINES:                             # 선분마다 한 음씩 올라가는 반짝임
        per = d / n
        for i in range(n): place(fx, s + i * per * .8, shimmer(PENTA[(i + int(s)) % len(PENTA)]), .7)
    for t in [9.4, 25.2]: place(fx, t, sfx_sparkle(), .7)            # 북극성, 은하수
    place(fx, .6, shimmer(523.25, 3), .6); place(fx, 27.8, shimmer(392.0, 3), .6); place(fx, 28.3, sfx_sparkle(), .6)
    mix = music / max(1e-6, np.abs(music).max()) * .55 + fx / max(1e-6, np.abs(fx).max()) * .45
    tt = np.arange(len(mix)) / SR
    mix *= np.minimum(1, tt / 1.0) * np.clip((DURATION - tt) / 1.5, 0, 1)
    # 간단한 잔향 (여러 지연을 섞음)
    wet = np.zeros_like(mix)
    for dl, g in [(.071, .35), (.113, .28), (.173, .22), (.251, .16), (.337, .11)]:
        k = int(dl * SR); wet[k:] += mix[:-k] * g
    mix = mix + wet * .8
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    sf.write(OUT, np.stack([mix, np.roll(mix, int(.012 * SR))], 1), SR, subtype='PCM_16')
    print('완료:', os.path.normpath(OUT))

if __name__ == '__main__':
    main()
