"""v2 sound mix — same narration as ../adaptive-diagnosis (cloned-voice Qwen3-TTS lines from its audio/tts_cache),
with the correct / incorrect cues moved to v2's own step times in the 'path' scene (STEPS below = STEPS in index.html).

  python3 tools/make_mix.py        # → audio/mix.wav (run tools/sync_narration.sh first if the narration changed)
"""
import os, sys, json
import numpy as np, soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(ROOT, '..', 'adaptive-diagnosis', 'tools'))
import make_audio as V1                                   # narration lines, sound-effect synths, place()

STEPS = {'l15': [.2, .5, .66], 'l16': [.3, .5, .64]}      # keep in sync with index.html

def main():
    src = open(os.path.join(ROOT, 'timeline.js'), encoding='utf-8').read()
    TL = json.loads(src[src.index('{'):src.rindex('}') + 1])
    L = TL['lines']; dur = TL['duration']; SR = V1.SR
    N = int(dur * SR); nar = np.zeros(N); fx = np.zeros(N)
    for lid, sc, sub, tts, _ in V1.SCRIPT: V1.place(nar, L[lid]['start'], V1.load_line(tts or sub))
    for s in TL['scenes'][1:]: V1.place(fx, s['start'] - .15, V1.whoosh(), .35)
    at = lambda lid, f: L[lid]['start'] + (L[lid]['end'] - L[lid]['start']) * f
    # incorrect case: 5 ✗, 3 ✗, 1 ✓ (then check 2) — correct case: 5 ✓, 7 ✓, 9 ✗ (then check 8)
    for f, snd in zip(STEPS['l15'], [V1.boop, V1.boop, V1.ding]): V1.place(fx, at('l15', f), snd(), .7)
    for f, snd in zip(STEPS['l16'], [V1.ding, V1.ding, V1.boop]): V1.place(fx, at('l16', f), snd(), .7)
    V1.place(fx, L['l20']['start'] + .8, V1.ding(), .6); V1.place(fx, L['l20']['start'] + 3.4, V1.boop(), .6)
    V1.place(fx, L['l31']['start'] - .3, V1.ding(), .5)
    mix = nar + fx * .5                                   # no background music
    mix = np.tanh(mix * .95) / .95; mix = mix / (np.abs(mix).max() + 1e-9) * .9
    out = os.path.join(ROOT, 'audio', 'mix.wav'); sf.write(out, np.stack([mix, mix], 1).astype(np.float32), SR, subtype='PCM_16')
    print(f'done: {out} ({dur}s)')

if __name__ == '__main__':
    main()
