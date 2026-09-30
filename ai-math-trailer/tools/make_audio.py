"""재능스스로AI수학 리뉴얼 예고편 음악: 드론 · 피아노 · 별 종소리 · 브람(BRAAM) · 타격 · 째깍 · 라이저 · 마지막 스팅
모두 numpy 로 합성 (외부 음원 없음). 시각은 ../timeline.js 를 읽어 화면과 같게 맞춤

사용법: python3 tools/make_audio.py → audio/mix.wav 생성 후 `node render.mjs`
"""
import os, json, re
import numpy as np
import soundfile as sf

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'audio', 'mix.wav')
TL = json.loads(re.search(r'window\.TL\s*=\s*(\{.*\});', open(os.path.join(HERE, '..', 'timeline.js'), encoding='utf-8').read(), re.S).group(1))
DUR = TL['duration']; N = int(DUR * SR); rs = np.random.RandomState(3)
t_ = lambda d: np.arange(int(d * SR)) / SR

def place(buf, t, x, g=1.0):
    o = int(t * SR)
    if o >= len(buf) or o + len(x) <= 0: return
    if o < 0: x = x[-o:]; o = 0
    n = min(len(x), len(buf) - o); buf[o:o + n] += x[:n] * g
def lp(x, k):
    for _ in range(3): x = np.convolve(x, np.ones(k) / k, 'same')
    return x
def piano(f, d=3.0):
    tt = t_(d); x = sum(a * np.sin(2 * np.pi * f * m * tt) * np.exp(-tt * k) for m, a, k in [(1, 1, 1.4), (2, .45, 2.2), (3, .22, 3.5), (4.02, .1, 5)])
    return x * np.minimum(1, tt / .004) * .5
def bell(f, d=2.5):
    tt = t_(d); x = sum(a * np.sin(2 * np.pi * f * m * tt) * np.exp(-tt * k) for m, a, k in [(1, 1, 1.8), (2.76, .35, 3), (5.4, .15, 6)])
    return x * np.minimum(1, tt / .002) * .35
def drone(f, d, bright=.2):
    tt = t_(d); x = np.zeros(len(tt))
    for det in (-.35, 0, .35): x += np.sin(2 * np.pi * (f + det) * tt) + bright * np.sin(2 * np.pi * 2 * (f + det) * tt) + bright * .5 * np.sin(2 * np.pi * 3 * (f + det) * tt)
    return x / 3 * np.minimum(1, tt / 2.5) * np.minimum(1, (d - tt) / 1.5)
def braam(d=4.5):                                   # 영화 예고편의 '브아아암'
    tt = t_(d); x = np.zeros(len(tt))
    for f in (36.7, 55.0, 73.4, 110.0):
        ph = 2 * np.pi * f * tt; saw = 2 * ((ph / (2 * np.pi)) % 1) - 1
        x += saw * (1 if f < 80 else .6)
    x = lp(x, 6); x = np.tanh(x * 2.2)
    return x * np.minimum(1, tt / .02) * np.exp(-tt * .75) * .9
def boom(d=2.5):                                    # 큰북 타격
    tt = t_(d); f = 38 + 90 * np.exp(-tt * 18)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 2.2)
    hitn = lp(rs.randn(len(tt)), 3) * np.exp(-tt * 30) * .6
    return np.tanh((body + hitn) * 1.6) * .9
def tick():
    d = .03; return lp(rs.randn(int(d * SR)), 2) * np.exp(-np.arange(int(d * SR)) / SR * 160) * .7
def riser(d):
    tt = t_(d); n = rs.randn(len(tt)); y = np.zeros_like(n); acc = 0.0
    for i in range(len(n)):
        a = .005 + .35 * (tt[i] / d) ** 2; acc += a * (n[i] - acc); y[i] = acc
    tone = np.sin(2 * np.pi * np.cumsum(np.geomspace(110, 880, len(tt))) / SR) * .25
    return (y * 2.5 + tone) * (tt / d) ** 2
def whoosh(d=.7):
    tt = t_(d); n = rs.randn(len(tt)); w = np.sin(np.pi * tt / d) ** 2; y = np.zeros_like(n); acc = 0.0
    for i in range(len(n)):
        a = .01 + .2 * w[i]; acc += a * (n[i] - acc); y[i] = acc
    return y * w * 3
def shimmer(freqs, d):
    tt = t_(d); x = sum(np.sin(2 * np.pi * f * tt + i) * (1 + .3 * np.sin(2 * np.pi * (5 + i) * tt)) for i, f in enumerate(freqs)) / len(freqs)
    return x * np.minimum(1, tt / .8) * np.minimum(1, (d - tt) / 2) * .35

def main():
    music = np.zeros(N); hits = np.zeros(N)
    # 1막 (0~17초): 낮은 드론 + 피아노, 별이 켜질 때마다 종소리
    place(music, 0.4, drone(55.0, 16.8, .15), .5)
    place(music, 4.5, drone(110.0, 12.5, .1), .25)
    notes = [440.0, 523.25, 659.25, 587.33, 523.25, 659.25, 783.99]          # A 단조 → C 장조로 밝아짐
    for i, t in enumerate(TL['ignite']): place(music, t, piano(notes[i]), .55); place(music, t, bell(notes[i] * 2), .5)
    for i, t in enumerate([1.0, 2.6]): place(music, t, piano([220.0, 261.63][i], 4), .5)
    c0, c1 = TL['connect']
    for i in range(7): place(music, c0 + i * (c1 - c0) / 7, bell([1046.5, 1174.7, 1318.5, 1568.0, 1760.0, 2093.0, 2349.3][i], 2), .35)
    place(music, TL['reward'], shimmer([523.25, 659.25, 783.99, 1046.5], 3.2), .9)
    place(music, 15.2, riser(1.8), .5)
    # 브람 + 정적
    for t in TL['braam']: place(hits, t, braam(), 1.0); place(hits, t, boom(), .7)
    # 2막 (19~28초): 앱 화면마다 타격 + 긴장감 있는 박동
    place(music, 19.0, drone(41.2, 9.5, .35), .55)
    for t in TL['ui']: place(hits, t, boom(), .85); place(hits, t - .5, whoosh(.6), .5); place(music, t, piano(329.63, 2.2), .35)
    for k in range(int(9 / .5)): place(music, 19.0 + k * .5, boom(.4) * .25, .5)          # 심장 박동 같은 저음
    # 3막 (28~32.6초): 몽타주 — 컷마다 째깍·타격, 라이저로 끌어올림
    for i, t in enumerate(TL['montage']): place(hits, t, tick(), .9); place(hits, t, boom(.5), .25 + .02 * i)
    s0, s1 = TL['silence']
    place(music, 28.0, riser(s0 - 28.0), .9)
    # 정적 (s0~s1) 뒤 타이틀: 가장 큰 타격 + 밝은 코드
    place(hits, TL['title'], braam(6), 1.0); place(hits, TL['title'], boom(3), 1.0)
    place(music, TL['title'], shimmer([261.63, 329.63, 392.0, 523.25, 587.33], 11), 1.0)
    place(music, TL['title'], drone(65.4, 11, .2), .45)
    place(music, TL['title'] + .6, bell(2093.0, 3), .4)
    # 개봉일 스팅
    place(hits, TL['sting'], boom(3), .9); place(music, TL['sting'], piano(523.25, 3.5), .5); place(music, TL['sting'], bell(1046.5, 3.5), .5)
    mix = music / (np.abs(music).max() + 1e-9) * .6 + hits / (np.abs(hits).max() + 1e-9) * .75
    mix[int(s0 * SR):int(s1 * SR)] *= np.linspace(1, 0, int(s1 * SR) - int(s0 * SR)) ** 4          # 타이틀 직전 정적
    # 잔향 (여러 지연)
    wet = np.zeros_like(mix)
    for dl, g in [(.047, .4), (.089, .32), (.143, .25), (.211, .19), (.307, .13), (.421, .09)]:
        k = int(dl * SR); wet[k:] += mix[:-k] * g
    mix = mix + wet * .6
    tt = np.arange(N) / SR; mix *= np.clip((DUR - tt) / 1.2, 0, 1)
    mix = np.tanh(mix * 1.3) / np.tanh(1.3) * .92
    L, Rr = mix, np.roll(mix, int(.011 * SR))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    sf.write(OUT, np.stack([L, Rr], 1), SR, subtype='PCM_16')
    print('완료:', os.path.normpath(OUT))

if __name__ == '__main__':
    main()
