"""지우의 형아 되기 — 대사 음성·효과음·배경음 만들기

- 목소리: Qwen3-TTS (Alibaba Qwen, Apache 2.0)
  1) VoiceDesign 모델로 캐릭터마다 기준 목소리를 한 번 지어냄 (설명: VOICES)
  2) Base 모델로 그 기준 목소리를 복제해 모든 대사를 읽음 → 한 캐릭터의 목소리가 장면마다 같음
- 대사마다 실제 길이로 시각을 정해 ../timeline.js 를 씀 (입 모양용 소리 크기 곡선 env 포함) → 화면(index.html)이 따라 움직임
- 효과음·배경음(오르골)은 numpy 로 합성

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
    'narr':  ('따뜻하고 부드러운 30대 한국 여성 동화 구연가의 목소리. 차분하고 다정하게, 또박또박 읽어 줌.', '옛날 옛날에, 작은 마을에 마음씨 고운 아이가 살았어요.'),
    'jiwoo': ('여섯 살 한국 남자아이의 밝고 귀여운 목소리. 높고 맑은 어린아이 음색, 씩씩하고 신나게.', '엄마, 이거 봐요! 내가 혼자서 블록을 이만큼 높이 쌓았어요!'),
    'mom':   ('상냥하고 다정한 30대 한국 엄마의 부드럽고 따뜻한 목소리.', '우리 지우 잘 잤어? 엄마가 맛있는 아침 만들어 줄게.'),
    'dad':   ('자상하고 차분한 30대 한국 아빠의 낮고 따뜻한 남성 목소리.', '지우야, 오늘은 아빠랑 같이 공원에 산책 갈까?'),
    'fairy': ('반짝반짝 맑고 높은 목소리의 장난스럽고 신비로운 꼬마 요정. 경쾌하고 사랑스러운 여자아이 목소리.', '안녕! 나는 반짝반짝 별나라에서 날아온 꿈별 요정이야!'),
    'baby':  ('돌이 안 된 아주 어린 아기의 옹알이와 울음소리.', '응애, 응애! 으앙, 아앙!'),
}
NAMES = {'narr': '', 'jiwoo': '지우', 'mom': '엄마', 'dad': '아빠', 'fairy': '꿈별 요정', 'baby': '동생', 'babyj': '아기 지우'}

SCENES = [('home', '바쁜 엄마 아빠'), ('night', '꿈별 요정'), ('baby', '아기가 된 지우'), ('back', '요정과 다시'), ('home2', '형아가 된 지우'), ('end', '끝')]
# (id, 장면, 말하는 사람, 대사, 뒤에 더 쉴 시간)
SCRIPT = [
    ('n1', 'home', 'narr', '지우네 집에 아기 동생이 태어났어요.', .2),
    ('n2', 'home', 'narr', '엄마 아빠는 하루 종일 아기를 돌보느라 바빴지요.', .3),
    ('j1', 'home', 'jiwoo', '엄마! 나랑 블록 놀이 하자!', 0),
    ('m1', 'home', 'mom', '지우야, 잠깐만. 아기 우유 먹이는 중이야.', .1),
    ('j2', 'home', 'jiwoo', '그럼 아빠! 아빠, 같이 놀아요!', 0),
    ('d1', 'home', 'dad', '미안해, 지우야. 아기 기저귀부터 갈아 줄게. 조금만 기다려 줄래?', .4),
    ('j3', 'home', 'jiwoo', '칫, 맨날 아기만 좋아해...', .3),
    ('j4', 'home', 'jiwoo', '나도 아기가 되면 좋겠다!', .6),

    ('n3', 'night', 'narr', '그날 밤, 지우 방에 반짝반짝 빛이 나타났어요.', .5),
    ('f1', 'night', 'fairy', '안녕, 지우야! 나는 꿈별 요정이야.', .1),
    ('f2', 'night', 'fairy', '아기가 되고 싶다고? 내가 소원을 들어줄게!', 0),
    ('j5', 'night', 'jiwoo', '정말요? 우와, 좋아요!', .2),
    ('f3', 'night', 'fairy', '반짝반짝, 아기가 되어라! 얍!', 1.2),

    ('n4', 'baby', 'narr', '다음 날 아침, 지우는 정말 아기가 되었어요.', .2),
    ('j6', 'baby', 'jiwoo', '와, 나 아기가 됐다! 이제 엄마 아빠가 나만 봐 주겠지?', .3),
    ('j7', 'baby', 'jiwoo', '배고파. 엄마, 나 과자 주세요!', 0),
    ('b1', 'baby', 'babyj', '응애! 응애!', .1),
    ('n5', 'baby', 'narr', '그런데 말은 안 나오고 울음만 나왔어요.', .1),
    ('m2', 'baby', 'mom', '우리 아기 배고프구나? 우유 먹자.', .1),
    ('j8', 'baby', 'jiwoo', '우유 말고 과자 먹고 싶은데...', .5),
    ('j9', 'baby', 'jiwoo', '저기 블록이다! 가서 놀아야지.', .1),
    ('n6', 'baby', 'narr', '하지만 걸을 수가 없어서 엉금엉금 기어야 했어요.', .2),
    ('j10', 'baby', 'jiwoo', '아이고, 다리가 말을 안 들어!', .5),
    ('b2', 'baby', 'babyj', '으앙!', .2),
    ('d2', 'baby', 'dad', '아이쿠, 넘어졌네. 이제 낮잠 잘 시간이야.', .1),
    ('j11', 'baby', 'jiwoo', '싫어요, 안 졸려요! 나도 밖에 나가서 놀고 싶단 말이에요!', .2),
    ('n7', 'baby', 'narr', '아기 지우는 아무것도 마음대로 할 수가 없었어요.', .2),
    ('j12', 'baby', 'jiwoo', '아기는 하나도 안 좋아... 다시 형아가 되고 싶어!', .6),

    ('f4', 'back', 'fairy', '지우야, 아기가 되어 보니 어때?', .1),
    ('j13', 'back', 'jiwoo', '아기는 힘든 게 정말 많아요. 말도 못 하고, 걷지도 못하고요.', .1),
    ('j14', 'back', 'jiwoo', '동생도 많이 힘들었겠다...', .2),
    ('f5', 'back', 'fairy', '그걸 알았으니, 이제 멋진 형아로 돌아가자! 얍!', 1.2),

    ('n8', 'home2', 'narr', '눈을 떠 보니, 지우는 다시 형아가 되어 있었어요.', .2),
    ('b3', 'home2', 'baby', '응애, 응애!', .1),
    ('j15', 'home2', 'jiwoo', '동생이 운다! 울지 마, 형아가 놀아 줄게.', .2),
    ('j16', 'home2', 'jiwoo', '까꿍! 까꿍!', .1),
    ('b4', 'home2', 'baby', '까르르, 꺄르르!', .3),
    ('m3', 'home2', 'mom', '우와, 우리 지우가 동생을 웃게 했네! 고마워, 지우야.', .1),
    ('d3', 'home2', 'dad', '지우는 정말 멋진 형아구나. 이제 다 같이 블록 놀이 할까?', .1),
    ('j17', 'home2', 'jiwoo', '좋아요! 동생아, 형아가 많이 사랑해!', .5),

    ('n9', 'end', 'narr', '지우는 동생을 아끼는 멋진 형아가 되었답니다.', 1.5),
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

def make_voices():
    import torch
    from qwen_tts import Qwen3TTSModel
    torch.set_num_threads(os.cpu_count() or 4)
    os.makedirs(CACHE, exist_ok=True)
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    refs = {k: os.path.join(CACHE, 'ref_' + h(k, *v) + '.wav') for k, v in VOICES.items()}
    if any(not os.path.exists(f) for f in refs.values()):          # 1) 기준 목소리 지어내기
        d = os.environ.get('QWEN_DESIGN_DIR') or sys.exit('QWEN_DESIGN_DIR 에 VoiceDesign 모델 폴더를 지정하세요.')
        m = Qwen3TTSModel.from_pretrained(d, device_map=dev, dtype=torch.bfloat16)
        for k, (desc, text) in VOICES.items():
            if os.path.exists(refs[k]): continue
            torch.manual_seed(7)
            w, sr = m.generate_voice_design(text=text, language='Korean', instruct=desc)
            sf.write(refs[k], w[0], sr); print(f'  기준 목소리: {k}')
        del m
    need = [(lid, sp, tx) for lid, _, sp, tx, _ in SCRIPT if not os.path.exists(line_path(sp, tx))]
    if need:                                                          # 2) 기준 목소리로 대사 읽기
        b = os.environ.get('QWEN_BASE_DIR') or sys.exit('QWEN_BASE_DIR 에 Base 모델 폴더를 지정하세요.')
        m = Qwen3TTSModel.from_pretrained(b, device_map=dev, dtype=torch.bfloat16)
        prompts = {}
        for lid, sp, tx in need:
            vk = 'baby' if sp in ('baby', 'babyj') else sp
            if vk not in prompts: prompts[vk] = m.create_voice_clone_prompt(ref_audio=refs[vk], ref_text=VOICES[vk][1])
            torch.manual_seed(11)
            w, sr = m.generate_voice_clone(text=tx, language='Korean', voice_clone_prompt=prompts[vk])
            sf.write(line_path(sp, tx), w[0], sr); print(f'  {lid} {NAMES.get(sp) or "내레이션"}: {tx}')

def line_path(sp, tx):
    vk = 'baby' if sp in ('baby', 'babyj') else sp
    return os.path.join(CACHE, h(vk, VOICES[vk][0], tx) + '.wav')

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
def thud(): tt = t_(.3); f = 120 * np.exp(-tt * 8) + 50; return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 12) * .9
def pop(f=700): tt = t_(.12); ff = np.geomspace(f * 1.8, f, len(tt)); return np.sin(2 * np.pi * np.cumsum(ff) / SR) * np.exp(-tt * 30) * .6
def rattle():
    out = np.zeros(int(.8 * SR))
    for i in range(6): d = .05; n = rs.randn(int(d * SR)); o = int(i * .12 * SR); out[o:o + len(n)] += (n - lp(n, .3)) * np.exp(-t_(d) * 50) * .5
    return out
def boing(): tt = t_(.35); f = np.geomspace(220, 660, len(tt)); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 6) * .5
def musicbox(dur, mood):
    # 오르골 아르페지오. mood: 'day' 밝게, 'night' 고요하게, 'sad' 단조
    prog = {'day': [[261.63, 329.63, 392.0], [220.0, 261.63, 329.63], [174.61, 220.0, 261.63], [196.0, 246.94, 293.66]],
            'night': [[220.0, 261.63, 329.63], [174.61, 220.0, 261.63], [196.0, 246.94, 293.66], [164.81, 196.0, 246.94]],
            'sad': [[220.0, 261.63, 329.63], [196.0, 233.08, 293.66], [174.61, 220.0, 261.63], [164.81, 207.65, 246.94]]}[mood]
    beat = .36 if mood == 'day' else .5
    out = np.zeros(int(dur * SR) + SR); t, k = 0.0, 0
    while t < dur:
        ch = prog[(k // 8) % 4]; f = [ch[0], ch[1], ch[2], ch[1] * 2, ch[2] * 2, ch[1] * 2, ch[2], ch[1]][k % 8] * 2
        x = bell(f, 1.4, .18); o = int(t * SR); out[o:o + len(x)] += x[:len(out) - o]
        t += beat; k += 1
    return out[:int(dur * SR)]

def place(buf, t, x, g=1.0):
    o = int(t * SR)
    if o >= len(buf) or o < 0: return
    n = min(len(x), len(buf) - o); buf[o:o + n] += x[:n] * g

def main():
    make_voices()
    t, prev, lines, order, scene_t, voice = 1.6, None, {}, [], {}, {}
    for lid, sc, sp, tx, extra in SCRIPT:
        if prev and sc != prev: t += SCENE_GAP
        if sc not in scene_t: scene_t[sc] = t - (1.0 if sc != 'home' else 1.6)
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
    N = int(dur * SR); nar = np.zeros(N); fx = np.zeros(N); mus = np.zeros(N)
    for lid, (st, x) in voice.items(): place(nar, st, x)
    L = lambda k: lines[k]; S = {s['id']: s for s in scenes}
    for s in scenes[1:]: place(fx, s['start'] - .2, whoosh(.8), .5)
    place(fx, L('n3')['start'] + .6, sparkle(10, 1046.5), .8)            # 요정 등장
    place(fx, L('f3')['end'] + .05, sparkle(14, 1568, .045), 1.0)         # 아기가 되어라
    place(fx, L('f3')['end'] + .2, whoosh(1.2), .6)
    place(fx, L('j10')['end'] + .15, thud(), .9)                           # 콩 넘어짐
    for k in ('j9', 'n6'): place(fx, L(k)['start'] + .3, pop(500), .3)
    place(fx, L('f4')['start'] - .6, sparkle(8, 1318.5), .7)
    place(fx, L('f5')['end'] + .05, sparkle(14, 1046.5, .045), 1.0)
    place(fx, L('j16')['start'] - .3, rattle(), .8)                         # 딸랑이
    place(fx, L('b4')['start'] - .05, boing(), .4)
    place(fx, L('n9')['start'] - .2, sparkle(8, 1568), .6)
    # 배경음: 장면마다 분위기
    moods = {'home': 'day', 'night': 'night', 'baby': 'day', 'back': 'night', 'home2': 'day', 'end': 'day'}
    for s in scenes:
        mood = 'sad' if s['id'] == 'baby' else moods[s['id']]
        seg = musicbox(s['end'] - s['start'] + .5, mood); place(mus, s['start'], seg * np.minimum(1, t_(len(seg) / SR) / .4) * np.clip((len(seg) / SR - t_(len(seg) / SR)) / .5, 0, 1))
    envl = np.convolve(np.abs(nar), np.ones(int(.3 * SR)) / int(.3 * SR), 'same')
    duck = 1 - .55 * np.clip(envl / (envl.max() * .2 + 1e-9), 0, 1)
    mix = nar * 1.0 + fx * .55 + mus * .5 * duck
    mix = np.tanh(mix * .95) / .95
    mix = mix / (np.abs(mix).max() + 1e-9) * .9
    out = os.path.join(ROOT, 'audio', 'mix.wav')
    sf.write(out, np.stack([mix, mix], 1).astype(np.float32), SR, subtype='PCM_16')
    print(f'완료: {out} ({dur}초, 대사 {len(order)}줄)')

if __name__ == '__main__':
    main()
