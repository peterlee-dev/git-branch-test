"""호박공주 — 대사 음성·효과음·배경음 만들기

- 목소리: Qwen3-TTS (Alibaba Qwen, Apache 2.0)
  1) VoiceDesign 모델로 캐릭터마다 기준 목소리를 한 번 지어냄 (설명: VOICES)
  2) Base 모델로 그 기준 목소리를 복제해 모든 대사를 읽음 → 한 캐릭터의 목소리가 장면마다 같음
- 대사마다 실제 길이로 시각을 정해 ../timeline.js 를 씀 (입 모양용 소리 크기 곡선 env 포함) → 화면(index.html)이 따라 움직임
- 효과음(빗소리, 천둥, 붓질, 팡파르, 종소리)·배경음(오르골)은 numpy 로 합성

  pip install torch qwen-tts soundfile numpy
  QWEN_DESIGN_DIR=/path/Qwen3-TTS-12Hz-1.7B-VoiceDesign QWEN_BASE_DIR=/path/Qwen3-TTS-12Hz-1.7B-Base python3 tools/make_audio.py
  (만든 음성은 audio/tts_cache/ 에 남아서, 대사를 고치면 그 줄만 다시 만들어요)
"""
import os, sys, json, hashlib
import numpy as np
import soundfile as sf

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
CACHE = os.path.join(ROOT, 'audio', 'tts_cache')
GAP, SCENE_GAP = .32, 1.3

# 캐릭터 목소리: (지어낼 목소리 설명, 기준 목소리로 읽을 문장)
VOICES = {
    'narr':    ('따뜻하고 부드러운 30대 한국 여성 동화 구연가의 목소리. 차분하고 다정하게, 또박또박 읽어 줌.', '옛날 옛날에, 작은 마을에 마음씨 고운 아이가 살았어요.'),
    'pumpkin': ('수줍고 상냥한 일곱 살 한국 여자아이 공주의 귀엽고 맑은 목소리. 다정하고 사랑스럽게.', '안녕하세요, 저는 호박나라의 공주예요. 만나서 정말 반가워요!'),
    'melon':   ('상냥하고 사랑스러운 열 살 한국 소녀 공주의 높고 맑은 여자 목소리. 또랑또랑하고 명랑하게, 귀엽고 여성스러운 음색.', '반가워요, 여러분! 오늘 파티 정말 신나요!'),
    'apple':   ('씩씩하고 명랑한 열 살 한국 남자아이 왕자의 힘찬 목소리. 신나고 또랑또랑하게.', '안녕! 나는 사과나라의 사과 왕자야. 같이 놀자!'),
    'grape':   ('부드럽고 느긋한 열 살 한국 남자아이 왕자의 다정한 목소리. 살짝 장난스럽게.', '안녕하세요, 포도나라에서 온 포도 왕자예요. 반가워요.'),
    'banana':  ('익살스럽고 장난꾸러기 같은 여덟 살 한국 남자아이 목소리. 키득키득 웃으며 장난치는 말투.', '헤헤, 나는 바나나야! 미끌미끌 재미있지?'),
    'berry':   ('새침하고 톡톡 튀는 여덟 살 한국 여자아이 목소리. 장난스럽고 깜찍한 말투.', '나는 딸기야! 빨갛고 상큼하지? 히히!'),
    'durian':  ('다정하고 부드러운 20대 한국 청년 왕자의 따뜻하고 차분한 목소리. 듬직하고 친절하게.', '안녕하세요, 공주님. 오늘 날씨가 참 좋네요.'),
}
NAMES = {'narr': '', 'pumpkin': '호박공주', 'melon': '수박공주', 'apple': '사과 왕자', 'grape': '포도 왕자', 'banana': '바나나', 'berry': '딸기', 'durian': '두리안 왕자'}

SCENES = [('castle', '호박나라'), ('party', '파티'), ('paint', '줄무늬 그리기'), ('stripes', '줄무늬 공주'), ('rain', '비'), ('durian', '두리안 왕자'), ('wedding', '결혼식')]
# (id, 장면, 말하는 사람, 대사, 뒤에 더 쉴 시간)
SCRIPT = [
    ('n1', 'castle', 'narr', '옛날 옛날, 동글동글 호박나라에 호박공주님이 살고 있었어요.', .2),
    ('p1', 'castle', 'pumpkin', '오늘은 내가 파티를 여는 날이야! 친구들이 많이 와 주면 좋겠다.', .2),
    ('n2', 'castle', 'narr', '호박공주님은 과일 나라 친구들을 모두 성의 정원으로 초대했어요.', .6),

    ('n3', 'party', 'narr', '파티가 시작되자 사과 왕자님, 포도 왕자님, 바나나와 딸기도 찾아왔어요.', .2),
    ('p2', 'party', 'pumpkin', '어서 와요! 달콤한 호박 파이도 많이 있어요.', .3),
    ('n4', 'party', 'narr', '그때, 옆 나라 수박공주님이 도착했어요.', .5),
    ('w1', 'party', 'melon', '안녕하세요! 저는 수박나라에서 온 수박공주예요.', .1),
    ('a1', 'party', 'apple', '우와, 초록색 줄무늬가 정말 멋져요!', 0),
    ('g1', 'party', 'grape', '수박공주님, 저랑 춤춰요!', 0),
    ('b1', 'party', 'banana', '저는 수박공주님 옆에 앉을래요!', .2),
    ('n5', 'party', 'narr', '친구들은 모두 수박공주님 곁으로 몰려갔어요.', .3),
    ('p3', 'party', 'pumpkin', '다들 수박공주님만 좋아하네...', .3),
    ('p4', 'party', 'pumpkin', '나도 수박공주님처럼 줄무늬가 있으면 좋겠다.', .6),

    ('n6', 'paint', 'narr', '호박공주님은 몰래 방으로 들어가 붓을 들었어요.', .2),
    ('p5', 'paint', 'pumpkin', '쓱쓱, 싹싹! 초록색 줄무늬를 그려야지.', 1.0),
    ('p6', 'paint', 'pumpkin', '짜잔! 이제 나도 수박공주님 같아!', .6),

    ('n7', 'stripes', 'narr', '줄무늬를 그린 호박공주님이 다시 정원에 나타나자,', .1),
    ('a2', 'stripes', 'apple', '와, 저 멋진 공주님은 누구지?', 0),
    ('g2', 'stripes', 'grape', '줄무늬 공주님, 저랑 춤춰요!', .1),
    ('n8', 'stripes', 'narr', '멋진 왕자님들이 호박공주님 곁으로 몰려왔어요.', .1),
    ('p7', 'stripes', 'pumpkin', '호호, 정말요? 좋아요!', .8),

    ('n9', 'rain', 'narr', '그런데 그때, 갑자기 하늘에서 비가 쏟아졌어요.', .2),
    ('p8', 'rain', 'pumpkin', '어머, 비가 와! 안 돼!', .3),
    ('n10', 'rain', 'narr', '빗물에 호박공주님의 줄무늬가 주르륵 지워지고 말았어요.', .4),
    ('s1', 'rain', 'berry', '어? 줄무늬가 지워졌다! 호박공주님이었잖아!', 0),
    ('b2', 'rain', 'banana', '하하! 호박에 줄 긋는다고 수박 되나?', 0),
    ('s2', 'rain', 'berry', '호박에 줄 긋는다고 수박 되나? 히히!', .3),
    ('p9', 'rain', 'pumpkin', '흑흑... 너무 창피해.', .3),
    ('n11', 'rain', 'narr', '호박공주님은 너무 슬퍼서 정원 구석에 쪼그려 앉아 울었어요.', .6),

    ('n12', 'durian', 'narr', '그때, 누군가 다가와 우산을 씌워 주었어요.', .2),
    ('d1', 'durian', 'durian', '공주님, 슬퍼하지 마세요.', .2),
    ('p10', 'durian', 'pumpkin', '누구... 세요?', .1),
    ('d2', 'durian', 'durian', '저는 두리안 나라의 두리안 왕자예요. 가시가 뾰족해서 다들 저를 피하지만요.', .2),
    ('d3', 'durian', 'durian', '공주님은 줄을 긋지 않아도 아름다워요. 동글동글 주황빛 그대로 정말 예뻐요.', .2),
    ('p11', 'durian', 'pumpkin', '정말요? 있는 그대로의 내가 예쁘다고요?', .1),
    ('d4', 'durian', 'durian', '그럼요. 웃는 얼굴이 해님처럼 환하답니다.', .3),
    ('p12', 'durian', 'pumpkin', '고마워요, 두리안 왕자님!', .3),
    ('n13', 'durian', 'narr', '어느새 비가 그치고, 하늘에 커다란 무지개가 떴어요.', .6),

    ('n14', 'wedding', 'narr', '호박공주님과 두리안 왕자님은 결혼을 했어요.', .2),
    ('w2', 'wedding', 'melon', '호박공주님, 결혼 축하해요! 정말 예뻐요!', .2),
    ('n15', 'wedding', 'narr', '그리고 오래오래 행복하게 살았답니다.', 1.8),
]

# ---------------------------------------------------------------- TTS
def trim(x, thr=.008):
    idx = np.where(np.abs(x) > thr)[0]
    if len(idx) == 0: return x
    return x[max(0, idx[0] - int(.03 * SR)): min(len(x), idx[-1] + int(.1 * SR))]

def resample(x, sr):
    if sr == SR: return x.astype(np.float32)
    n = int(len(x) * SR / sr)
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)

def h(*a): return hashlib.sha1('|'.join(a).encode()).hexdigest()[:16]

def line_path(sp, tx): return os.path.join(CACHE, h(sp, VOICES[sp][0], tx) + '.wav')

def make_voices():
    os.makedirs(CACHE, exist_ok=True)
    refs = {k: os.path.join(CACHE, 'ref_' + h(k, *v) + '.wav') for k, v in VOICES.items()}
    need = [(lid, sp, tx) for lid, _, sp, tx, _ in SCRIPT if not os.path.exists(line_path(sp, tx))]
    if not need and all(os.path.exists(f) for f in refs.values()): return
    import torch
    from qwen_tts import Qwen3TTSModel
    torch.set_num_threads(os.cpu_count() or 4)
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    if any(not os.path.exists(f) for f in refs.values()):          # 1) 기준 목소리 지어내기
        d = os.environ.get('QWEN_DESIGN_DIR') or sys.exit('QWEN_DESIGN_DIR 에 VoiceDesign 모델 폴더를 지정하세요.')
        m = Qwen3TTSModel.from_pretrained(d, device_map=dev, dtype=torch.bfloat16)
        for k, (desc, text) in VOICES.items():
            if os.path.exists(refs[k]): continue
            torch.manual_seed(7)
            w, sr = m.generate_voice_design(text=text, language='Korean', instruct=desc)
            sf.write(refs[k], w[0], sr); print(f'  기준 목소리: {k}', flush=True)
        del m
    if need:                                                          # 2) 기준 목소리로 대사 읽기
        b = os.environ.get('QWEN_BASE_DIR') or sys.exit('QWEN_BASE_DIR 에 Base 모델 폴더를 지정하세요.')
        m = Qwen3TTSModel.from_pretrained(b, device_map=dev, dtype=torch.bfloat16)
        prompts = {}
        for lid, sp, tx in need:
            if sp not in prompts: prompts[sp] = m.create_voice_clone_prompt(ref_audio=refs[sp], ref_text=VOICES[sp][1])
            torch.manual_seed(11)
            w, sr = m.generate_voice_clone(text=tx, language='Korean', voice_clone_prompt=prompts[sp])
            sf.write(line_path(sp, tx), w[0], sr); print(f'  {lid} {NAMES.get(sp) or "내레이션"}: {tx}', flush=True)

def load_line(sp, tx):
    x, sr = sf.read(line_path(sp, tx), dtype='float32')
    if x.ndim > 1: x = x.mean(1)
    return trim(resample(x, sr))

# ---------------------------------------------------------------- 효과음·배경음
t_ = lambda d: np.arange(int(d * SR)) / SR
rs = np.random.RandomState(5)
def lp(x, a):
    y = np.zeros_like(x); acc = 0.0
    for i in range(len(x)): acc += a * (x[i] - acc); y[i] = acc
    return y
def bell(f, d=1.2, g=.5): tt = t_(d); return (np.sin(2 * np.pi * f * tt) + .3 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt * 6)) * np.exp(-tt * 3.5) * g
def sparkle(n=8, base=1318.5, step=.06):
    out = np.zeros(int((n * step + 1.2) * SR)); scale = [1, 1.122, 1.26, 1.498, 1.682, 2, 2.245, 2.52]
    for i in range(n): x = bell(base * scale[i % 8], 1.0, .22); o = int(i * step * SR); out[o:o + len(x)] += x
    return out
def whoosh(d=.7):
    n = rs.randn(int(d * SR)); e = np.sin(np.pi * np.linspace(0, 1, len(n))) ** 2
    return (lp(n, .06) * 3) * e * .5
def pop(f=700): tt = t_(.12); ff = np.geomspace(f * 1.8, f, len(tt)); return np.sin(2 * np.pi * np.cumsum(ff) / SR) * np.exp(-tt * 30) * .6
def brush(d=.35):   # 붓질 쓱
    n = rs.randn(int(d * SR)); hp = n - lp(n, .2); e = np.sin(np.pi * np.linspace(0, 1, len(n))) ** 1.5
    return lp(hp, .5) * e * .5
def horn(f, d):     # 팡파르 나팔 (톱니파 + 부드러운 필터)
    tt = t_(d); ph = (f * tt) % 1; x = (2 * ph - 1) * .6 + np.sin(2 * np.pi * f * tt) * .4
    return lp(x, .25) * np.minimum(1, tt / .03) * np.clip((d - tt) / .08, 0, 1) * .45
def fanfare():
    out = np.zeros(int(1.6 * SR))
    for st, f, d in [(0, 523.25, .16), (.18, 523.25, .16), (.36, 523.25, .16), (.54, 659.25, .3), (.86, 783.99, .6)]:
        x = horn(f, d) + horn(f * 1.26, d) * .5; o = int(st * SR); out[o:o + len(x)] += x
    return out
def rain(d):        # 빗소리: 쏴아 + 톡톡 빗방울
    n = rs.randn(int(d * SR)); base = lp(n - lp(n, .05), .35) * .35
    drops = np.zeros_like(n)
    for _ in range(int(d * 40)):
        o = rs.randint(0, len(n) - 2000); f = rs.uniform(1800, 4200); tt = t_(.03)
        drops[o:o + len(tt)] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 160) * rs.uniform(.1, .35)
    return base + drops
def thunder(d=2.4):
    n = rs.randn(int(d * SR)); x = lp(lp(n, .01), .02) * 40; tt = t_(d)
    return x * (np.exp(-tt * 1.6) * (1 + .6 * np.sin(2 * np.pi * 3 * tt) ** 2)) * .5
def chime(): return sparkle(10, 1046.5, .05)
def wedding_bells(d=4.0):
    out = np.zeros(int(d * SR) + SR)
    for i, f in enumerate([783.99, 659.25, 523.25, 392.0, 523.25, 659.25, 783.99, 1046.5]):
        x = bell(f, 1.6, .35); x[:int(1.0 * SR)] += bell(f * 2, 1.0, .1); o = int(i * .42 * SR); out[o:o + len(x)] += x
    return out[:int(d * SR)]
def giggle():       # 놀리는 키득 (짧은 높은 음 몇 번)
    out = np.zeros(int(.7 * SR))
    for i in range(5): tt = t_(.07); f = 900 + i * 60; x = np.sin(2 * np.pi * f * tt) * np.sin(np.pi * tt / .07); o = int(i * .12 * SR); out[o:o + len(x)] += x * .25
    return out
def musicbox(dur, mood):
    # 오르골 아르페지오. mood: 'day' 밝게, 'waltz' 파티 왈츠, 'sad' 단조, 'wedding' 환하게
    prog = {'day': [[261.63, 329.63, 392.0], [220.0, 261.63, 329.63], [174.61, 220.0, 261.63], [196.0, 246.94, 293.66]],
            'waltz': [[293.66, 369.99, 440.0], [246.94, 293.66, 369.99], [196.0, 246.94, 293.66], [220.0, 277.18, 329.63]],
            'sad': [[220.0, 261.63, 329.63], [196.0, 233.08, 293.66], [174.61, 220.0, 261.63], [164.81, 207.65, 246.94]],
            'wedding': [[261.63, 329.63, 392.0], [174.61, 220.0, 261.63], [196.0, 246.94, 293.66], [261.63, 329.63, 392.0]]}[mood]
    beat = {'day': .36, 'waltz': .3, 'sad': .55, 'wedding': .34}[mood]
    pat = [0, 1, 2, 1, 2, 1] if mood == 'waltz' else [0, 1, 2, 3, 4, 3, 2, 1]
    out = np.zeros(int(dur * SR) + 2 * SR); t, k = 0.0, 0
    while t < dur:
        ch = prog[(k // len(pat)) % 4]; notes = [ch[0], ch[1], ch[2], ch[1] * 2, ch[2] * 2]
        f = notes[pat[k % len(pat)]] * 2
        x = bell(f, 1.4, .18 if pat[k % len(pat)] else .24); o = int(t * SR); out[o:o + len(x)] += x[:len(out) - o]
        t += beat; k += 1
    return out[:int(dur * SR)]

def place(buf, t, x, g=1.0):
    o = int(t * SR)
    if o >= len(buf) or o < 0: return
    n = min(len(x), len(buf) - o); buf[o:o + n] += x[:n] * g

def main():
    make_voices()
    t, prev, lines, order, scene_t, voice = 2.2, None, {}, [], {}, {}
    for lid, sc, sp, tx, extra in SCRIPT:
        if prev and sc != prev: t += SCENE_GAP
        if sc not in scene_t: scene_t[sc] = t - (1.0 if prev else 2.2)
        x = load_line(sp, tx); d = len(x) / SR; voice[lid] = (t, x)
        hop = SR // 30; env = [float(np.sqrt(np.mean(x[i:i + hop] ** 2))) for i in range(0, len(x), hop)]
        mx = max(env) + 1e-9; env = [round(min(1, v / mx * 1.4), 2) for v in env]   # 입 벌림 0~1 (30fps)
        lines[lid] = {'text': tx, 'who': sp, 'name': NAMES.get(sp, ''), 'start': round(t, 3), 'end': round(t + d, 3), 'scene': sc, 'env': env}
        order.append(lid); t += d + GAP + extra; prev = sc
    dur = round(t + .4, 2)
    ids = [s for s, _ in SCENES]
    scenes = [{'id': s, 'label': lab, 'start': round(max(0, scene_t[s]), 3), 'end': round(scene_t[ids[i + 1]] if i + 1 < len(ids) else dur, 3)} for i, (s, lab) in enumerate(SCENES)]
    TL = {'duration': dur, 'scenes': scenes, 'lines': lines, 'order': order}
    with open(os.path.join(ROOT, 'timeline.js'), 'w', encoding='utf-8') as f:
        f.write('// make_audio.py 가 만든 시각표 (대사 실제 길이 기준, env = 입 모양용 소리 크기 30fps). 손으로 고치지 말고 make_audio.py 를 다시 실행하세요\n')
        f.write('window.TL = ' + json.dumps(TL, ensure_ascii=False) + ';\n')
    N = int(dur * SR); nar = np.zeros(N); fx = np.zeros(N); mus = np.zeros(N); amb = np.zeros(N)
    for lid, (st, x) in voice.items(): place(nar, st, x)
    L = lambda k: lines[k]; S = {s['id']: s for s in scenes}
    for s in scenes[1:]: place(fx, s['start'] - .2, whoosh(.8), .45)
    place(fx, .3, chime(), .6)                                             # 제목
    place(fx, L('n4')['end'] + .05, fanfare(), .9)                         # 수박공주 도착
    for i in range(8): place(fx, L('p5')['start'] + .1 + i * .42, brush(), .9)   # 붓질
    place(fx, L('p6')['start'] - .1, sparkle(12, 1318.5, .045), .9)        # 짜잔
    place(fx, L('a2')['start'] - .4, sparkle(8, 1568), .6)
    rs0, re0 = L('n9')['start'] - .4, S['durian']['end'] - 0
    rr_ = rain(re0 - rs0); fade = np.minimum(1, t_(len(rr_) / SR) / 1.2) * np.clip((len(rr_) / SR - t_(len(rr_) / SR)) / 2.5, 0, 1)
    # 두리안 왕자 장면 끝(무지개) 쯤엔 빗소리가 잦아들게
    stop = L('n13')['start'] - rs0; fade *= np.clip((stop + 1.5 - t_(len(rr_) / SR)) / 2.5, 0, 1)
    place(amb, rs0, rr_ * fade, 1.0)                                       # 빗소리는 따로 작게, 대사 나올 땐 더 줄임
    place(fx, S['rain']['start'] + .05, thunder(), .5)                     # 천둥은 대사 전에
    place(fx, L('b2')['end'] - .2, giggle(), .7)
    place(fx, L('s2')['end'] - .2, giggle(), .7)
    place(fx, L('n12')['start'] + 1.2, pop(420), .5)                      # 우산 펼침
    place(fx, L('n13')['start'] + .6, sparkle(14, 1046.5, .06), .8)        # 무지개
    place(fx, S['wedding']['start'] + .3, wedding_bells(), .9)
    place(fx, L('n15')['end'] + .1, sparkle(10, 1318.5), .6)
    moods = {'castle': 'day', 'party': 'waltz', 'paint': 'day', 'stripes': 'waltz', 'rain': 'sad', 'durian': 'sad', 'wedding': 'wedding'}
    for s in scenes:
        seg = musicbox(s['end'] - s['start'] + .5, moods[s['id']])
        if s['id'] == 'durian':   # 무지개부터 밝아지게
            k = L('n13')['start'] - s['start']; seg2 = musicbox(len(seg) / SR, 'day'); tt = t_(len(seg) / SR); w = np.clip((tt - k) / 1.5, 0, 1)
            seg = seg * (1 - w) + seg2 * w
        dd = len(seg) / SR
        place(mus, s['start'], seg * np.minimum(1, t_(dd) / .4) * np.clip((dd - t_(dd)) / .5, 0, 1))
    envl = np.convolve(np.abs(nar), np.ones(int(.3 * SR)) / int(.3 * SR), 'same')
    duck = 1 - .55 * np.clip(envl / (envl.max() * .2 + 1e-9), 0, 1)
    duck2 = 1 - .75 * np.clip(envl / (envl.max() * .15 + 1e-9), 0, 1)
    mix = nar * 1.0 + fx * .5 + mus * .5 * duck + amb * .035 * duck2
    mix = np.tanh(mix * .95) / .95
    mix = mix / (np.abs(mix).max() + 1e-9) * .9
    out = os.path.join(ROOT, 'audio', 'mix.wav')
    sf.write(out, np.stack([mix, mix], 1).astype(np.float32), SR, subtype='PCM_16')
    print(f'완료: {out} ({dur}초, 대사 {len(order)}줄)')

if __name__ == '__main__':
    main()
