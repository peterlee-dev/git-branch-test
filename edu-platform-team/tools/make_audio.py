"""교육플랫폼팀 30초 홍보 영상 사운드트랙: 통통 튀는 120BPM 비트 + 마림바 멜로디 + 효과음

효과음은 tools/events.json (node tools/export_events.mjs 로 영상에서 뽑은 등장·착지 시각)에 맞춰 놓아서 화면과 소리가 같은 박자에 맞음 (모두 numpy 로 합성, 외부 음원 없음)

사용법: python3 tools/make_audio.py  → audio/mix.wav 생성 후 `node render.mjs`
"""
import os
import numpy as np
import soundfile as sf
import json

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
            for i in range(8):
                place(music, t0 + i * BEAT / 2, marimba(SCALE[(MEL[i * 2] + bar) % len(SCALE)]), .38)
    place(music, 3.0, riser(1.0), .5)
    # 효과음: 영상에서 뽑은 이벤트 시각에 그대로 놓음
    events = json.load(open(os.path.join(HERE, 'events.json')))
    land_i = 0
    for e in events:
        t, kind, info = e['t'], e['type'], e['info']
        if kind == 'land':                            # 글자가 바닥에 닿는 순간: 음계를 따라 오르는 통통 소리
            f = SCALE[land_i % len(SCALE)] * (0.5 if info >= 180 else 1); land_i += 1
            place(fx, t, marimba(f, .25), .5 if info >= 120 else .35)
            if info >= 180: place(fx, t, kick(), .25)
        elif kind == 'pop': place(fx, t, sfx_pop(620 + (int(t * 4) % 5) * 70), .65)
        elif kind == 'ball': place(fx, t, boing(260 + info * 60, 780 + info * 90, .24), .8); place(fx, t, kick(), .3)
        elif kind == 'block': place(fx, t, kick(), .6); place(fx, t, sfx_pop(420 + info * 80), .7)
        elif kind == 'stamp': place(fx, t, kick(), 1.0); place(fx, t, clap(), 1.0); place(fx, t, sfx_tick(900), .8)
        elif kind == 'double': place(fx, t, sfx_pop(520 * 2 ** (info / 7)), .6)
        elif kind == 'device': place(fx, t, boing(300 if info else 380, 700 if info else 900, .2), .55)
        elif kind == 'wipe': place(fx, t - .05, sfx_whoosh(.5), .85)
        elif kind == 'burst': place(fx, t, sfx_sparkle(), .8)
        elif kind == 'toggle': place(fx, t, sfx_tick(1400), 1.0); place(fx, t, clap(), .7)
    # AI 프롬프트 타이핑 (21.3초부터 1.2초, 16분음표마다)
    for i in range(10): place(fx, 21.25 + i * BEAT / 4 * .96, sfx_tick(2200 + (i % 3) * 300), .3)
    mix = music / max(1e-6, np.abs(music).max()) * .75 + fx / max(1e-6, np.abs(fx).max()) * .35
    tt = np.arange(len(mix)) / SR
    mix *= np.minimum(1, tt / .05) * np.clip((DURATION - tt) / 1.2, 0, 1)   # 끝 1.2초 페이드아웃
    mix = np.tanh(mix * 1.2) / np.tanh(1.2)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    sf.write(OUT, np.stack([mix, mix], 1), SR, subtype='PCM_16')
    print('완료:', os.path.normpath(OUT))

if __name__ == '__main__':
    main()
