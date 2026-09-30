"""한강 다리 산책 배경음: 바람 + 강물 + 멀리 차 소리 + 발소리 (모두 numpy 로 합성, 외부 음원 없음)

사용법: python3 tools/make_audio.py  → audio/mix.wav 생성 후 `node render.mjs`
"""
import os
import numpy as np
import soundfile as sf

SR = 44100
DURATION = 15.0
STEPS_PER_SEC = 1.85          # index.html 의 걸음 수와 같음
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'audio', 'mix.wav')
rs = np.random.RandomState(15)
N = int(DURATION * SR)
tt = np.arange(N) / SR

def lowpass(x, a):
    y = np.zeros_like(x); acc = 0.0
    for i in range(len(x)): acc += a * (x[i] - acc); y[i] = acc
    return y
def lp_fast(x, k):                               # 이동평균 여러 번 = 부드러운 저역통과
    for _ in range(3): x = np.convolve(x, np.ones(k) / k, 'same')
    return x

def main():
    # 바람: 아주 낮은 소음이 천천히 커졌다 작아짐
    wind = lp_fast(rs.randn(N), 220) * (0.6 + 0.4 * np.sin(2 * np.pi * tt / 6.5) ** 2) * 9
    # 강물: 중간 대역 소음 + 찰랑임
    water = (lp_fast(rs.randn(N), 18) - lp_fast(rs.randn(N), 90)) * 2.2
    water *= 0.7 + 0.3 * np.abs(np.sin(2 * np.pi * tt * .6 + np.sin(tt * 1.7)))
    # 멀리 차 소리: 낮은 웅웅거림 + 가끔 지나가는 차
    traffic = lp_fast(rs.randn(N), 400) * 14
    for t0 in [1.2, 4.1, 6.8, 9.9, 12.6]:
        d = 3.0; i0, i1 = int(t0 * SR), min(N, int((t0 + d) * SR))
        seg = lp_fast(rs.randn(i1 - i0), 60) * np.sin(np.linspace(0, np.pi, i1 - i0)) ** 2 * 4
        traffic[i0:i1] += seg
    # 발소리: 보도블록 위 운동화 (짧은 저역 톡 + 사각)
    steps = np.zeros(N)
    for k in range(int(DURATION * STEPS_PER_SEC)):
        t0 = (k + .5) / STEPS_PER_SEC + rs.uniform(-.015, .015); i0 = int(t0 * SR)
        d = int(.09 * SR); e = np.exp(-np.arange(d) / SR * 55)
        thump = np.sin(2 * np.pi * (90 + 40 * np.exp(-np.arange(d) / SR * 60)) * np.arange(d) / SR) * e
        scuff = lp_fast(rs.randn(d), 4) * np.exp(-np.arange(d) / SR * 35) * .5
        g = .8 + rs.uniform(-.15, .15) * (1 if k % 2 else .8)
        steps[i0:i0 + d] += (thump + scuff)[:max(0, min(d, N - i0))] * g
    norm = lambda x: x / (np.abs(x).max() + 1e-9)
    mix = norm(wind) * .35 + norm(water) * .22 + norm(traffic) * .2 + norm(steps) * .28
    mix *= np.minimum(1, tt / 1.0) * np.clip((DURATION - tt) / 1.0, 0, 1)
    L = mix + norm(lp_fast(rs.randn(N), 200)) * .03; Rch = mix + norm(lp_fast(rs.randn(N), 200)) * .03
    stereo = np.stack([L, np.roll(Rch, int(.008 * SR))], 1)
    stereo = np.tanh(stereo * 1.4) / np.tanh(1.4) * .9
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    sf.write(OUT, stereo, SR, subtype='PCM_16')
    print('완료:', os.path.normpath(OUT))

if __name__ == '__main__':
    main()
