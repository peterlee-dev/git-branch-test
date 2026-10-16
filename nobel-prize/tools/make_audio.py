"""노벨상이 궁금해요 — 내레이션·효과음·배경음 만들기

- 목소리: Qwen3-TTS (Apache 2.0), DGX의 TTS API(../../ ~/dev/dgx-tts/API.md)를 HTTP로 불러요
  1) --design: VoiceDesign으로 내레이터 목소리 후보를 지어 audio/voice_cands/ 에 저장 → 하나를 골라 audio/voice_ref.wav 로 복사
  2) 기본 실행: Base(복제) 모델이 voice_ref.wav 를 따라 모든 문장을 읽음 → 한 목소리가 끝까지 같아요
- 문장마다 실제 길이로 시각을 정해 ../timeline.js 를 씀 → 화면(index.html)이 따라 움직여요
- 효과음(뿅, 반짝, 휙, 딩동, 도장)·배경음(마림바 느낌의 밝은 반복 선율)은 numpy 로 합성

  TTS_URL=http://192.168.51.8:8095 python3 tools/make_audio.py --design   # 목소리 후보 만들기 (처음 한 번)
  python3 tools/make_audio.py                                              # 음성·시각표·믹스
  (만든 음성은 audio/tts_cache/ 에 남아서, 문장을 고치면 그 줄만 다시 만들어요. 다시 뽑으려면 --redo n3,f1)
"""
import os, sys, json, hashlib, re, subprocess, urllib.request, uuid, wave
import numpy as np

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
AUD = os.path.join(ROOT, 'audio')
CACHE = os.path.join(AUD, 'tts_cache')
REF = os.path.join(AUD, 'voice_ref.wav')
REF_TXT = os.path.join(AUD, 'voice_ref.txt')
TTS = os.environ.get('TTS_URL', 'http://192.168.51.8:8095')
FFMPEG = os.environ.get('FFMPEG') or next((p for p in [os.path.join(ROOT, 'node_modules/ffmpeg-static/ffmpeg'), os.path.join(ROOT, '../math-di-improvement-v2/node_modules/ffmpeg-static/ffmpeg')] if os.path.exists(p)), 'ffmpeg')
GAP, SCENE_GAP, LEAD = .35, 1.0, 1.0

VOICE_DESIGN = ('밝고 상냥한 30대 한국 여성 어린이 교양 프로그램 내레이터 목소리. 또랑또랑하고 정확한 표준어 발음, '
                '궁금증을 불러일으키는 생기 있는 말투, 너무 빠르지 않게 또박또박.')
VOICE_SAMPLE = '안녕하세요, 여러분! 오늘은 세상에서 가장 유명한 상에 대해 함께 알아볼 거예요. 정말 궁금하지 않나요?'

SCENES = [('hook', '네 사람의 공통점'), ('title', '제목'), ('origin', '노벨의 유언'), ('fields', '여섯 분야'),
          ('select', '심사 과정'), ('rules', '수상 인원'), ('anyone', '누구나 받을 수 있어요'), ('alive', '세상을 떠난 사람은?'),
          ('outro', '마무리')]
# (id, 장면, 자막, 읽을 문장(None = 자막과 같음), 뒤에 더 쉴 시간)
SCRIPT = [
    ('h1', 'hook', '과학자 아인슈타인, 대통령 김대중, 가수 밥 딜런, 인권 운동가 말랄라 유사프자이.', '과학자 아인슈타인, 대통령 김대중, 가수 밥 딜런, 인권 운동가 말랄라 유사프자이.', .3),
    ('h2', 'hook', '나라도, 나이도, 하는 일도 모두 다른 이 네 사람에게는 놀라운 공통점이 하나 있어요.', None, .3),
    ('h3', 'hook', '과연 무엇일까요? 힌트를 하나 줄게요.', None, .4),
    ('h4', 'hook', '이 사람은 다이너마이트를 발명한 알프레드 노벨이에요.', None, .5),
    ('h5', 'hook', '이제 알겠죠? 네 사람은 모두 노벨상을 받은 사람들이에요.', None, .3),
    ('h6', 'hook', '세계에서 가장 영예로운 상, 노벨상! 누가, 어떻게 받게 되는 걸까요?', None, .2),

    ('t1', 'title', '지식 한 스푼! 노벨상이 궁금해요!', None, 1.4),

    ('o1', 'origin', '노벨은 세상을 떠나기 전, 자신의 재산으로 인류에게 큰 도움을 준 사람들에게 상을 주라는 유언을 남겼어요.', None, .3),
    ('o2', 'origin', '그렇게 해서 1901년, 첫 번째 노벨상이 주어졌답니다.', '그렇게 해서 천구백일 년, 첫 번째 노벨상이 주어졌답니다.', .2),

    ('f1', 'fields', '처음 노벨상은 물리학, 화학, 생리학·의학, 문학, 평화, 이렇게 다섯 분야였어요.', '처음 노벨상은 물리학, 화학, 생리학 의학, 문학, 평화, 이렇게 다섯 분야였어요.', .3),
    ('f2', 'fields', '그리고 1969년부터 경제학상이 더해져, 지금은 모두 여섯 분야에서 상을 준답니다.', '그리고 천구백육십구 년부터 경제학상이 더해져, 지금은 모두 여섯 분야에서 상을 준답니다.', .2),

    ('s1', 'select', '노벨상 심사는 아주 꼼꼼하고 엄격해요.', None, .2),
    ('s2', 'select', '먼저 분야마다 세계 곳곳의 전문가 수천 명에게서 후보를 추천받아요.', None, .3),
    ('s3', 'select', '그다음 후보들의 연구와 업적을 하나하나 살펴서 최종 후보를 골라요.', None, .3),
    ('s4', 'select', '마지막으로 분야마다 정해진 기관에서 수상자를 결정하지요.', None, .3),
    ('s5', 'select', '이 과정은 철저한 비밀이라서, 누가 추천되었는지는 50년이 지나야 공개된대요.', '이 과정은 철저한 비밀이라서, 누가 추천되었는지는 오십 년이 지나야 공개된대요.', .2),

    ('r1', 'rules', '그런데 한 분야에서 꼭 한 명만 상을 받는 건 아니에요.', None, .2),
    ('r2', 'rules', '세 명까지 함께 받을 수 있고, 수상자가 없어서 상을 주지 않은 해도 있었어요.', None, .3),
    ('r3', 'rules', '또 노벨상은 사람에게 주는 것이 원칙이지만, 평화상은 단체가 받을 수도 있어요.', None, .2),

    ('a1', 'anyone', '노벨상은 나라, 인종, 종교와 상관없이 누구나 받을 수 있어요.', None, .3),
    ('a2', 'anyone', '한 번 받은 사람이 또 받을 수도 있지요. 마리 퀴리는 물리학상과 화학상을 모두 받았어요.', None, .2),

    ('d1', 'alive', '하지만 이미 세상을 떠난 사람에게는 상을 주지 않아요.', None, .3),
    ('d2', 'alive', '단, 수상자로 발표된 뒤 시상식 전에 세상을 떠났다면 상을 그대로 준답니다.', None, .2),
    ('d3', 'alive', '한 번 정해진 수상자는 바꾸지 않기 때문이에요.', None, .2),

    ('e1', 'outro', '노벨상 시상식은 해마다 노벨이 세상을 떠난 날인 12월 10일에 열려요.', '노벨상 시상식은 해마다 노벨이 세상을 떠난 날인 십이월 십일에 열려요.', .3),
    ('e2', 'outro', '인류를 위해 큰일을 해낸 사람들에게 주는 상, 노벨상.', None, .3),
    ('e3', 'outro', '수상자들의 땀과 노력이 바로 노벨이 꿈꾸던 평화롭고 발전된 세상을 만들어 가고 있어요.', None, .3),
    ('e4', 'outro', '여러분도 언젠가 세상을 밝히는 주인공이 될 수 있지 않을까요?', None, 2.6),
]
# 효과음: (문장 id, 문장 안 위치 0~1 또는 '+초'로 끝난 뒤, 소리, 크기). 화면도 같은 시각(TL.sfx)에 맞춰 움직여요
SFX = [
    ('h1', 0.0, 'pop', .8), ('h1', .3, 'pop', .8), ('h1', .55, 'pop', .8), ('h1', .78, 'pop', .8),
    ('h3', .15, 'boing', .7), ('h4', 0.0, 'whoosh', .6), ('h4', .45, 'fuse', .5),
    ('h5', .55, 'chime', .7), ('h6', 0.0, 'sparkle', .7),
    ('t1', 0.0, 'fanfare', .8),
    ('o1', .55, 'scribble', .5), ('o2', .25, 'stamp', .8),
    ('f1', .2, 'pop', .6), ('f1', .3, 'pop', .6), ('f1', .42, 'pop', .6), ('f1', .58, 'pop', .6), ('f1', .7, 'pop', .6), ('f2', .35, 'chime', .7),
    ('s2', .1, 'whoosh', .4), ('s3', .2, 'tick', .5), ('s4', .55, 'stamp', .8), ('s5', .3, 'lock', .7),
    ('r2', .05, 'pop', .6), ('r2', .15, 'pop', .6), ('r2', .25, 'pop', .6), ('r2', .62, 'boing', .5), ('r3', .6, 'chime', .6),
    ('a1', .1, 'whoosh', .4), ('a2', .7, 'chime', .6), ('a2', .9, 'chime', .6),
    ('d3', .3, 'lock', .6),
    ('e1', .1, 'fanfare', .6), ('e4', '+0.4', 'sparkle', .8),
]


def h(*a): return hashlib.sha1('|'.join(a).encode()).hexdigest()[:16]


def post(path, fields, files=None):
    """application/json 이거나 (files 있으면) multipart/form-data 로 POST → 바이트"""
    if files:
        b = uuid.uuid4().hex; body = b''
        for k, v in fields.items(): body += f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
        for k, (name, data) in files.items(): body += f'--{b}\r\nContent-Disposition: form-data; name="{k}"; filename="{name}"\r\nContent-Type: application/octet-stream\r\n\r\n'.encode() + data + b'\r\n'
        body += f'--{b}--\r\n'.encode(); ctype = f'multipart/form-data; boundary={b}'
    else:
        body = json.dumps(fields).encode(); ctype = 'application/json'
    req = urllib.request.Request(TTS + path, data=body, headers={'Content-Type': ctype}, method='POST')
    with urllib.request.urlopen(req, timeout=300) as r: return r.read()


def decode(path):
    """아무 음성 파일 → float32 mono SR"""
    out = subprocess.run([FFMPEG, '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(out, np.float32).copy()


def trim(x, thr=.01):
    idx = np.where(np.abs(x) > thr)[0]
    if not len(idx): return x
    a, b = max(0, idx[0] - int(.03 * SR)), min(len(x), idx[-1] + int(.08 * SR))
    return x[a:b]


def design():
    d = os.path.join(AUD, 'voice_cands'); os.makedirs(d, exist_ok=True)
    for i in range(int(os.environ.get('N', 4))):
        wav = post('/v1/tts/design', {'text': VOICE_SAMPLE, 'instruct': VOICE_DESIGN, 'language': 'Korean', 'format': 'wav'})
        p = os.path.join(d, f'cand{i + 1}.wav'); open(p, 'wb').write(wav); print('→', p, f'{len(decode(p)) / SR:.2f}s')
    open(os.path.join(d, 'sample.txt'), 'w').write(VOICE_SAMPLE)
    print('골라서: cp audio/voice_cands/candN.wav audio/voice_ref.wav && cp audio/voice_cands/sample.txt audio/voice_ref.txt')


def ref_id(): return h(open(REF, 'rb').read().hex()[:20000], open(REF_TXT).read().strip())


def line_path(tts): return os.path.join(CACHE, h(ref_id(), tts) + '.wav')


def make_voices(redo=()):
    os.makedirs(CACHE, exist_ok=True)
    ref, ref_text = open(REF, 'rb').read(), open(REF_TXT).read().strip()
    for lid, _, sub, tts, _ in SCRIPT:
        p = line_path(tts or sub)
        if os.path.exists(p) and lid not in redo: continue
        print('TTS', lid, (tts or sub)[:40])
        wav = post('/v1/tts/clone', {'text': tts or sub, 'ref_text': ref_text, 'language': 'Korean', 'format': 'wav'}, {'ref_audio': ('ref.wav', ref)})
        open(p, 'wb').write(wav)


# ---------------- 합성 소리 ----------------
def t_(d): return np.arange(int(d * SR)) / SR
def env(n, a=.004, r=.1):
    e = np.ones(n); na, nr = int(a * SR), int(r * SR)
    if na: e[:na] = np.linspace(0, 1, na)
    if nr: e[-nr:] *= np.linspace(1, 0, min(nr, n))[-nr:]
    return e
def tone(f, d, g=.3, dec=6, harm=(1,)):
    tt = t_(d); x = sum(np.sin(2 * np.pi * f * k * tt) / k ** 1.4 for k in harm)
    return x * np.exp(-tt * dec) * np.minimum(1, tt / .004) * g
def noise(d, seed=1): return np.random.default_rng(seed).standard_normal(int(d * SR))
def lp(x, a):
    y = np.empty_like(x); s = 0.
    for i, v in enumerate(x): s += a * (v - s); y[i] = s
    return y
def mix_at(buf, x, t, g=1.):
    i = int(t * SR); n = min(len(x), len(buf) - i)
    if n > 0 and i >= 0: buf[i:i + n] += x[:n] * g


def sfx(name):
    if name == 'pop':
        tt = t_(.14); f = 520 + 900 * np.exp(-tt * 30); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 28) * .5
    if name == 'boing':
        tt = t_(.5); f = 180 + 120 * np.sin(2 * np.pi * 9 * tt) * np.exp(-tt * 5) + 80 * tt; return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 6) * .45
    if name == 'whoosh':
        x = lp(noise(.5, 3), .08); e = np.sin(np.pi * np.linspace(0, 1, len(x))) ** 2; return x * e * 1.6
    if name == 'swish':
        x = lp(noise(.35, 4), .2); e = np.sin(np.pi * np.linspace(0, 1, len(x)) ** .6) ** 2; return x * e * 1.1
    if name == 'fuse':
        x = noise(.8, 5) * (np.random.default_rng(7).random(int(.8 * SR)) > .97) * .5; return lp(x, .5) * env(len(x), .01, .2)
    if name == 'chime':
        return tone(1318.5, .9, .22, 4, (1, 2, 3)) + np.concatenate([np.zeros(int(.09 * SR)), tone(1975.5, .81, .18, 4, (1, 2))])
    if name == 'sparkle':
        out = np.zeros(int(1.2 * SR)); rng = np.random.default_rng(11)
        for i in range(9): mix_at(out, tone(rng.choice([2093, 2349, 2637, 3136, 3520]), .4, .09, 9), i * .09)
        return out
    if name == 'fanfare':
        out = np.zeros(int(1.8 * SR))
        for i, (f, d) in enumerate([(523.25, .14), (659.25, .14), (783.99, .14), (1046.5, .9)]):
            mix_at(out, tone(f, d + .5, .2, 3 if d > .5 else 8, (1, 2, 3, 4)), i * .15)
        return out
    if name == 'stamp':
        tt = t_(.25); return (np.sin(2 * np.pi * 90 * tt) * .7 + lp(noise(.25, 9), .3) * .6) * np.exp(-tt * 22) * .8
    if name == 'scribble':
        x = lp(noise(1.0, 13), .4) * (.5 + .5 * np.sign(np.sin(2 * np.pi * 6 * t_(1.0)))) * .35; return x * env(len(x), .02, .1)
    if name == 'tick':
        out = np.zeros(int(1.2 * SR))
        for i in range(4): mix_at(out, tone(1800, .05, .25, 60), i * .28)
        return out
    if name == 'lock':
        return np.concatenate([tone(1400, .05, .3, 50), np.zeros(int(.06 * SR)), tone(900, .12, .35, 30)])
    raise KeyError(name)


def bgm(dur):
    """밝은 마림바 느낌 반복 선율 (F장조, 96bpm) — 내레이션 밑에 아주 작게"""
    out = np.zeros(int(dur * SR) + SR); beat = 60 / 96
    def mar(f, d=.5, g=.12): return tone(f, d, g, 7, (1, 4))
    chords = [(174.61, [349.23, 440, 523.25]), (233.08, [349.23, 466.16, 587.33]), (130.81, [329.63, 392, 523.25]), (174.61, [349.23, 440, 523.25])]
    melody = [523.25, 587.33, 659.25, 523.25, 698.46, 659.25, 587.33, 523.25, 466.16, 523.25, 587.33, 466.16, 440, 392, 440, 523.25]
    t, bar = 0., 0
    while t < dur:
        root, ch = chords[bar % 4]
        mix_at(out, tone(root / 2, beat * 2, .16, 2.5, (1, 2)), t); mix_at(out, tone(root / 2, beat * 2, .1, 2.5, (1, 2)), t + beat * 2)
        for k in range(4):
            for f in ch: mix_at(out, mar(f, .35, .035), t + k * beat + beat / 2)
        for k in range(4):
            if (bar // 4) % 2 == 0 or k % 2 == 0: mix_at(out, mar(melody[(bar % 4) * 4 + k] , .5, .07), t + k * beat)
        t += beat * 4; bar += 1
    return out[:int(dur * SR)]


def chunks(text, maxc=34):
    """긴 자막을 화면에 맞게 쉼표·마침표 기준으로 나눔 (글자 수 비율로 시각 배분)"""
    parts = re.split(r'(?<=[,.?!])\s+', text); out, cur = [], ''
    for p in parts:
        if cur and len(cur) + len(p) + 1 > maxc: out.append(cur); cur = p
        else: cur = (cur + ' ' + p).strip()
    if cur: out.append(cur)
    return out


def main():
    if '--design' in sys.argv: return design()
    redo = set(sys.argv[sys.argv.index('--redo') + 1].split(',')) if '--redo' in sys.argv else set()
    make_voices(redo)
    t, lines, order, scenes, prev, voice = LEAD, {}, [], [], None, []
    for lid, sc, sub, tts, extra in SCRIPT:
        if prev and sc != prev: t += SCENE_GAP
        if sc != prev: scenes.append({'id': sc, 'label': dict(SCENES)[sc], 'start': round(max(0, t - (SCENE_GAP * .6 if prev else LEAD)), 3)})
        x = trim(decode(line_path(tts or sub)))
        d = len(x) / SR
        cs = chunks(sub); tot = sum(len(c) for c in cs); ct, ch = t, []
        for c in cs: dd = d * len(c) / tot; ch.append({'text': c, 'start': round(ct, 3), 'end': round(ct + dd, 3)}); ct += dd
        lines[lid] = {'scene': sc, 'text': sub, 'start': round(t, 3), 'end': round(t + d, 3), 'chunks': ch}
        order.append(lid); voice.append((t, x)); t += d + GAP + extra; prev = sc
    dur = round(t + .4, 2)
    for i, s in enumerate(scenes): s['end'] = scenes[i + 1]['start'] if i + 1 < len(scenes) else dur
    cues = []
    for lid, at, name, g in SFX:
        L = lines[lid]; tt = L['end'] + float(at[1:]) if isinstance(at, str) else L['start'] + (L['end'] - L['start']) * at
        cues.append({'line': lid, 'at': at, 't': round(tt, 3), 'name': name, 'g': g})
    for sc in scenes[1:]: cues.append({'line': None, 'at': 'scene', 't': round(sc['start'] + .05, 3), 'name': 'swish', 'g': .5})   # 장면 전환 (화면의 동그란 와이프와 같은 때)
    # 믹스: 내레이션 + 효과음 + 배경음(말할 때 더 작게)
    n = int(dur * SR); vo, fx = np.zeros(n), np.zeros(n)
    for st, x in voice: mix_at(vo, x, st)
    for c in cues: mix_at(fx, sfx(c['name']), c['t'], c['g'] * .55)
    talk = np.zeros(n)
    for L in lines.values(): talk[int((L['start'] - .2) * SR):int((L['end'] + .25) * SR)] = 1
    k = int(.25 * SR); duck = np.convolve(talk, np.ones(k) / k, 'same')
    music = bgm(dur) * (1 - .55 * duck) * .55
    fade = np.ones(n); fade[-int(2.5 * SR):] = np.linspace(1, 0, int(2.5 * SR))
    m = (vo * .95 + fx + music * fade)
    m = m / np.abs(m).max() * .89   # 최고 -1 dBFS 에 맞춤
    with wave.open(os.path.join(AUD, 'mix.wav'), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype('<i2').tobytes())
    tl = {'duration': dur, 'scenes': scenes, 'order': order, 'lines': lines, 'sfx': cues}
    open(os.path.join(ROOT, 'timeline.js'), 'w').write('// written by tools/make_audio.py (timing from the real narration length). Do not edit by hand — rerun make_audio.py\nwindow.TL = ' + json.dumps(tl, ensure_ascii=False) + ';\n')
    print(f'완료: {dur:.1f}s, 문장 {len(order)}개 → timeline.js, audio/mix.wav')


if __name__ == '__main__':
    main()
