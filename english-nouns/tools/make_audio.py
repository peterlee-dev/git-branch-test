"""Nouns: One and More Than One — 내레이션·효과음·배경음 만들기

교재: 재능 미주영어 D01 (Nouns · singular/plural · regular/irregular plurals)
- 내레이션: Supertonic 3 (sherpa-onnx, 온디바이스 소형 TTS, 영어)
- 줄마다 음성을 만든 뒤 실제 길이로 시각을 정해 ../timeline.js 를 씀 → 화면(index.html)이 그 시각을 따라 움직임
- 효과음·배경음은 numpy 로 합성 (외부 음원 없음)

  pip install sherpa-onnx soundfile numpy
  TTS_MODEL_DIR=/path/to/sherpa-onnx-supertonic-3-tts-int8-2026-05-11 python3 tools/make_audio.py
"""
import os, sys, json
import numpy as np
import soundfile as sf

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
VOICE_SID, SPEED, PAIR_SPEED = 1, 0.9, 0.72   # 낱말 짝(Dog, dogs.)은 더 천천히
GAP, SCENE_GAP = 0.45, 1.1          # 줄 사이, 장면 사이 쉼(초)

SCENES = [
    ('intro', 'Intro'),
    ('noun', 'What is a noun?'),
    ('sp', 'One and more than one'),
    ('r1', 'Rule 1 · add -s'),
    ('r2', 'Rule 2 · add -es'),
    ('r3', 'Rule 3 · y → ies'),
    ('r4', 'Rule 4 · f → ves'),
    ('irr', 'Irregular plurals'),
    ('same', 'Same for one and many'),
    ('quiz', 'Quiz time'),
    ('end', 'Great job'),
]
# (id, 장면, 말할 문장, 화면 자막(없으면 말과 같음), 뒤에 더 쉴 시간)
# 글자 이름은 대문자를 띄어 써서 TTS 가 한 글자씩 읽게 함 (자막은 -es 처럼 보여 줌)
SCRIPT = [
    ('i1', 'intro', "Hi, friends! Let's learn about nouns.", None, 0),
    ('i2', 'intro', "Today we will learn how to talk about one thing, and more than one.", None, 0.3),

    ('n1', 'noun', "A noun names a person, a place, or a thing.", None, 0.2),
    ('n2', 'noun', "A teacher is a person.", None, 0),
    ('n3', 'noun', "A school is a place.", None, 0),
    ('n4', 'noun', "A desk is a thing.", None, 1.2),
    ('n5', 'noun', "Let's find the nouns in this sentence.", None, 0),
    ('n6', 'noun', "The green truck drove to the gas station.", None, 0.5),
    ('n7', 'noun', "Truck and gas station are nouns!", None, 0.3),

    ('s1', 'sp', "A noun that names one is a singular noun.", None, 0.2),
    ('s2', 'sp', "A noun that names more than one is a plural noun.", None, 0.3),

    ('a0', 'r1', "Rule one. To make most nouns plural, just add S.", "Rule 1. To make most nouns plural, just add -s.", 0.2),
    ('a1', 'r1', "Dog, dogs.", None, 0.1),
    ('a2', 'r1', "Playground, playgrounds.", None, 0.1),
    ('a3', 'r1', "Baseball, baseballs.", None, 0.3),

    ('b0', 'r2', "Rule two. If a noun ends in C H, S, X, or S H, add E S.", "Rule 2. If a noun ends in -ch, -s, -x, or -sh, add -es.", 0.2),
    ('b1', 'r2', "Church, churches.", None, 0.1),
    ('b2', 'r2', "Bus, buses.", None, 0.1),
    ('b3', 'r2', "Fox, foxes.", None, 0.1),
    ('b4', 'r2', "Dish, dishes.", None, 0.3),

    ('c0', 'r3', "Rule three. If a noun ends in Y, change the Y to I, and add E S.", "Rule 3. If a noun ends in -y, change the -y to -i and add -es.", 0.2),
    ('c1', 'r3', "Baby, babies.", None, 0.1),
    ('c2', 'r3', "Bunny, bunnies.", None, 0.1),
    ('c3', 'r3', "City, cities.", None, 0.3),
    ('c4', 'r3', "But some words just add S.", "But some words just add -s.", 0.1),
    ('c5', 'r3', "Boy, boys.", None, 0.1),
    ('c6', 'r3', "Toy, toys.", None, 0.3),

    ('d0', 'r4', "Rule four. For most nouns that end in F or F E, change the F to V, and add E S.", "Rule 4. For most nouns that end in -f or -fe, change the -f to -v and add -es.", 0.2),
    ('d1', 'r4', "Leaf, leaves.", None, 0.1),
    ('d2', 'r4', "Knife, knives.", None, 0.1),
    ('d3', 'r4', "Wolf, wolves.", None, 0.3),

    ('e0', 'irr', "Some nouns change their spelling when they mean more than one.", None, 0.2),
    ('e1', 'irr', "One mouse ate the cheese. But three mice ate the cheese!", None, 0.3),
    ('e2', 'irr', "Man, men.", None, 0.1),
    ('e3', 'irr', "Woman, women.", None, 0.1),
    ('e4', 'irr', "Child, children.", None, 0.1),
    ('e5', 'irr', "Tooth, teeth.", None, 0.1),
    ('e6', 'irr', "Foot, feet.", None, 0.1),
    ('e7', 'irr', "Person, people.", None, 0.3),

    ('f0', 'same', "And some nouns stay the same for one, or more than one.", None, 0.2),
    ('f1', 'same', "One fish, many fish.", None, 0.1),
    ('f2', 'same', "One deer, two deer.", None, 0.1),
    ('f3', 'same', "One moose, four moose.", None, 0.1),
    ('f4', 'same', "One sheep, ten sheep.", None, 0.3),

    ('q0', 'quiz', "Quiz time! Say the plural out loud.", None, 0.2),
    ('q1', 'quiz', "Puppy.", None, 3.0),
    ('q2', 'quiz', "Puppies!", None, 0.5),
    ('q3', 'quiz', "Box.", None, 3.0),
    ('q4', 'quiz', "Boxes!", None, 0.5),
    ('q5', 'quiz', "Foot.", None, 3.0),
    ('q6', 'quiz', "Feet!", None, 0.5),

    ('z1', 'end', "Great job! Now you can make plural nouns.", None, 0.2),
    ('z2', 'end', "Keep reading, and look for nouns all around you!", None, 1.5),
]
PAIR_IDS = {'a1', 'a2', 'a3', 'b1', 'b2', 'b3', 'b4', 'c1', 'c2', 'c3', 'c5', 'c6', 'd1', 'd2', 'd3', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'f1', 'f2', 'f3', 'f4'}

# ---------------------------------------------------------------- TTS
def load_tts():
    import sherpa_onnx as s
    d = os.environ.get('TTS_MODEL_DIR')
    if not d or not os.path.isdir(d):
        sys.exit('TTS_MODEL_DIR 에 Supertonic 3 모델 폴더를 지정하세요.')
    j = lambda f: os.path.join(d, f)
    tts = s.OfflineTts(s.OfflineTtsConfig(model=s.OfflineTtsModelConfig(
        supertonic=s.OfflineTtsSupertonicModelConfig(
            duration_predictor=j('duration_predictor.int8.onnx'), text_encoder=j('text_encoder.int8.onnx'),
            vector_estimator=j('vector_estimator.int8.onnx'), vocoder=j('vocoder.int8.onnx'),
            tts_json=j('tts.json'), unicode_indexer=j('unicode_indexer.bin'), voice_style=j('voice.bin')),
        num_threads=4)))
    def say(text, speed=SPEED):
        g = s.GenerationConfig()
        g.sid, g.speed, g.num_steps, g.extra = VOICE_SID, speed, 8, {'lang': 'en'}
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
    a, b = max(0, idx[0] - int(.02 * SR)), min(len(x), idx[-1] + int(.08 * SR))
    return x[a:b]

def second_word_at(x):
    """'Dog, dogs.' 처럼 두 낱말 사이 쉼을 찾아 둘째 낱말이 시작하는 시각(초)"""
    win = int(.02 * SR); e = np.sqrt(np.convolve(x ** 2, np.ones(win) / win, 'same'))
    quiet = e < max(1e-4, e.max() * .06)
    best, run, start = None, 0, 0
    lo, hi = int(len(x) * .2), int(len(x) * .8)
    for i in range(lo, hi):
        if quiet[i]:
            if run == 0: start = i
            run += 1
        else:
            if run > (best[1] if best else int(.06 * SR)): best = (start, run)
            run = 0
    if not best: return len(x) / SR * .5
    return (best[0] + best[1]) / SR

# ---------------------------------------------------------------- 효과음
t_ = lambda d: np.arange(int(d * SR)) / SR
def sweep(f0, f1, d): f = np.geomspace(f0, f1, int(d * SR)); return np.sin(2 * np.pi * np.cumsum(f) / SR)
def pop(f=620): d = .11; return sweep(f * 1.7, f, d) * np.exp(-t_(d) * 36) * .8
def sparkle():
    out = np.zeros(int(.6 * SR))
    for k, f in enumerate([1568, 2093, 2637, 3136]):
        o = int(k * .055 * SR); tt = t_(.4)
        out[o:o + len(tt)] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 9) * .22
    return out
def whoosh(d=.55):
    rs = np.random.RandomState(4); n = rs.randn(int(d * SR)); y = np.zeros_like(n); acc = 0
    for i in range(len(n)):
        a = .02 + .25 * np.sin(np.pi * i / len(n)) ** 2; acc += a * (n[i] - acc); y[i] = acc
    return y * np.sin(np.pi * np.linspace(0, 1, len(y))) * .5
def ding(): tt = t_(1.2); return sum(a * np.sin(2 * np.pi * 1046.5 * m * tt) * np.exp(-tt * k) for m, a, k in [(1, .5, 3), (2.01, .2, 5), (3, .1, 7)])
def tick(): tt = t_(.05); return np.sin(2 * np.pi * 1800 * tt) * np.exp(-tt * 90) * .35
def chime_up():
    out = np.zeros(int(1.6 * SR))
    for k, f in enumerate([523.25, 659.25, 783.99, 1046.5]):
        o = int(k * .12 * SR); tt = t_(1.0); out[o:o + len(tt)] += (np.sin(2 * np.pi * f * tt) + .3 * np.sin(4 * np.pi * f * tt)) * np.exp(-tt * 3.5) * .22
    return out

# ---------------------------------------------------------------- 배경음: 잔잔한 우쿨렐레 느낌 (카플러스-스트롱)
def pluck(f, d=1.2, bright=.5):
    n = int(d * SR); p = max(2, int(SR / f)); rs = np.random.RandomState(int(f))
    buf = rs.uniform(-1, 1, p) * bright; out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]; buf[i % p] = .996 * .5 * (buf[i % p] + buf[(i + 1) % p])
    return out * np.exp(-t_(d) * 1.2)
def bgm(dur):
    bpm = 96; beat = 60 / bpm
    chords = [[261.63, 329.63, 392.0], [196.0, 246.94, 293.66], [220.0, 261.63, 329.63], [174.61, 220.0, 261.63]]   # C G Am F
    out = np.zeros(int(dur * SR) + SR * 2); cache = {}
    t, k = 0.0, 0
    while t < dur:
        ch = chords[(k // 8) % 4]; f = [ch[0], ch[1], ch[2], ch[1]][k % 4] * (2 if k % 8 >= 4 else 1)
        if f not in cache: cache[f] = pluck(f)
        x = cache[f]; o = int(t * SR); out[o:o + len(x)] += x[:len(out) - o] * (.5 if k % 2 else .7)
        if k % 8 == 0:   # 낮은 음
            b = ch[0] / 2; key = ('b', b)
            if key not in cache: cache[key] = np.sin(2 * np.pi * b * t_(beat * 7.5)) * np.exp(-t_(beat * 7.5) * .5) * .6
            y = cache[key]; out[o:o + len(y)] += y[:len(out) - o]
        t += beat / 2; k += 1
    return out[:int(dur * SR)]

def place(buf, t, x, g=1.0):
    o = int(t * SR)
    if o >= len(buf): return
    n = min(len(x), len(buf) - o); buf[o:o + n] += x[:n] * g

def main():
    say = load_tts()
    voice, t, prev_scene, lines, order = {}, 1.2, None, {}, []
    scene_t = {}
    for lid, sc, speak, shown, extra in SCRIPT:
        if prev_scene and sc != prev_scene: t += SCENE_GAP
        if sc not in scene_t: scene_t[sc] = t
        print(f'  {lid}: {speak}'); x = say(speak, PAIR_SPEED if lid in PAIR_IDS else SPEED); voice[lid] = (t, x)
        d = len(x) / SR
        L = {'text': shown or speak, 'start': round(t, 3), 'end': round(t + d, 3), 'scene': sc}
        if lid in PAIR_IDS: L['m'] = round(t + second_word_at(x), 3)   # 둘째 낱말(복수형)을 말하는 시각
        lines[lid] = L; order.append(lid)
        t += d + GAP + extra + (.55 if lid in PAIR_IDS else 0); prev_scene = sc   # 짝 뒤에는 따라 말할 틈
    dur = round(t + .5, 2)
    ids = [s for s, _ in SCENES]
    scenes = [{'id': s, 'label': lab, 'start': round(scene_t[s] - (0 if i == 0 else SCENE_GAP * .5), 3), 'end': round((scene_t[ids[i + 1]] - SCENE_GAP * .5) if i + 1 < len(ids) else dur, 3)} for i, (s, lab) in enumerate(SCENES)]
    scenes[0]['start'] = 0
    TL = {'duration': dur, 'scenes': scenes, 'lines': lines, 'order': order}
    with open(os.path.join(ROOT, 'timeline.js'), 'w', encoding='utf-8') as f:
        f.write('// make_audio.py 가 만든 시각표 (내레이션 실제 길이 기준). 손으로 고치지 말고 make_audio.py 를 다시 실행하세요\n')
        f.write('window.TL = ' + json.dumps(TL, ensure_ascii=False, indent=1) + ';\n')

    N = int(dur * SR); nar = np.zeros(N); fx = np.zeros(N)
    for lid, (st, x) in voice.items(): place(nar, st, x)
    for s in scenes[1:]: place(fx, s['start'] + .1, whoosh(), .5)
    for lid, L in lines.items():
        if 'm' in L:
            place(fx, L['start'] - .05, pop(), .35)
            if L['scene'] != 'same': place(fx, L['m'] + .05, sparkle(), .55)
            else: place(fx, L['m'] + .05, pop(880), .35)
    for q, a in [('q1', 'q2'), ('q3', 'q4'), ('q5', 'q6')]:
        for k in range(3): place(fx, lines[q]['end'] + .4 + k * .9, tick())
        place(fx, lines[a]['start'] - .05, ding(), .5)
    place(fx, lines['n7']['start'], sparkle(), .5)
    place(fx, lines['z1']['start'] - .1, chime_up(), .7)
    music = bgm(dur)
    env = np.convolve(np.abs(nar), np.ones(int(.25 * SR)) / int(.25 * SR), 'same')   # 말할 때 배경음을 살짝 낮춤
    duck = 1 - .45 * np.clip(env / (env.max() * .25 + 1e-9), 0, 1)
    mix = nar * 1.0 + fx * .8 + music * .085 * duck
    mix = np.tanh(mix * .9) / .9
    mix = mix / (np.abs(mix).max() + 1e-9) * .89
    out = os.path.join(ROOT, 'audio', 'mix.wav'); os.makedirs(os.path.dirname(out), exist_ok=True)
    sf.write(out, np.stack([mix, mix], 1).astype(np.float32), SR, subtype='PCM_16')
    print(f'완료: {out} ({dur}초, 줄 {len(order)}개)')

if __name__ == '__main__':
    main()
