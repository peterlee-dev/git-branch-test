"""재능그룹 홍보 영상 사운드트랙: 배경음 CELEBRATION(audio/celebration.mp3, 사내용)을 처음부터 + 큰 순간에만 작은 효과음 (합성)
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
    import json, subprocess, imageio_ffmpeg
    here = os.path.dirname(os.path.abspath(__file__))
    song_js = open(os.path.join(here, '..', 'song.js'), encoding='utf-8').read()
    info = json.loads(song_js[song_js.index('{'):song_js.rindex('}') + 1])
    dur = 48 * info['beat'] / .5                                       # 영상 길이 (격자 48초 → 실제 초)
    raw = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-ss', str(info['start']), '-t', str(dur), '-i', os.path.join(here, '..', info['file']),
                          '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    song = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)
    N = len(song); fx = np.zeros(N)
    # 효과음은 곡을 해치지 않게 작게: 전환 슉, 계열사 등장 톡, 지식맵 반짝 (음높이 있는 소리는 거의 쓰지 않음)
    for e in json.load(open(os.path.join(here, 'events.json'))):
        t, k, i = e['t'], e['type'], e['info']
        if k == 'wipe': place(fx, t - .05, sfx_whoosh(.5), .7)
        elif k == 'card': place(fx, t, sfx_tick(1300 + (int(i) % 5) * 120), .45)
        elif k == 'tick': place(fx, t, sfx_tick(1600 + (int(i) % 7) * 80), .25)
        elif k == 'node': place(fx, t, sfx_tick(1800 + (int(i) % 8) * 60), .16)
        elif k == 'spark': place(fx, t, sfx_tick(2400 + (int(i) % 5) * 150), .07)
    G = lambda g: g * info['beat'] / .5
    place(fx, G(34.1), sfx_sparkle(), .35)                               # 드롭에서 지식맵이 켜짐
    place(fx, G(40.25), sfx_sparkle(), .35)                              # 엔딩
    fx = fx / (np.abs(fx).max() + 1e-9) * .25
    mix = song * .92 + fx[:, None]
    tt = np.arange(N) / SR
    mix *= (np.minimum(1, tt / .1) * np.clip((tt[-1] - tt) / 2.2, 0, 1))[:, None]   # 끝 2.2초 페이드아웃
    mix = np.tanh(mix * 1.05) / np.tanh(1.05)
    out = os.path.join(here, '..', 'audio', 'mix.wav'); os.makedirs(os.path.dirname(out), exist_ok=True)
    sf.write(out, mix.astype(np.float32), SR, subtype='PCM_16')
    print(f'완료: {os.path.normpath(out)} ({dur:.2f}초, 곡 {info["start"]}초부터)')

if __name__ == '__main__':
    main()
