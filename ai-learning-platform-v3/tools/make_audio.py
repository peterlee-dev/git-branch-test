"""JEI Math: An AI-Powered Personalized Learning Platform v3 — narration, timeline and mix (the revised, shorter script; 30 pages)

- Voice: Qwen3-TTS 1.7B Base (clone) on the DGX TTS API (POST /v1/tts/clone), following audio/voice_ref.wav
  (the 29 s reference from the D–I narration) and its words audio/voice_ref.txt
- Every line is read N times (default 3). Each take is transcribed with whisper large-v3-turbo (mlx-whisper);
  takes that do not read the script word for word are dropped, and of the rest the one closest to the median speaking
  rate without long pauses inside wins. Takes and transcripts are cached in audio/tts_cache/, so changing a line only
  re-reads that line (--redo l3_2,l6_4 reads those again)
- Lines are placed with GAP between lines and SCENE_GAP between pages. Writes ../timeline.js (with each line's
  spoken words and their times, so index.html can key pictures to words) and audio/mix.wav (narration + page-turn
  whoosh + a ding before the thank-you, no music)

  export FFMPEG=../math-di-improvement-v2/node_modules/ffmpeg-static/ffmpeg   # or any ffmpeg (also needed on PATH by whisper)
  uv run --with mlx-whisper python tools/make_audio.py
"""
import os, sys, json, re, hashlib, subprocess, difflib, urllib.request, uuid, wave
import numpy as np

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
AUD = os.path.join(ROOT, 'audio')
CACHE = os.path.join(AUD, 'tts_cache')
REF, REF_TXT = os.path.join(AUD, 'voice_ref.wav'), os.path.join(AUD, 'voice_ref.txt')
TTS = os.environ.get('TTS_URL', 'http://192.168.51.8:8095')
N_TAKES = int(os.environ.get('N', 3))
TAKES = {'l10_1': 8}   # lines that needed more takes before one read the script word for word
FFMPEG = os.environ.get('FFMPEG') or next((p for p in [os.path.join(ROOT, 'node_modules/ffmpeg-static/ffmpeg'), os.path.join(ROOT, '../math-di-improvement-v2/node_modules/ffmpeg-static/ffmpeg')] if os.path.exists(p)), 'ffmpeg')
LEAD, GAP, SCENE_GAP, TAIL = 2.6, .45, 1.0, 2.4

SCENES = [('title', 'Title'), ('vision', 'Our vision'),
          ('kmap', 'What is the Knowledge Map?'), ('kmapHow', 'How skills build on one another'),
          ('gather', 'Building the map: input'), ('analyze', 'Building the map: AI proposes, researchers review'), ('expand', 'Building the map: by country'),
          ('layerK', 'Knowledge layer'), ('layerA', 'AI Engine layer'), ('layerS', 'Service layer'),
          ('phases', 'Two phases, seven projects'), ('phase1', 'Phase 1'), ('phase2', 'Phase 2'), ('wiki', 'LLM Wiki'),
          ('pod', 'Personalized POD'), ('podCycle', 'The POD learning cycle'),
          ('behavior', 'How students learn'), ('loop', 'Adaptive learning path'), ('assistant', 'AI Learning Assistant'),
          ('statusMap', "A student's learning status"), ('statuses', 'Four learning statuses'), ('recommend', 'Next step'),
          ('ben1', 'Benefit 1'), ('ben2', 'Benefit 2'), ('ben3', 'Benefit 3'), ('ben4', 'Benefit 4'),
          ('roadmap', 'Roadmap: Phase 1'), ('roadmapPhases', 'Roadmap: Phase 2'), ('roadmapAll', 'Throughout development'),
          ('outro', 'Closing')]
CONT = {'statuses', 'recommend', 'roadmapPhases'}   # same sheet as the page before: only part of it changes, no page turn (index.html CONT)
# (id, page, line as written, line as read (None = as written), extra pause after it). Line ids: l<slide>_<n>
SCRIPT = [
    ('l1_1', 'title', "This project is about more than using AI to improve efficiency.", None, 0),
    ('l1_2', 'title', "It's about transforming JEI's learning products and services.", None, 0),
    ('l1_3', 'vision', "Over the past 50 years, JEI has developed deep expertise in learning design and built a rich collection of educational resources.", None, 0),
    ('l1_4', 'vision', "By turning that expertise into knowledge AI can use, we aim to connect printed workbooks, personalized print-on-demand materials, and online learning on one integrated platform.", None, 0),

    ('l2_1', 'kmap', "The foundation of this platform is the JEI-Math Knowledge Map.", "The foundation of this platform is the JEI Math Knowledge Map.", .2),
    ('l2_2', 'kmap', "Think of it as a network that connects math learning objectives and shows how skills build on one another.", None, 0),
    ('l2_3', 'kmapHow', "For example, students progress from single-digit addition to addition with sums up to eighteen, and then to two-digit addition with regrouping.", None, .2),
    ('l2_4', 'kmapHow', "Each objective also includes content and difficulty information, helping AI understand the overall structure of math learning.", None, 0),

    ('l3_1', 'gather', "We're building the JEI-Math Knowledge Map around JEI's educational philosophy, rather than the curriculum of any single country.",
     "We're building the JEI Math Knowledge Map around JEI's educational philosophy, rather than the curriculum of any single country.", .2),
    ('l3_2', 'gather', "AI compares JEI workbooks, research materials, and educational principles with learning standards from different countries.", None, 0),
    ('l3_3', 'analyze', "It then proposes learning objectives and how they connect.", None, .2),
    ('l3_4', 'analyze', "JEI researchers review these proposals for educational soundness, while new resources help the map evolve.", None, 0),
    ('l3_5', 'expand', "By aligning this shared map with national curricula, we can develop learning content for different markets more quickly and flexibly.", None, 0),

    ('l4_1', 'layerK', "The platform has three connected layers: Knowledge, AI Engine, and Service.", None, .2),
    ('l4_2', 'layerK', "The Knowledge Layer organizes learning objectives, workbooks, and educational expertise into a shared foundation.", None, 0),
    ('l4_3', 'layerA', "The AI Engine Layer uses that foundation to generate step-by-step, programmed learning materials, analyze learning progress, and provide hints and explanations.", None, 0),
    ('l4_4', 'layerS', "Finally, the Service Layer delivers these capabilities through workbooks, personalized print-on-demand materials, online learning, and teacher support tools.", None, .2),
    ('l4_5', 'layerS', "Students' results then feed back into the system to guide what they learn next.", None, 0),

    ('l5_1', 'phases', "Seven interconnected projects will move forward in two phases.", None, 0),
    ('l5_2', 'phase1', "Phase One focuses on the Knowledge Map, automated content generation, and personalized print-on-demand learning, linking assessment results to learning recommendations and follow-up practice.", None, 0),
    ('l5_3', 'phase2', "Phase Two expands into online learning through progress analysis, adaptive learning paths, and an AI Learning Assistant.", None, 0),
    ('l5_4', 'wiki', "We'll also build LLM Wiki, a shared knowledge base JEI staff can manage and update to support the entire effort.", None, 0),

    ('l6_1', 'pod', "The centerpiece of Phase One is personalized print-on-demand learning.", None, .2),
    ('l6_2', 'pod', "We analyze each student's assessment results and learning history to identify what they need to study and how much practice they need.", None, 0),
    ('l6_3', 'pod', "AI generates the materials, which JEI researchers review before delivery.", None, 0),
    ('l6_4', 'podCycle', "The student's results then shape the next round of learning.", None, .2),
    ('l6_5', 'podCycle', "We can also add targeted practice to existing workbooks.", None, 0),
    ('l6_6', 'behavior', "In Phase Two, we extend this approach online.", None, 0),
    ('l6_7', 'behavior', "Along with correct and incorrect answers, the system analyzes learning behaviors, including time spent on problems, hint usage, and repeated attempts.", None, 0),
    ('l6_8', 'loop', "It uses those insights to adjust each student's path through review, additional practice, or more advanced work.", None, 0),
    ('l6_9', 'assistant', "The AI Learning Assistant provides hints and explanations rather than simply giving answers, while teachers gain information to guide each student more effectively.", None, 0),

    ('l7_1', 'statusMap', "This screen illustrates a student's progress on the Knowledge Map.", None, .2),
    ('l7_2', 'statusMap', "The top shows concepts not yet studied.", None, 0),
    ('l7_3', 'statusMap', "The middle shows concepts being learned or needing further assessment, and the bottom shows concepts already studied.", None, 0),
    ('l7_4', 'statuses', "Each objective is classified as Mastered, Needs More Practice, Learning Gap, or Not Yet Studied.", None, 0),
    ('l7_5', 'recommend', "These statuses help AI identify what the student understands and recommend the next step.", None, .2),
    ('l7_6', 'recommend', "The classification criteria will be developed and validated using actual assessment and learning data.", None, 0),

    ('l8_1', 'ben1', "We expect four key benefits.", None, .2),
    ('l8_2', 'ben1', "First, we can develop content aligned with different national curricula more quickly.", None, 0),
    ('l8_3', 'ben2', "Second, assessment results and learning data can reveal each student's strengths and learning needs.", None, 0),
    ('l8_4', 'ben3', "Third, we can personalize learning objectives and the amount of practice across print-on-demand and online services.", None, 0),
    ('l8_5', 'ben4', "Finally, by considering academic achievement alongside the JEI Self-Learning Index, or JEI-SLI, we can gain a fuller picture of each student's growth over time.",
     "Finally, by considering academic achievement alongside the JEI Self-Learning Index, or J-E-I S-L-I, we can gain a fuller picture of each student's growth over time.", 0),

    ('l9_1', 'roadmap', "Phase One runs from the fourth quarter of 2026 through 2027.", "Phase One runs from the fourth quarter of twenty twenty-six through twenty twenty-seven.", .2),
    ('l9_2', 'roadmap', "We'll develop the Knowledge Map and content generation, pilot personalized print-on-demand learning in the United States, and then expand to Korea.", None, 0),
    ('l9_3', 'roadmapPhases', "Phase Two begins in 2028, combining progress analysis, adaptive learning paths, and the AI Learning Assistant into an online platform.",
     "Phase Two begins in twenty twenty-eight, combining progress analysis, adaptive learning paths, and the AI Learning Assistant into an online platform.", 0),
    ('l9_4', 'roadmapAll', "Throughout development, we'll improve the Knowledge Map and AI engines quarterly, supported by LLM Wiki as our shared knowledge base.", None, 0),

    ('l10_1', 'outro', "By combining 50 years of learning design expertise with AI, JEI aims to create a more personalized learning experience, one that meets the needs of every student.", None, .5),
    ('l10_2', 'outro', "Thank you.", None, 0),
]


def h(*a): return hashlib.sha1('|'.join(a).encode()).hexdigest()[:12]


def post(path, fields, files):
    b = uuid.uuid4().hex; body = b''
    for k, v in fields.items(): body += f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
    for k, (name, data) in files.items(): body += f'--{b}\r\nContent-Disposition: form-data; name="{k}"; filename="{name}"\r\nContent-Type: application/octet-stream\r\n\r\n'.encode() + data + b'\r\n'
    body += f'--{b}--\r\n'.encode()
    req = urllib.request.Request(TTS + path, data=body, headers={'Content-Type': f'multipart/form-data; boundary={b}'}, method='POST')
    with urllib.request.urlopen(req, timeout=300) as r: return r.read()


def decode(path):
    out = subprocess.run([FFMPEG, '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(out, np.float32).astype(np.float64)


# ---------------------------------------------------------------- words: script vs. what was read
ONES = 'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split()
TENS = 'twenty thirty forty fifty sixty seventy eighty ninety'.split()
def say(n):
    if n < 20: return ONES[n]
    if n < 100: return TENS[n // 10 - 2] + ('' if n % 10 == 0 else ONES[n % 10])
    if 2000 <= n < 2100: return 'twenty' + say(n - 2000) if n > 2009 else 'twothousand' + ('' if n == 2000 else say(n - 2000))
    if n < 1000: return ONES[n // 100] + 'hundred' + ('' if n % 100 == 0 else say(n % 100))
    return str(n)
def toks(text):
    """lower-case tokens without punctuation; numbers spelled out; hyphenated letters joined (P-O-D → pod)"""
    out = []
    for w in re.split(r'[\s—–]+', text.lower()):
        if re.fullmatch(r"([a-z]-)+[a-z][.,]?", w): w = w.replace('-', '')
        for p in re.split(r'-', w):
            p = re.sub(r"[^a-z0-9]", '', p.replace("'", ''))
            if not p: continue
            out.append(say(int(p)) if p.isdigit() else p)
    return out
def flat(text): return ''.join(toks(text))   # blind to spacing, hyphens and how numbers are written


def ref_id(): return h(open(REF, 'rb').read().hex()[:40000], open(REF_TXT).read().strip())
def take_path(lid, read, k): return os.path.join(CACHE, f'{lid}_{h(ref_id(), read)}_{k}.wav')


def make_takes(redo):
    os.makedirs(CACHE, exist_ok=True)
    ref, ref_text = open(REF, 'rb').read(), open(REF_TXT).read().strip()
    for lid, _, sub, read, _ in SCRIPT:
        for k in range(TAKES.get(lid, N_TAKES)):
            p = take_path(lid, read or sub, k)
            if os.path.exists(p) and lid not in redo: continue
            print(f'TTS {lid} #{k}', (read or sub)[:50], flush=True)
            open(p, 'wb').write(post('/v1/tts/clone', {'text': read or sub, 'ref_text': ref_text, 'language': 'English', 'format': 'wav'}, {'ref_audio': ('ref.wav', ref)}))
            j = p[:-4] + '.json'
            if os.path.exists(j): os.remove(j)


def transcribe(p):
    j = p[:-4] + '.json'
    if os.path.exists(j): return json.load(open(j))
    import mlx_whisper
    r = mlx_whisper.transcribe(p, path_or_hf_repo='mlx-community/whisper-large-v3-turbo', language='en', word_timestamps=True)
    words = [{'w': w['word'], 's': round(w['start'], 3), 'e': round(w['end'], 3)} for s in r['segments'] for w in s.get('words', [])]
    out = {'text': r['text'].strip(), 'words': words}
    json.dump(out, open(j, 'w'), ensure_ascii=False); return out


# ---------------------------------------------------------------- pick a take and trim it
def frames_db(x, hop=480):
    n = len(x) // hop
    return 20 * np.log10(np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)


def trim(x, db):
    """keep the voiced part (frames above -50 dB) with a little air: 0.06 s before, 0.18 s after"""
    v = np.where(db > -50)[0]
    a, b = max(0, v[0] * 480 - int(.06 * SR)), min(len(x), (v[-1] + 1) * 480 + int(.18 * SR))
    y = x[a:b].copy(); fi, fo = int(.01 * SR), int(.05 * SR)
    y[:fi] *= np.linspace(0, 1, fi); y[-fo:] *= np.linspace(1, 0, fo)
    return y, a / SR


def longest_pause(db):
    v = np.where(db > -45)[0]; best = run = 0
    for q in (db[v[0]:v[-1]] < -45):
        run = run + 1 if q else 0; best = max(best, run)
    return best * .01


def choose():
    cands = {}
    for lid, _, sub, read, _ in SCRIPT:
        want = flat(sub); cs = []
        for k in range(TAKES.get(lid, N_TAKES)):
            p = take_path(lid, read or sub, k); tr = transcribe(p)
            x = decode(p); db = frames_db(x); y, off = trim(x, db)
            got = flat(tr['text'])
            miss = 0 if got == want else sum(max(i2 - i1, j2 - j1) for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, want, got, autojunk=False).get_opcodes() if op != 'equal')
            cs.append({'k': k, 'p': p, 'tr': tr, 'y': y, 'off': off, 'miss': miss, 'rate': len(want) / (len(y) / SR), 'pause': longest_pause(db)})
        cands[lid] = cs
    med = float(np.median([c['rate'] for cs in cands.values() for c in cs if c['miss'] == 0] or [1]))
    pick, bad = {}, []
    for lid, cs in cands.items():
        for c in cs: c['score'] = c['miss'] * 10 + abs(c['rate'] - med) / med + max(0, c['pause'] - .7) * 4
        best = min(cs, key=lambda c: c['score']); pick[lid] = best
        if best['miss']: bad.append((lid, best['miss'], best['tr']['text']))
    print(f'median rate {med:.2f} chars/s')
    for lid, c in pick.items(): print(f"  {lid:6s} take {c['k']}  {len(c['y']) / SR:5.2f}s  miss {c['miss']}  pause {c['pause']:.2f}s  [{' '.join(str(x['miss']) for x in cands[lid])}]")
    for lid, m, t in bad: print(f'  ! {lid} best take still differs from the script by {m} chars: {t}')
    return pick


# ---------------------------------------------------------------- sounds
def t_(d): return np.arange(int(d * SR)) / SR
def lp(x, a):
    y = np.empty_like(x); s = 0.
    for i, v in enumerate(x): s += a * (v - s); y[i] = s
    return y
def whoosh():
    x = lp(np.random.default_rng(3).standard_normal(int(.55 * SR)), .07); e = np.sin(np.pi * np.linspace(0, 1, len(x)) ** .8) ** 2; return x * e * 1.4
def tick():
    tt = t_(.06); return np.sin(2 * np.pi * 1700 * tt) * np.exp(-tt * 70) * .5
def ding():
    tt = t_(.9); return sum(np.sin(2 * np.pi * 1318.5 * k * tt) / k ** 1.5 for k in (1, 2, 3)) * np.exp(-tt * 5) * .3
def place(buf, t, x, g=1.):
    i = int(t * SR); n = min(len(x), len(buf) - i)
    if n > 0 and i >= 0: buf[i:i + n] += x[:n] * g


def main():
    redo = set(sys.argv[sys.argv.index('--redo') + 1].split(',')) if '--redo' in sys.argv else set()
    make_takes(redo)
    pick = choose()
    t, prev, lines, order, scene_t, voice = LEAD, None, {}, [], {}, []
    for lid, sc, sub, read, extra in SCRIPT:
        if prev and sc != prev: t += SCENE_GAP
        if sc not in scene_t: scene_t[sc] = 0 if not prev else t - .9
        c = pick[lid]; y = c['y']
        # same loudness for every line (RMS of the voiced frames)
        db = frames_db(y); r = np.sqrt(np.mean(10 ** (db[db > -40] / 10))); y = y * (.08 / r)
        d = len(y) / SR
        words = []   # whisper splits some words ("two" "-digit"): pieces without a leading space join the word before
        for w in c['tr']['words']:
            if words and not w['w'].startswith(' '): words[-1][0] += w['w'].strip()
            else: words.append([w['w'].strip(), round(t + w['s'] - c['off'], 3)])
        words = [[re.sub(r"[^\w'%-]", '', w).lower(), s] for w, s in words]
        lines[lid] = {'scene': sc, 'text': sub, 'start': round(t, 3), 'end': round(t + d, 3), 'words': words}
        order.append(lid); voice.append((t, y)); t += d + GAP + extra; prev = sc
    dur = round(t - GAP + TAIL, 2)
    ids = [s for s, _ in SCENES]
    scenes = [{'id': s, 'label': lab, 'start': round(scene_t[s], 3), 'end': round(scene_t[ids[i + 1]] if i + 1 < len(ids) else dur, 3)} for i, (s, lab) in enumerate(SCENES)]
    TL = {'duration': dur, 'scenes': scenes, 'order': order, 'lines': lines}
    with open(os.path.join(ROOT, 'timeline.js'), 'w', encoding='utf-8') as f:
        f.write('// written by tools/make_audio.py (timing from the real narration; lines[id].words = spoken words and their start times). Do not edit by hand — rerun make_audio.py\n')
        f.write('window.TL = ' + json.dumps(TL, ensure_ascii=False) + ';\n')
    n = int(dur * SR); nar, fx = np.zeros(n), np.zeros(n)
    for s0, y in voice: place(nar, s0, y)
    for s in scenes[1:]:   # the page slides sideways at the same time (index.html); pages that carry on the same sheet (CONT) do not turn
        if s['id'] not in CONT: place(fx, s['start'] - .15, whoosh(), .3)
    place(fx, lines['l10_2']['start'] - .3, ding(), .35)
    mix = nar + fx
    mix = np.tanh(mix * 1.1) / 1.1
    mix = mix / (np.abs(mix).max() + 1e-9) * .89
    with wave.open(os.path.join(AUD, 'mix.wav'), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.repeat(mix, 2) * 32767).astype('<i2').tobytes())
    print(f'done: {dur:.1f}s, {len(order)} lines → timeline.js, audio/mix.wav')


if __name__ == '__main__':
    main()
