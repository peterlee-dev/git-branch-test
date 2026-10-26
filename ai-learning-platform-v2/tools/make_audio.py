"""JEI Math: An AI-Powered Personalized Learning Platform v2 — narration, timeline and mix (same narration as v1, cut into 30 pages: PAGE)

- Voice: Qwen3-TTS 1.7B Base (clone) on the DGX TTS API (POST /v1/tts/clone), following audio/voice_ref.wav
  (the 29 s reference from the D–I narration) and its words audio/voice_ref.txt
- Every line is read N times (default 3). Each take is transcribed with whisper large-v3-turbo (mlx-whisper);
  takes that do not read the script word for word are dropped, and of the rest the one closest to the median speaking
  rate without long pauses inside wins. Takes and transcripts are cached in audio/tts_cache/, so changing a line only
  re-reads that line (--redo l3_2,l6_4 reads those again)
- Lines are placed with GAP between lines and SCENE_GAP between scenes. Writes ../timeline.js (with each line's
  spoken words and their times, so index.html can key pictures to words) and audio/mix.wav (narration + page-turn
  whoosh + a few pen sounds, no music)

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
FFMPEG = os.environ.get('FFMPEG') or next((p for p in [os.path.join(ROOT, 'node_modules/ffmpeg-static/ffmpeg'), os.path.join(ROOT, '../math-di-improvement-v2/node_modules/ffmpeg-static/ffmpeg')] if os.path.exists(p)), 'ffmpeg')
LEAD, GAP, SCENE_GAP, TAIL = 2.6, .45, 1.0, 2.4

SCENES = [('title', 'Title'), ('vision', 'Our vision'),
          ('kmap', 'What is the Knowledge Map?'), ('kmapHow', 'How the map fits together'),
          ('gather', 'Building the map: input'), ('analyze', 'Building the map: AI analysis'), ('expand', 'Building the map: by country'),
          ('layerK', 'Knowledge layer'), ('layerA', 'AI Engine layer'), ('layerS', 'Service layer'),
          ('phases', 'Two phases, seven projects'), ('phase1', 'Phase 1'), ('phase2', 'Phase 2'), ('wiki', 'LLM Wiki'),
          ('pod', 'Personalized POD'), ('podCycle', 'The POD learning cycle'),
          ('behavior', 'How students learn'), ('loop', 'Adaptive learning path'), ('assistant', 'AI Learning Assistant'),
          ('statusMap', "A student's learning status"), ('statuses', 'Four learning statuses'), ('recommend', 'Recommended path'),
          ('ben1', 'Benefit 1'), ('ben2', 'Benefit 2'), ('ben3', 'Benefit 3'), ('ben4', 'Benefit 4'),
          ('roadmap', 'Roadmap'), ('roadmapPhases', 'What each phase delivers'), ('roadmapAll', 'Throughout development'),
          ('outro', 'Closing')]
# v2: the v1 scenes split into shorter pages (no page holds much longer than half a minute). line id → page
PAGE = {'l1_1': 'title', 'l1_2': 'vision', 'l1_3': 'vision', 'l2_1': 'kmap', 'l2_2': 'kmap', 'l2_3': 'kmap', 'l2_4': 'kmapHow', 'l2_5': 'kmapHow', 'l2_6': 'kmapHow',
        'l3_1': 'gather', 'l3_2': 'gather', 'l3_3': 'gather', 'l3_4': 'analyze', 'l3_5': 'analyze', 'l3_6': 'analyze', 'l3_7': 'expand', 'l3_8': 'expand',
        'l4_1': 'layerK', 'l4_2': 'layerK', 'l4_3': 'layerK', 'l4_4': 'layerK', 'l4_5': 'layerA', 'l4_6': 'layerA', 'l4_7': 'layerA',
        'l4_8': 'layerS', 'l4_9': 'layerS', 'l4_10': 'layerS', 'l4_11': 'layerS',
        'l5_1': 'phases', 'l5_2': 'phases', 'l5_3': 'phase1', 'l5_4': 'phase1', 'l5_5': 'phase2', 'l5_6': 'wiki', 'l5_7': 'wiki',
        'l6_1': 'pod', 'l6_2': 'pod', 'l6_3': 'pod', 'l6_4': 'pod', 'l6_5': 'podCycle', 'l6_6': 'podCycle',
        'l6_7': 'behavior', 'l6_8': 'behavior', 'l6_9': 'behavior', 'l6_10': 'loop', 'l6_11': 'loop', 'l6_12': 'assistant', 'l6_13': 'assistant',
        'l7_1': 'statusMap', 'l7_2': 'statusMap', 'l7_3': 'statusMap', 'l7_4': 'statusMap', 'l7_5': 'statuses', 'l7_6': 'statuses', 'l7_7': 'statuses',
        'l7_8': 'recommend', 'l7_9': 'recommend', 'l8_1': 'ben1', 'l8_2': 'ben1', 'l8_3': 'ben2', 'l8_4': 'ben3', 'l8_5': 'ben4', 'l8_6': 'ben4',
        'l9_1': 'roadmap', 'l9_2': 'roadmap', 'l9_3': 'roadmapPhases', 'l9_4': 'roadmapPhases', 'l9_5': 'roadmapPhases', 'l9_6': 'roadmapAll', 'l9_7': 'roadmapAll',
        'l10_1': 'outro', 'l10_2': 'outro', 'l10_3': 'outro'}
# (id, scene, line as written, line as read (None = as written), extra pause after it)
SCRIPT = [
    ('l1_1', 'intro', "This project is about more than using AI to make our work more efficient. It's about improving JEI's learning products and services themselves.", None, 0),
    ('l1_2', 'intro', "Over the past 50 years, JEI has built a rich foundation of learning design expertise and educational resources.", None, 0),
    ('l1_3', 'intro', "By organizing these resources in a way that AI can use, we aim to create JEI's own personalized learning platform—one that connects printed workbooks, print-on-demand materials, and online learning into a unified system.",
     "By organizing these resources in a way that AI can use, we aim to create JEI's own personalized learning platform, one that connects printed workbooks, print-on-demand materials, and online learning into a unified system.", 0),

    ('l2_1', 'kmap', "The starting point for this platform is the JEI-Math Knowledge Map.", "The starting point for this platform is the JEI Math Knowledge Map.", .2),
    ('l2_2', 'kmap', "Think of it as a connected network of math learning objectives. Each objective is represented by a point, and the lines show how the objectives relate to one another.", None, 0),
    ('l2_3', 'kmap', "For example, students may start with single-digit addition, move on to addition with sums up to 18, and then progress to two-digit addition with regrouping.",
     "For example, students may start with single-digit addition, move on to addition with sums up to eighteen, and then progress to two-digit addition with regrouping.", 0),
    ('l2_4', 'kmap', "The Knowledge Map organizes these skills in a logical sequence and shows how different math concepts build on one another.", None, 0),
    ('l2_5', 'kmap', "Each learning objective also includes information about the content and its difficulty level.", None, 0),
    ('l2_6', 'kmap', "This allows AI to understand not just individual learning objectives, but how the entire math learning structure fits together.", None, 0),

    ('l3_1', 'build', "Our goal is to create a shared math learning framework that reflects JEI's own educational approach, rather than being tied to the curriculum of any single country.", None, .2),
    ('l3_2', 'build', "We begin by gathering and organizing a wide range of resources, including JEI's educational philosophy, math workbooks and learning objectives from Korea and the United States, and internal research materials.", None, 0),
    ('l3_3', 'build', "We also incorporate curricula and learning standards from different countries.", None, 0),
    ('l3_4', 'build', "AI compares and analyzes these resources to identify similarities and differences. It then proposes learning objectives and the connections between them.", None, 0),
    ('l3_5', 'build', "JEI researchers review these proposals, checking their educational validity and the evidence supporting them.", None, 0),
    ('l3_6', 'build', "By repeating this process, we can continuously refine the Knowledge Map.", None, 0),
    ('l3_7', 'build', "We're also designing the system to analyze and incorporate new resources as they become available, allowing the map to evolve over time.", None, .2),
    ('l3_8', 'build', "Once the shared Knowledge Map is connected to different national curricula, JEI will be able to develop learning programs and content for each country or region more quickly and flexibly.", None, 0),

    ('l4_1', 'layers', "The AI-powered personalized learning platform is built around three connected layers: Knowledge, AI Engine, and Services.", None, .2),
    ('l4_2', 'layers', "The first is the Knowledge Layer.", None, 0),
    ('l4_3', 'layers', "This layer organizes learning objectives, workbooks, and educational knowledge in a structured format that AI can use.", None, 0),
    ('l4_4', 'layers', "It provides a shared foundation for analyzing student learning and generating educational content.", None, .2),
    ('l4_5', 'layers', "The second is the AI Engine Layer.", None, 0),
    ('l4_6', 'layers', "Using this knowledge, the AI engines generate programmed learning content that guides students step by step.", None, 0),
    ('l4_7', 'layers', "They also support the analysis of students' learning status and features such as explanations and hints.", None, .2),
    ('l4_8', 'layers', "The third is the Service Layer.", None, 0),
    ('l4_9', 'layers', "This is where AI-generated content and insights are turned into actual learning products and services, including workbooks, personalized print-on-demand materials, online learning, and teacher support tools.", None, 0),
    ('l4_10', 'layers', "Students' learning results are then fed back into the system to help determine what they should learn next.", None, .2),
    ('l4_11', 'layers', "In short, the platform allows multiple AI functions and learning services to operate from one shared knowledge foundation.", None, 0),

    ('l5_1', 'phases', "Platform development will take place in two major phases.", None, 0),
    ('l5_2', 'phases', "The seven projects are closely connected and will move forward in parallel, rather than being developed strictly one after another.", None, .2),
    ('l5_3', 'phases', "In Phase 1, we'll build the Knowledge Map of learning objectives and develop automated content generation capabilities.", "In Phase One, we'll build the Knowledge Map of learning objectives and develop automated content generation capabilities.", 0),
    ('l5_4', 'phases', "We'll also introduce personalized print-on-demand, or POD, learning materials to test a continuous learning cycle in which each student's results help determine what comes next.",
     "We'll also introduce personalized print-on-demand, or P-O-D, learning materials to test a continuous learning cycle in which each student's results help determine what comes next.", .2),
    ('l5_5', 'phases', "In Phase 2, we'll expand into online personalized learning by developing learning status analysis, adaptive learning paths, and an AI Learning Assistant.",
     "In Phase Two, we'll expand into online personalized learning by developing learning status analysis, adaptive learning paths, and an AI Learning Assistant.", .2),
    ('l5_6', 'phases', "Alongside these projects, we'll also build LLM Wiki, a shared knowledge base that JEI staff can directly edit and manage.", None, 0),
    ('l5_7', 'phases', "LLM Wiki will bring together JEI's educational philosophy and research knowledge, providing a consistent source of information for all projects.", None, 0),

    ('l6_1', 'pod', "The main service in Phase 1 will be personalized print-on-demand learning materials, designed around each student's individual needs.", "The main service in Phase One will be personalized print-on-demand learning materials, designed around each student's individual needs.", .2),
    ('l6_2', 'pod', "First, we'll analyze diagnostic assessment results and learning history to determine which learning objectives a student needs to focus on and how much practice they need.", None, 0),
    ('l6_3', 'pod', "AI will then generate programmed learning content based on those needs.", None, 0),
    ('l6_4', 'pod', "JEI researchers will review the generated materials before they're provided as personalized worksheets.", None, 0),
    ('l6_5', 'pod', "Afterward, we'll analyze the student's learning results and adjust both the content and the amount of practice for the next learning cycle.", None, .2),
    ('l6_6', 'pod', "POD can be used in different ways, from creating personalized worksheets to adding targeted supplementary materials to existing workbooks.", "P-O-D can be used in different ways, from creating personalized worksheets to adding targeted supplementary materials to existing workbooks.", 0),

    ('l6_7', 'online', "In Phase 2, we'll bring this approach into an online learning environment.", "In Phase Two, we'll bring this approach into an online learning environment.", 0),
    ('l6_8', 'online', "Instead of looking only at right and wrong answers, we'll also analyze how students learn.", None, 0),
    ('l6_9', 'online', "This includes how long they spend solving problems, whether they use hints, and how often they try again.", None, 0),
    ('l6_10', 'online', "These learning behaviors will help the system understand each student's current learning status.", None, .2),
    ('l6_11', 'online', "Based on that information, AI will continuously adjust the student's learning path and provide appropriate content for additional practice, review, or more advanced learning.", None, .2),
    ('l6_12', 'online', "The AI Learning Assistant will also help students work through problems independently by offering hints and explanations instead of simply giving them the answers.", None, 0),
    ('l6_13', 'online', "For teachers, the system will provide information about each student's learning progress and areas of difficulty, helping them offer more focused and effective guidance.", None, 0),

    ('l7_1', 'status', "This screen shows a conceptual example of how an individual student's learning status could be displayed on the shared Knowledge Map.", None, .2),
    ('l7_2', 'status', "The upper section represents concepts the student has not yet studied.", None, 0),
    ('l7_3', 'status', "The middle section shows concepts the student is currently learning or areas that need further assessment.", None, 0),
    ('l7_4', 'status', "The lower section represents concepts the student has already studied.", None, .2),
    ('l7_5', 'status', "Each learning objective is classified into one of four learning statuses: Mastered, Needs More Practice, Learning Gap, or Not Yet Studied.", None, .2),
    ('l7_6', 'status', "This gives us more than a simple picture of how far a student has progressed.", None, 0),
    ('l7_7', 'status', "It helps us understand what the student has learned well and where additional support may be needed.", None, 0),
    ('l7_8', 'status', "AI will use this information to recommend the learning objectives and learning path that best match each student's needs.", None, .2),
    ('l7_9', 'status', "The specific criteria for determining and updating these learning statuses will be developed and validated separately, using diagnostic assessment results and actual learning data.", None, 0),

    ('l8_1', 'benefits', "With the JEI-Math Knowledge Map as our foundation, we aim to achieve four major improvements.", "With the JEI Math Knowledge Map as our foundation, we aim to achieve four major improvements.", .2),
    ('l8_2', 'benefits', "First, by connecting the shared Knowledge Map to different national curricula, we can develop learning programs and content tailored to each country or region more quickly.", None, .2),
    ('l8_3', 'benefits', "Second, by analyzing assessment results and learning data, we can identify what each student understands, where they need additional support, and how their learning path should be adjusted.", None, .2),
    ('l8_4', 'benefits', "Third, by selecting the right learning objectives and amount of practice for each student, we can deliver personalized learning through both POD materials and online services.",
     "Third, by selecting the right learning objectives and amount of practice for each student, we can deliver personalized learning through both P-O-D materials and online services.", .2),
    ('l8_5', 'benefits', "Fourth, we plan to connect academic achievement data with the JEI Self-Learning Index, or JEI-SLI, to better understand and track each student's growth over time.",
     "Fourth, we plan to connect academic achievement data with the JEI Self-Learning Index, or J-E-I S-L-I, to better understand and track each student's growth over time.", .2),
    ('l8_6', 'benefits', "Together, these improvements will help us build JEI's own AI-powered learning platform, connecting content development, personalized learning, and ongoing support for student growth.", None, 0),

    ('l9_1', 'roadmap', "Our overall development plan is divided into two phases.", None, 0),
    ('l9_2', 'roadmap', "Phase 1 will run from the fourth quarter of 2026 through the end of 2027, while Phase 2 will begin in 2028.",
     "Phase One will run from the fourth quarter of twenty twenty-six through the end of twenty twenty-seven, while Phase Two will begin in twenty twenty-eight.", .2),
    ('l9_3', 'roadmap', "During Phase 1, we'll develop the Knowledge Map and automated content generation capabilities.", "During Phase One, we'll develop the Knowledge Map and automated content generation capabilities.", 0),
    ('l9_4', 'roadmap', "We'll then test and validate personalized POD learning in the United States before expanding the service to Korea.", "We'll then test and validate personalized P-O-D learning in the United States before expanding the service to Korea.", .2),
    ('l9_5', 'roadmap', "In Phase 2, we'll bring together learning status analysis, adaptive learning paths, and the AI Learning Assistant to create an online personalized learning platform.",
     "In Phase Two, we'll bring together learning status analysis, adaptive learning paths, and the AI Learning Assistant to create an online personalized learning platform.", .2),
    ('l9_6', 'roadmap', "Throughout development, we'll continue to improve the Knowledge Map and AI engines on a quarterly basis by adding new resources, conducting further analysis, and refining their capabilities.", None, 0),
    ('l9_7', 'roadmap', "At the same time, LLM Wiki will serve as the shared knowledge base supporting every stage of the development process.", None, 0),

    ('l10_1', 'outro', "By bringing together 50 years of learning design expertise and AI technology, JEI is working to create a new approach to personalized learning.", None, .2),
    ('l10_2', 'outro', "Our goal is to provide every student with a learning experience that better meets their individual needs.", None, .5),
    ('l10_3', 'outro', "Thank you.", None, 0),
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
        for k in range(N_TAKES):
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
        for k in range(N_TAKES):
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
    for lid, _, sub, read, extra in SCRIPT:
        sc = PAGE[lid]
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
    for s in scenes[1:]: place(fx, s['start'] - .15, whoosh(), .3)   # the page slides sideways at the same time (index.html)
    place(fx, lines['l10_3']['start'] - .3, ding(), .35)
    mix = nar + fx
    mix = np.tanh(mix * 1.1) / 1.1
    mix = mix / (np.abs(mix).max() + 1e-9) * .89
    with wave.open(os.path.join(AUD, 'mix.wav'), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.repeat(mix, 2) * 32767).astype('<i2').tobytes())
    print(f'done: {dur:.1f}s, {len(order)} lines → timeline.js, audio/mix.wav')


if __name__ == '__main__':
    main()
