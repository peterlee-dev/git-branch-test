"""Adaptive Diagnostic Assessment — narration, sound effects and background music

- Voice: Qwen3-TTS (Alibaba Qwen, Apache 2.0) Base model clones the reference voice in audio/voice_ref.wav
  (the sample the team provided) and reads every line of the script in English.
- Each line's real length decides the timing → writes ../timeline.js (subtitle chunks included), which index.html follows.
- UI sound effects and a soft background pad are synthesised with numpy.

  pip install torch qwen-tts soundfile numpy
  QWEN_BASE_DIR=/path/Qwen3-TTS-12Hz-1.7B-Base python3 tools/make_audio.py
  (generated lines are cached in audio/tts_cache/, so editing one line only regenerates that line)
"""
import os, sys, json, hashlib, re
import numpy as np
import soundfile as sf

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
CACHE = os.path.join(ROOT, 'audio', 'tts_cache')
REF = os.path.join(ROOT, 'audio', 'voice_ref.wav')
REF_TEXT = 'Great job! Now click the next button at the bottom right to continue.'   # what the reference sample says
GAP, SCENE_GAP = .45, 1.0

SCENES = [('intro', 'Title'), ('what', 'What is a diagnostic assessment?'), ('problem', 'Problems'), ('adaptive', 'Adaptive diagnostic assessment'),
          ('necessary', 'Only the necessary questions'), ('benefit', 'Benefits'), ('how', 'How it works'), ('path', 'Algorithm example'),
          ('validate', 'Validation step'), ('quick', 'Quick Diagnosis'), ('effects', 'Expected effects'), ('outro', 'Thank you')]
# (id, scene, subtitle text, text read aloud (None = same), extra pause after)
SCRIPT = [
    ('l1', 'intro', "Hello. Today, I'd like to introduce the development direction and expected benefits of the online Adaptive Diagnostic Assessment for Self-Learning JEI Math.",
     "Hello. Today, I'd like to introduce the development direction and expected benefits of the online Adaptive Diagnostic Assessment for Self-Learning J.E.I. Math.", .6),
    ('l2', 'what', 'First, let me explain the challenges with our current diagnostic assessment.', None, .2),
    ('l3', 'what', "A diagnostic assessment is designed to identify a learner's current level before the learner begins studying and to prescribe a personalized learning program.", None, .4),
    ('l4', 'problem', 'Currently, accurate diagnosis requires every learner to answer the same set of questions.', None, .2),
    ('l5', 'problem', 'While using a large number of questions can help improve diagnostic accuracy, it also places a significant burden on learners.', None, .2),
    ('l6', 'problem', "As a result, the process can become less efficient when it comes to identifying each learner's true starting point for learning.", None, .4),
    ('l7', 'adaptive', 'To address this issue, we are developing an Adaptive Diagnostic Assessment.', None, .2),
    ('l8', 'adaptive', 'It is a responsive, high-precision diagnostic system in which the next question is adjusted in real time based on whether the learner answers each question correctly or incorrectly within each learning objective.', None, .4),
    ('l9', 'necessary', 'The key is not to have learners answer every question, but to present only the questions that are necessary based on their responses.', None, .4),
    ('l10', 'benefit', 'This approach improves both diagnostic efficiency and reliability, while also reducing the time required for the assessment.', None, .2),
    ('l11', 'benefit', "In short, it is an assessment system designed to reduce the burden of diagnosis while maintaining its core purpose: accurately identifying the learner's starting point for learning.", None, .4),
    ('l12', 'how', 'So, how does the Adaptive Diagnostic Assessment actually work?', None, .3),
    ('l13', 'how', 'When a question is presented, a correct answer leads to a higher-level question, while an incorrect answer leads to a lower-level question designed to identify any missing concepts.', None, .4),
    ('l14', 'path', "For example, instead of having a learner answer every question sequentially from No. 1 to No. 9, we first present a representative core question.",
     "For example, instead of having a learner answer every question sequentially from number one to number nine, we first present a representative core question.", .2),
    ('l15', 'path', 'If the learner answers incorrectly, the system moves down to lower-level concepts, such as No. 3 and then No. 1, to identify where the learning gap begins.',
     'If the learner answers incorrectly, the system moves down to lower-level concepts, such as number three and then number one, to identify where the learning gap begins.', .3),
    ('l16', 'path', "On the other hand, if the learner answers correctly, the system moves up to No. 7 and then No. 9 to determine how far the learner's understanding extends.",
     "On the other hand, if the learner answers correctly, the system moves up to number seven and then number nine to determine how far the learner's understanding extends.", .3),
    ('l17', 'path', "In this way, we can minimize the number of questions while accurately pinpointing the learner's actual ability level.", None, .4),
    ('l18', 'validate', 'However, to maintain reliability even with fewer questions, the system also includes a validation step.', None, .2),
    ('l19', 'validate', 'For each Representative Learning Objective, which represents the core learning goal, we prepare two additional similar questions for thorough evaluation.', None, .3),
    ('l20', 'validate', 'Answering two out of three correctly results in an "Understood" status; otherwise, it is marked as "Not Understood."',
     'Answering two out of three correctly results in an Understood status. Otherwise, it is marked as Not Understood.', .3),
    ('l21', 'validate', 'It is a mechanism to reduce the number of questions while preserving the reliability of the result.', None, .4),
    ('l22', 'quick', "We also prepared a 'Quick Diagnosis' option so it can be used more quickly in the field.", 'We also prepared a Quick Diagnosis option so it can be used more quickly in the field.', .2),
    ('l23', 'quick', 'The Quick Diagnosis first diagnoses Numbers and Operations, a foundational area of mathematics, and then provides a quick report on Numbers and Operations.', None, .2),
    ('l24', 'quick', "Using this report, even before the full diagnosis is complete, you can discuss the learner's level of understanding in Numbers and Operations along with the direction for their next steps in learning.", None, .4),
    ('l25', 'effects', "Now, let's look at how the Adaptive Diagnostic Assessment can help in practice.", None, .2),
    ('l26', 'effects', 'First and foremost, it addresses one of the biggest pain points of the current diagnostic assessment: the excessive number of questions.', None, .2),
    ('l27', 'effects', 'With fewer questions, both learners and teachers can experience less burden during the diagnostic process.', None, .2),
    ('l28', 'effects', 'This is expected to improve the efficiency of consultations and classroom management as well.', None, .2),
    ('l29', 'effects', 'The Adaptive Diagnostic Assessment will first be applied to Self-Learning JEI Math, with the potential to expand the system to other subjects in the future.',
     'The Adaptive Diagnostic Assessment will first be applied to Self-Learning J.E.I. Math, with the potential to expand the system to other subjects in the future.', .5),
    ('l30', 'outro', 'This concludes our introduction to the Adaptive Diagnostic Assessment.', None, .3),
    ('l31', 'outro', 'Thank you.', None, 2.2),
]

# ---------------------------------------------------------------- TTS
def trim(x, thr=.008):
    idx = np.where(np.abs(x) > thr)[0]
    if len(idx) == 0: return x
    return x[max(0, idx[0] - int(.03 * SR)): min(len(x), idx[-1] + int(.12 * SR))]

def resample(x, sr):
    if sr == SR: return x.astype(np.float32)
    n = int(len(x) * SR / sr)
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)

def h(*a): return hashlib.sha1('|'.join(a).encode()).hexdigest()[:16]
REF_ID = h(open(REF, 'rb').read().hex()[:20000]) if os.path.exists(REF) else 'noref'
def line_path(tts): return os.path.join(CACHE, h(REF_ID, tts) + '.wav')

def make_voices():
    os.makedirs(CACHE, exist_ok=True)
    need = [(lid, tts or sub) for lid, _, sub, tts, _ in SCRIPT if not os.path.exists(line_path(tts or sub))]
    if not need: return
    if not os.path.exists(REF): sys.exit('audio/voice_ref.wav (the voice sample to clone) is missing.')
    import torch
    from qwen_tts import Qwen3TTSModel
    torch.set_num_threads(os.cpu_count() or 4)
    b = os.environ.get('QWEN_BASE_DIR') or sys.exit('Set QWEN_BASE_DIR to the Qwen3-TTS Base model folder.')
    m = Qwen3TTSModel.from_pretrained(b, device_map='cuda' if torch.cuda.is_available() else 'cpu', dtype=torch.bfloat16)
    prompt = m.create_voice_clone_prompt(ref_audio=REF, ref_text=REF_TEXT)
    for lid, tx in need:
        torch.manual_seed(11)
        w, sr = m.generate_voice_clone(text=tx, language='English', voice_clone_prompt=prompt)
        sf.write(line_path(tx), w[0], sr); print(f'  {lid}: {tx}', flush=True)

def load_line(tx):
    x, sr = sf.read(line_path(tx), dtype='float32')
    if x.ndim > 1: x = x.mean(1)
    return trim(resample(x, sr))

# Subtitle chunks: fill words up to ~74 characters, preferring to break right after a comma / colon / period
# once a chunk is long enough; timed in proportion to their length (good enough for reading along)
def chunks(text, maxc=74, soft=38):
    out, cur = [], []
    for w in text.split():
        if cur and len(' '.join(cur + [w])) > maxc: out.append(' '.join(cur)); cur = []
        cur.append(w)
        if len(' '.join(cur)) >= soft and w[-1] in ',;:.?!': out.append(' '.join(cur)); cur = []
    if cur:
        if out and len(' '.join(cur)) < 20 and len(out[-1]) + len(' '.join(cur)) < maxc + 12: out[-1] += ' ' + ' '.join(cur)
        else: out.append(' '.join(cur))
    return out

# ---------------------------------------------------------------- sound
t_ = lambda d: np.arange(int(d * SR)) / SR
rs = np.random.RandomState(5)
def lp(x, a):
    y = np.zeros_like(x); acc = 0.0
    for i in range(len(x)): acc += a * (x[i] - acc); y[i] = acc
    return y
def tone(f, d, g=.3, dec=6): tt = t_(d); return np.sin(2 * np.pi * f * tt) * np.exp(-tt * dec) * np.minimum(1, tt / .005) * g
def pop(): x = tone(880, .12, .25, 30); x[:int(.1 * SR)] += tone(1320, .1, .12, 40); return x
def ding(): x = tone(1046.5, .5, .25, 7); y = tone(1568, .42, .22, 7); o = int(.08 * SR); n = min(len(y), len(x) - o); x[o:o + n] += y[:n]; return x   # correct
def boop(): return tone(392, .25, .22, 10) + tone(370, .25, .1, 10)                              # incorrect (soft, not harsh)
def whoosh(d=.5):
    n = rs.randn(int(d * SR)); e = np.sin(np.pi * np.linspace(0, 1, len(n))) ** 2
    return lp(n, .08) * e * 1.2
def pad(dur):
    # soft background: slow major chords (Cmaj7 - Am7 - Fmaj7 - G6) with gentle swell, very quiet
    chords = [[261.63, 329.63, 392.0, 493.88], [220.0, 261.63, 329.63, 392.0], [174.61, 220.0, 261.63, 329.63], [196.0, 246.94, 293.66, 329.63]]
    seg = 4.0; out = np.zeros(int(dur * SR) + SR)
    for k in range(int(dur / seg) + 1):
        tt = t_(seg + 1.5); env = np.sin(np.pi * np.clip(tt / (seg + 1.5), 0, 1)) ** 1.5
        x = sum(np.sin(2 * np.pi * f * tt) + .3 * np.sin(2 * np.pi * f * 2 * tt) for f in chords[k % 4]) * env * .05
        o = int(k * seg * SR); n = min(len(x), len(out) - o)
        if n > 0: out[o:o + n] += x[:n]
    return out[:int(dur * SR)]

def place(buf, t, x, g=1.0):
    o = int(t * SR)
    if o >= len(buf) or o < 0: return
    n = min(len(x), len(buf) - o); buf[o:o + n] += x[:n] * g

def main():
    make_voices()
    t, prev, lines, order, scene_t, voice = 3.0, None, {}, [], {}, {}
    for lid, sc, sub, tts, extra in SCRIPT:
        if prev and sc != prev: t += SCENE_GAP
        if sc not in scene_t: scene_t[sc] = t - (.8 if prev else 3.0)
        x = load_line(tts or sub); d = len(x) / SR; voice[lid] = (t, x)
        cs = chunks(sub); tot = sum(len(c) for c in cs); acc = 0; cl = []
        for c in cs: cl.append({'text': c, 'start': round(t + d * acc / tot, 3)}); acc += len(c)
        lines[lid] = {'text': sub, 'start': round(t, 3), 'end': round(t + d, 3), 'scene': sc, 'chunks': cl}
        order.append(lid); t += d + GAP + extra; prev = sc
    dur = round(t + .3, 2)
    ids = [s for s, _ in SCENES]
    scenes = [{'id': s, 'label': lab, 'start': round(max(0, scene_t[s]), 3), 'end': round(scene_t[ids[i + 1]] if i + 1 < len(ids) else dur, 3)} for i, (s, lab) in enumerate(SCENES)]
    TL = {'duration': dur, 'scenes': scenes, 'lines': lines, 'order': order}
    with open(os.path.join(ROOT, 'timeline.js'), 'w', encoding='utf-8') as f:
        f.write('// written by tools/make_audio.py (timing from the real narration length). Do not edit by hand — rerun make_audio.py\n')
        f.write('window.TL = ' + json.dumps(TL, ensure_ascii=False) + ';\n')
    N = int(dur * SR); nar = np.zeros(N); fx = np.zeros(N)
    for lid, (st, x) in voice.items(): place(nar, st, x)
    L = lambda k: lines[k]; S = {s['id']: s for s in scenes}
    for s in scenes[1:]: place(fx, s['start'] - .15, whoosh(), .35)
    # 'path' scene: correct / incorrect cues follow the narration (see index.html for the same timings)
    l15, l16 = L('l15'), L('l16')
    for k, tt in enumerate(np.linspace(l15['start'] + .6, l15['end'] - .8, 3)): place(fx, tt, boop() if k < 2 else pop(), .7)
    for k, tt in enumerate(np.linspace(l16['start'] + 1.2, l16['end'] - .8, 3)): place(fx, tt, ding() if k < 2 else pop(), .7)
    place(fx, L('l20')['start'] + .8, ding(), .6); place(fx, L('l20')['start'] + 3.4, boop(), .6)
    place(fx, L('l31')['start'] - .3, ding(), .5)
    mus = pad(dur)
    envl = np.convolve(np.abs(nar), np.ones(int(.3 * SR)) / int(.3 * SR), 'same')
    duck = 1 - .5 * np.clip(envl / (envl.max() * .2 + 1e-9), 0, 1)
    mix = nar * 1.0 + fx * .5 + mus * duck * np.minimum(1, t_(dur)[:N] / 2) * np.clip((dur - t_(dur)[:N]) / 2.5, 0, 1)
    mix = np.tanh(mix * .95) / .95
    mix = mix / (np.abs(mix).max() + 1e-9) * .9
    out = os.path.join(ROOT, 'audio', 'mix.wav')
    sf.write(out, np.stack([mix, mix], 1).astype(np.float32), SR, subtype='PCM_16')
    print(f'done: {out} ({dur}s, {len(order)} lines)')

if __name__ == '__main__':
    main()
