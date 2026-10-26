"""Adaptive Diagnostic Assessment v2 — narration from the recorded reading (audio/narration.mp3)

- The script, scene list, gaps, subtitle chunking and sound effects are imported from ../../adaptive-diagnosis/tools/make_audio.py
  (v1, the Qwen3-TTS version) and are not copied here, so both videos read the same script. v1's outputs are not touched.
- audio/narration.mp3 is one take of the same 31 lines. audio/narration_words.json is its word-level transcript
  (whisper large-v3-turbo: {"words": [{"w", "s", "e"}]}). The script's words are aligned to the transcript, each line is
  cut out at the middle of the silence around its first / last word, trimmed (a little air kept before and after), and
  placed with v1's rules: GAP between lines, SCENE_GAP between scenes, each line's extra pause.
- Writes ../timeline.js (subtitle chunks start on their first spoken word) and ../audio/mix.wav.
  timeline.js also carries `cues`: the times of the words the pictures and sound effects follow (index.html reads them).
- 3rd revision: the final script ([최종] 수학 어댑티브 정밀진단평가 영상 대본_최종.pdf) rewords the 15 lines in CLONE. They are not cut
  from the take but read by a clone of this take's voice (Qwen3-TTS on DGX, tools/clone_lines_dgx.py; reference = the take's l3–l4 as
  recorded; 8 candidates → Whisper text check → best speaker similarity → atempo to the old line's pace). audio/clone_<id>.wav is the
  pick, audio/clone_<id>.json its text (as the final script writes it) and words.
  Each is trimmed like the cut lines, EQ'd to the take's average spectrum (the clone is duller: 24 kHz output, -5…-15 dB at 5–11 kHz),
  matched to the loudness of the line it replaces and placed in its slot.

  python3 -m venv /tmp/venv && /tmp/venv/bin/pip install numpy soundfile
  /tmp/venv/bin/python tools/make_audio.py          # ffmpeg: $FFMPEG, else imageio_ffmpeg, else ffmpeg on PATH
"""
import os, sys, json, re, subprocess, difflib
import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
# v1's script, loaded by path under its own name: SCRIPT, SCENES, GAP, SCENE_GAP, chunks, ding/boop/pop/whoosh, place (loading does not run it)
import importlib.util
_spec = importlib.util.spec_from_file_location('make_audio_v1', os.path.join(ROOT, '..', 'adaptive-diagnosis', 'tools', 'make_audio.py'))
sys.dont_write_bytecode = True   # leave no __pycache__ in the v1 folder
v1 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(v1)

SR = v1.SR
MP3 = os.path.join(ROOT, 'audio', 'narration.mp3')
WORDS = os.path.join(ROOT, 'audio', 'narration_words.json')
SILENT_DB = -45          # 10 ms frames quieter than this count as a pause between lines (noise floor of the take is about -70 dB)
TRIM_DB = -55            # a line is trimmed to its frames louder than this (low enough to keep soft h / f / s onsets)
PRE, POST = .08, .15     # air kept before the first / after the last voiced frame of a line
CLONE = ['l3', 'l5', 'l6', 'l8', 'l11', 'l15', 'l16', 'l17', 'l21', 'l22', 'l23', 'l25', 'l27', 'l28', 'l29']   # reworded in the final script: cloned voice

def ffmpeg():
    if os.environ.get('FFMPEG'): return os.environ['FFMPEG']
    try:
        import imageio_ffmpeg; return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        pass
    try:   # the system python usually has imageio_ffmpeg even when this venv does not
        return subprocess.run(['python3', '-c', 'import imageio_ffmpeg as i; print(i.get_ffmpeg_exe())'], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return 'ffmpeg'

def decode(path):
    raw = subprocess.run([ffmpeg(), '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)

# ---------------------------------------------------------------- align the script to the transcript
NUM = {'1': 'one', '2': 'two', '3': 'three', '4': 'four', '5': 'five', '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine'}
def norm(word):
    out = []
    for p in word.lower().replace('-', ' ').replace('–', ' ').split():
        p = re.sub(r'[^a-z0-9]', '', p)
        if p == 'no': p = 'number'          # subtitles write "No. 3", the reader says "number three"
        p = NUM.get(p, p)
        if p: out.append(p)
    return out

def align(words, subs=None):
    """→ per line: list of (whitespace-word index in the subtitle, token, (s, e) in the take)"""
    subs = subs or [sub for _, _, sub, *_ in v1.SCRIPT]
    wt, wtime = [], []
    for w in words:
        for tok in norm(w['w']): wt.append(tok); wtime.append((w['s'], w['e']))
    st, owner = [], []
    for li, sub in enumerate(subs):
        for wi, w in enumerate(sub.split()):
            for tok in norm(w): st.append(tok); owner.append((li, wi))
    m = [None] * len(st)
    for a, b, n in difflib.SequenceMatcher(None, st, wt, autojunk=False).get_matching_blocks():
        for k in range(n): m[a + k] = b + k
    matched = sum(x is not None for x in m)
    print(f'aligned {matched}/{len(st)} script tokens to {len(wt)} transcript tokens')
    for i, x in enumerate(m):
        if x is None: print(f'  unmatched: line {owner[i][0]} "{st[i]}"')
    # unmatched tokens borrow the time of the nearest matched neighbour (start from the next one, end from the previous one)
    times = []
    for i in range(len(st)):
        if m[i] is not None: times.append(wtime[m[i]]); continue
        nxt = next((wtime[m[j]] for j in range(i + 1, len(st)) if m[j] is not None), None)
        prv = next((wtime[m[j]] for j in range(i - 1, -1, -1) if m[j] is not None), None)
        times.append(((nxt or prv)[0], (prv or nxt)[1]))
    per = [[] for _ in subs]
    for i, (li, wi) in enumerate(owner): per[li].append((wi, st[i], times[i]))
    return per

# ---------------------------------------------------------------- cut the take into lines
def frames_db(x, hop=441):
    n = len(x) // hop
    r = np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1))
    return 20 * np.log10(r + 1e-9)

def cut_between(db, e, s):
    """middle of the longest silence near the boundary between a line ending at e and the next starting at s (seconds)"""
    a, b = int((min(e, s) - .4) * 100), int((max(e, s) + .4) * 100)
    quiet = db[a:b] < SILENT_DB
    best, run, k0 = (0, None), 0, 0
    for k, q in enumerate(quiet):
        if q:
            if run == 0: k0 = k
            run += 1
            if run > best[0]: best = (run, k0)
        else: run = 0
    if best[0] < 3: return (e + s) / 2                      # no real pause: cut halfway
    return (a + best[1] + best[0] / 2) / 100

def lines_from_take(x, per):
    db = frames_db(x)
    bounds = [(toks[0][2][0], toks[-1][2][1]) for toks in per]
    cuts = [0.0] + [cut_between(db, bounds[i][1], bounds[i + 1][0]) for i in range(len(bounds) - 1)] + [len(x) / SR]
    out = []
    for i in range(len(per)):
        out.append(trim(x, db, cuts[i], cuts[i + 1]))
    return out, cuts

def trim(x, db, c0, c1):
    """(start, samples) of x[c0:c1] (seconds) cut to its voiced frames plus a little air, with short fades"""
    f0, f1 = int(c0 * 100), int(c1 * 100)
    voiced = np.where(db[f0:f1] >= TRIM_DB)[0]
    on, off = (f0 + voiced[0]) / 100, (f0 + voiced[-1] + 1) / 100
    a, b = max(c0, on - PRE), min(c1, off + POST)
    y = x[int(a * SR):int(b * SR)].copy()
    fi, fo = int(.012 * SR), int(.04 * SR)
    y[:fi] *= np.linspace(0, 1, fi); y[-fo:] *= np.linspace(1, 0, fo)
    return a, y

def speech_rms(y):
    e = 10 ** (frames_db(y) / 20)
    return np.sqrt(np.mean(e[e > np.percentile(e, 50)] ** 2))

def ltas(y, n=4096):
    """average power spectrum of the louder 60 % of frames"""
    fr = np.lib.stride_tricks.sliding_window_view(y, n)[::n // 2] * np.hanning(n)
    e = (fr ** 2).mean(1)
    return (np.abs(np.fft.rfft(fr[e > np.percentile(e, 40)], axis=1)) ** 2).mean(0)

def match_eq(y, ref, n=4096, maxdb=12, passes=3):
    """zero-phase EQ bringing y's average spectrum to ref's: gains in 1/3-octave bands (60 Hz–11 kHz, held outside), ±maxdb.
    Measured again after each pass (louder sibilants change which frames ltas picks) and the rest corrected."""
    f = np.fft.rfftfreq(n, 1 / SR)
    cen = 60 * 2 ** (np.arange(0, np.log2(11000 / 60), 1 / 3))
    bands = [(f >= c / 2 ** (1 / 6)) & (f < c * 2 ** (1 / 6)) for c in cen]
    Pr = ltas(ref, n)
    Y0 = np.fft.rfft(y, 2 * len(y)); F = np.fft.rfftfreq(2 * len(y), 1 / SR)
    g, out = np.zeros(len(cen)), y
    for _ in range(passes):
        Py = ltas(out, n)
        d = np.array([10 * np.log10(Pr[b].sum() / Py[b].sum()) for b in bands])
        g = np.clip(g + d - np.interp(1000, cen, d), -maxdb, maxdb)        # 0 dB at 1 kHz: level is matched separately
        out = np.fft.irfft(Y0 * 10 ** (np.interp(np.log2(np.maximum(F, 1)), np.log2(cen), g) / 20))[:len(y)]
    return out

def clone_lines(per, clips, take):
    """swap the CLONE lines' clips (and word times, text) for the cloned readings → {lid: new text}"""
    ids, texts = [lid for lid, *_ in v1.SCRIPT], {}
    for lid in CLONE:
        i = ids.index(lid)
        meta = json.load(open(os.path.join(ROOT, 'audio', f'clone_{lid}.json'), encoding='utf-8'))
        x = decode(os.path.join(ROOT, 'audio', f'clone_{lid}.wav'))
        a, y = trim(x, frames_db(x), 0, len(x) / SR)
        y = match_eq(y, take)
        y *= speech_rms(clips[i][1]) / speech_rms(y)          # as loud as the line it replaces
        print(f'{lid}: cloned reading {len(y) / SR:.2f}s (take {len(clips[i][1]) / SR:.2f}s)')
        per[i] = align(meta['words'], [meta['text']])[0]; clips[i] = (a, y); texts[lid] = meta['text']
    return texts

def main():
    x = decode(MP3)
    words = json.load(open(WORDS, encoding='utf-8'))['words']
    per = align(words)
    clips, cuts = lines_from_take(x, per)
    new_text = clone_lines(per, clips, x)
    # place the lines with v1's rules
    t, prev, lines, order, scene_t, voice, offs = 3.0, None, {}, [], {}, {}, {}
    for (lid, sc, sub, tts, extra), toks, (a, y) in zip(v1.SCRIPT, per, clips):
        sub = new_text.get(lid, sub)
        if prev and sc != prev: t += v1.SCENE_GAP
        if sc not in scene_t: scene_t[sc] = t - (.8 if prev else 3.0)
        d = len(y) / SR; voice[lid] = (t, y); offs[lid] = t - a          # take time + offs = timeline time
        first = {}
        for wi, tok, (s, e) in toks: first.setdefault(wi, s)
        cs, cl, wi = v1.chunks(sub), [], 0
        for c in cs:
            n = len(c.split())
            cl.append({'text': c, 'start': round(max(t, first.get(wi, a) + offs[lid] - .05), 3)}); wi += n
        lines[lid] = {'text': sub, 'start': round(t, 3), 'end': round(t + d, 3), 'scene': sc, 'chunks': cl}
        order.append(lid); t += d + v1.GAP + extra; prev = sc
    dur = round(t + .3, 2)
    ids = [s for s, _ in v1.SCENES]
    scenes = [{'id': s, 'label': lab, 'start': round(max(0, scene_t[s]), 3), 'end': round(scene_t[ids[i + 1]] if i + 1 < len(ids) else dur, 3)} for i, (s, lab) in enumerate(v1.SCENES)]

    tok_of = {lid: toks for (lid, *_), toks in zip(v1.SCRIPT, per)}
    def word(lid, w, nth=1):
        hits = [s for _, tok, (s, e) in tok_of[lid] if tok == w]
        if len(hits) < nth: sys.exit(f'cue word "{w}" (#{nth}) not found in {lid}')
        return round(hits[nth - 1] + offs[lid], 3)
    cues = {
        'adaptive': {'responsive': word('l8', 'responsive'), 'precision': word('l8', 'high'), 'realtime': word('l8', 'real'),
                     'next': word('l8', 'next'), 'correct': word('l8', 'correctly'), 'incorrect': word('l8', 'incorrectly')},
        'pathDown': [word('l15', 'incorrectly'), word('l15', 'three'), word('l15', 'one')],    # 5 ✗, 3 ✗, 1 ✓
        'pathUp': [word('l16', 'correctly'), word('l16', 'seven'), word('l16', 'nine')],       # 5 ✓, 7 ✓, 9 ✗
        'understood': word('l20', 'understood'), 'notUnderstood': word('l20', 'not'),
        'numbersOps': word('l23', 'numbers'),
    }
    TL = {'duration': dur, 'scenes': scenes, 'lines': lines, 'order': order, 'cues': cues}
    with open(os.path.join(ROOT, 'timeline.js'), 'w', encoding='utf-8') as f:
        f.write('// written by tools/make_audio.py (timing from the recorded narration, audio/narration.mp3; the reworded lines from the cloned readings audio/clone_*.wav). Do not edit by hand — rerun make_audio.py\n')
        f.write('window.TL = ' + json.dumps(TL, ensure_ascii=False) + ';\n')

    N = int(dur * SR); nar = np.zeros(N); fx = np.zeros(N)
    for lid, (s0, y) in voice.items(): v1.place(nar, s0, y)
    nar *= .9 / (np.abs(nar).max() + 1e-9)
    for s in scenes[1:]: v1.place(fx, s['start'] - .15, v1.whoosh(), .35)
    # same effects as v1, now on the words they belong to
    for k, tt in enumerate(cues['pathDown']): v1.place(fx, tt, v1.boop() if k < 2 else v1.pop(), .7)
    for k, tt in enumerate(cues['pathUp']): v1.place(fx, tt, v1.ding() if k < 2 else v1.pop(), .7)
    v1.place(fx, cues['understood'], v1.ding(), .6); v1.place(fx, cues['notUnderstood'], v1.boop(), .6)
    v1.place(fx, lines['l31']['start'] - .3, v1.ding(), .5)
    mix = nar * 1.0 + fx * .5
    mix = np.tanh(mix * .95) / .95
    mix = mix / (np.abs(mix).max() + 1e-9) * .9
    out = os.path.join(ROOT, 'audio', 'mix.wav')
    sf.write(out, np.stack([mix, mix], 1).astype(np.float32), SR, subtype='PCM_16')
    print('line cuts in the take (s):', ' '.join(f'{c:.2f}' for c in cuts[1:-1]))
    print(f'done: {out} ({dur}s, {len(order)} lines)')

if __name__ == '__main__':
    main()
