"""피타고라스 정리 영상용 내레이션(TTS) + 효과음 믹스 생성.

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
DURATION = 124.0
VOICE_SID = 1          # Supertonic 3 음성 (0~4 여성, 5~9 남성)
PAUSE = 0.6            # 문장 뒤 쉬는 시간(초)
BASE_SPEED = 0.9        # 중학생용: 약간 천천히
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'audio', 'mix.wav')

# (시작, 끝[이 안에 끝나야 함], 읽을 문장, 화면 자막) — 읽을 문장은 발음대로 한글로 적음
# 자막이 None 이면 읽을 문장을 그대로 자막으로 씀
NARRATION = [
    (0.8, 5.8, '피타고라스 정리! 직각삼각형의 세 변 사이에 숨어 있는 규칙을 알아볼까요?', None),
    (7.2, 10.5, '여기 직각삼각형이 있어요.', None),
    (10.8, 14.5, '직각을 끼고 있는 두 변을 에이, 비라고 하고,', '직각을 끼고 있는 두 변을 a, b라고 하고,'),
    (14.8, 19.5, '직각과 마주 보는 가장 긴 변을 빗변 씨라고 해요.', '직각과 마주 보는 가장 긴 변을 빗변 c라고 해요.'),
    (20.5, 24.0, '각 변을 한 변으로 하는 정사각형을 그려 볼까요?', None),
    (24.2, 29.5, '정사각형의 넓이는 각각 에이 제곱, 비 제곱, 씨 제곱이에요.', '정사각형의 넓이는 각각 a², b², c²이에요.'),
    (29.8, 37.5, '이 세 넓이 사이에는 놀라운 관계가 있어요. 직접 세어 볼까요?', None),
    (38.4, 42.0, '에이가 삼, 비가 사, 씨가 오인 직각삼각형이에요.', 'a = 3, b = 4, c = 5인 직각삼각형이에요.'),
    (42.2, 45.5, '에이 제곱 정사각형은 작은 칸이 아홉 개,', 'a² 정사각형은 작은 칸이 9개,'),
    (45.7, 49.2, '비 제곱은 열여섯 개,', 'b²은 16개,'),
    (49.4, 53.0, '씨 제곱은 스물다섯 개예요.', 'c²은 25개예요.'),
    (53.2, 56.5, '구 더하기 십육은 이십오! 딱 맞아요.', '9 + 16 = 25, 딱 맞아요!'),
    (56.8, 60.0, '삼의 제곱 더하기 사의 제곱은 오의 제곱과 같아요.', '3² + 4² = 5²'),
    (60.8, 64.0, '정말 모든 직각삼각형에서 그럴까요? 함께 확인해 봐요.', None),
    (64.2, 67.5, '한 변의 길이가 에이 더하기 비인 정사각형을 그리고,', '한 변의 길이가 a + b인 정사각형을 그리고,'),
    (67.7, 71.0, '똑같은 직각삼각형 네 개를 넣어요.', '똑같은 직각삼각형 4개를 넣어요.'),
    (71.2, 74.5, '가운데 남은 부분은 한 변이 씨인 정사각형, 넓이는 씨 제곱이에요.', '가운데 남은 부분은 넓이가 c²인 정사각형이에요.'),
    (74.7, 79.5, '이번엔 삼각형을 옮겨 볼게요. 남은 부분은 에이 제곱과 비 제곱!', '삼각형을 옮기면 남은 부분은 a²과 b²!'),
    (79.8, 84.0, '두 그림 모두 큰 정사각형에서 삼각형 네 개를 뺀 넓이라서 서로 같아요.', '두 그림 모두 (큰 정사각형 − 삼각형 4개)라서 넓이가 같아요.'),
    (84.8, 89.0, '그래서 에이 제곱 더하기 비 제곱은 씨 제곱!', '그래서 a² + b² = c²!'),
    (89.2, 95.5, '직각삼각형에서 직각을 낀 두 변의 제곱의 합은 빗변의 제곱과 같아요. 이것을 피타고라스 정리라고 해요.', '두 변의 제곱의 합 = 빗변의 제곱, 이것이 피타고라스 정리예요.'),
    (96.5, 100.0, '문제를 풀어 볼까요? 빗변의 길이는 얼마일까요?', None),
    (100.2, 103.5, '피타고라스 정리로, 씨 제곱은 육의 제곱 더하기 팔의 제곱.', 'c² = 6² + 8²'),
    (103.7, 106.5, '삼십육 더하기 육십사는,', '= 36 + 64'),
    (106.7, 109.0, '백이에요.', '= 100'),
    (109.2, 115.5, '제곱해서 백이 되는 양수는 십! 그래서 빗변의 길이는 십이에요.', '제곱해서 100이 되는 양수는 10, 빗변의 길이는 10이에요!'),
    (116.8, 122.5, '직각삼각형의 빗변을 구할 때는 피타고라스 정리를 떠올려 보세요!', None),
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

# (시각, 소리, 볼륨)
def sfx_events():
    ev = []
    add = lambda t, s, v=1.0: ev.append((t, s, v))
    # 타이틀
    add(.3, sfx_whoosh(.5), .7); add(.8, sfx_ding(784), .7); add(1.6, sfx_pop(620)); add(2.2, sfx_soft_chime(990), .6)
    # 장면 전환
    for T in [6.05, 60.05, 84.05, 95.55, 115.55]: add(T, sfx_whoosh(), .9)
    # 개념 1: 삼각형 그리기
    add(7.0, sfx_whoosh(.9), .35); add(8.5, sfx_tick(1600), .8)
    add(10.8, sfx_pop(560)); add(11.6, sfx_pop(640)); add(14.8, sfx_pop(760)); add(15.3, sfx_soft_chime(880), .6)
    # 개념 2: 정사각형 세우기
    for i, s in enumerate([24.2, 25.8, 27.4]):
        add(s, sfx_whoosh(.6), .4); add(s + .8, sfx_pop(560 + i * 120))
    # 개념 3: 칸 세기
    for s, n in [(42.2, 9), (45.7, 16), (49.4, 25)]:
        for i in range(n): add(s + i * 1.4 / n, sfx_tick(1100 + i * 30), .35)
        add(s + 1.6, sfx_ding(880 if n == 9 else 988 if n == 16 else 1046.5), .8)
    for i in range(5): add(53.3 + i * .35, sfx_pop(600 + i * 60), .7)
    add(55.2, sfx_sparkle(), .7)
    add(56.9, sfx_pop(700)); add(57.4, sfx_soft_chime(990), .6)
    # 개념 4: 증명
    add(64.2, sfx_whoosh(.8), .4)
    for i in range(4): add(67.7 + i * .4, sfx_pop(520 + i * 70), .9)
    add(71.2, sfx_ding(784), .8)
    add(74.7, sfx_whoosh(.9), .5)
    for i in range(3): add(76.0 + i * .8, sfx_whoosh(.6), .45); add(76.6 + i * .8, sfx_tick(1500), .7)
    add(78.4, sfx_pop(620)); add(78.8, sfx_pop(720)); add(79.8, sfx_ding(988), .8); add(80.3, sfx_sparkle(), .6)
    # 개념 5: 공식
    for i in range(5): add(85.0 + i * .18, sfx_pop(600 + i * 70), .7)
    add(86.2, sfx_sparkle(), .8); add(89.2, sfx_ding(1046.5), .8)
    # 예제
    add(96.3, sfx_whoosh(.9), .35); add(98.2, sfx_pop(760))
    for i, s in enumerate([100.2, 103.7, 106.7]): add(s, sfx_pop(560 + i * 90))
    add(109.2, sfx_ding(1046.5), .9); add(109.6, sfx_sparkle(), .8)
    # 마무리
    add(116.3, sfx_pop(620)); add(116.8, sfx_ding(880), .7); add(118.0, sfx_sparkle(), .8)
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
