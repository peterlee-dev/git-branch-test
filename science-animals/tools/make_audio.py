"""동물 관찰 일기 (재능스스로과학 F01) — 내레이션·효과음·배경음 만들기

교재: 재능스스로과학 F01 (동물의 몸 색깔과 생김새, 움직임, 빠르기, 살아가는 데 필요한 것)
- 내레이션: Qwen3-TTS 1.7B CustomVoice (Alibaba Qwen, Apache 2.0) 의 한국어 목소리 Sohee
  (TTS_ENGINE=supertonic 으로 예전 Supertonic 3 도 쓸 수 있음)
- 줄마다 음성을 만든 뒤 실제 길이로 시각을 정해 ../timeline.js 를 씀 → 화면(index.html)이 그 시각을 따라 움직임
- 효과음·배경음은 numpy 로 합성 (외부 음원 없음)

  pip install torch qwen-tts soundfile numpy
  QWEN_MODEL_DIR=/path/to/Qwen3-TTS-12Hz-1.7B-CustomVoice python3 tools/make_audio.py
  # 예전 목소리: pip install sherpa-onnx 후
  TTS_ENGINE=supertonic TTS_MODEL_DIR=/path/to/sherpa-onnx-supertonic-3-tts-int8-2026-05-11 python3 tools/make_audio.py
"""
import os, sys, json
import numpy as np
import soundfile as sf

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
VOICE_SID, SPEED = 1, 0.92
GAP, SCENE_GAP = 0.5, 1.2          # 줄 사이, 장면 사이 쉼(초)

SCENES = [
    ('intro', '동물 관찰 일기'),
    ('color', '1. 몸 색깔과 생김새'),
    ('move', '2. 동물의 움직임'),
    ('speed', '3. 동물의 빠르기'),
    ('need', '4. 살아가는 데 필요한 것'),
    ('end', '정리'),
]
# (id, 장면, 말할 문장, 화면 자막(없으면 말과 같음), 뒤에 더 쉴 시간)
SCRIPT = [
    ('i1', 'intro', "안녕, 친구들! 오늘은 동물 관찰 일기를 함께 써 볼 거예요.", None, 0),
    ('i2', 'intro', "동물의 몸 색깔, 움직임, 빠르기, 그리고 살아가는 데 필요한 것을 알아봐요.", None, 0.3),

    ('a1', 'color', "첫 번째, 동물의 몸 색깔과 생김새를 살펴볼까요?", None, 0.1),
    ('a2', 'color', "풀숲에 메뚜기가 숨어 있어요. 어디 있는지 찾았나요?", None, 1.6),
    ('a3', 'color', "메뚜기와 청개구리는 몸 색깔이 주위 환경의 색깔과 비슷해요.", None, 0.1),
    ('a4', 'color', "그래서 다른 동물의 눈에 잘 보이지 않아요.", None, 0.4),
    ('a5', 'color', "자벌레와 대벌레는 나뭇가지와 비슷하고,", None, 0.1),
    ('a6', 'color', "으름덩굴큰나방은 떨어진 낙엽과 비슷하게 생겼어요.", None, 0.4),
    ('a7', 'color', "이렇게 자신의 몸을 보호하기 위해 주위와 비슷하게 되어 있는 몸의 색깔을 보호색이라고 해요.", None, 0.6),
    ('a8', 'color', "고등어의 등이 푸른 것도 보호색이에요. 위에서 보면 바다색과 비슷해서 바닷새에게 잘 들키지 않거든요.", None, 0.4),

    ('b1', 'move', "두 번째, 동물들은 어떻게 움직일까요?", None, 0.2),
    ('b2', 'move', "호랑이와 기린은 다리를 이용하여 걷거나 뛰어다녀요.", None, 0.3),
    ('b3', 'move', "독수리와 잠자리는 날개를 이용하여 날아다녀요.", None, 0.3),
    ('b4', 'move', "붕어와 돌고래는 지느러미를 이용하여 헤엄쳐 다녀요.", None, 0.3),
    ('b5', 'move', "지렁이와 뱀은 기어다녀요.", None, 0.3),
    ('b6', 'move', "원숭이는 팔과 다리로 나무에 오르거나 나뭇가지 사이를 왔다 갔다 해요.", None, 0.5),

    ('c1', 'speed', "세 번째, 동물들이 달리기 시합을 해요! 누가 가장 빠를까요?", None, 3.2),
    ('c2', 'speed', "가장 빨리 달리는 동물은 치타예요.", None, 0.2),
    ('c3', 'speed', "가장 늦게 달리는 동물은 기린이에요.", None, 0.2),
    ('c4', 'speed', "캥거루는 기린보다 빠르지만, 사자보다는 느려요.", None, 0.2),
    ('c5', 'speed', "타조는 날개가 있지만 날 수 없고, 길고 튼튼한 두 다리로 빨리 달려요.", None, 0.2),
    ('c6', 'speed', "이렇게 동물마다 빠르기가 각각 달라요.", None, 0.5),
    ('c7', 'speed', "사자는 기린을 잡아먹기 위해, 기린은 사자에게 잡아먹히지 않기 위해 빨리 달려요.", None, 0.2),
    ('c8', 'speed', "동물은 적으로부터 도망치거나, 사냥을 하기 위해 빨리 달린답니다.", None, 0.5),

    ('d1', 'need', "네 번째, 동물이 살아가는 데 필요한 것은 무엇일까요?", None, 0.2),
    ('d2', 'need', "동물이 살아가려면 먹이, 물, 공기, 그리고 집이 필요해요.", None, 0.3),
    ('d3', 'need', "새는 영양분과 물을 얻기 위해 벌레를 잡아먹거나 과일을 먹어요.", None, 0.2),
    ('d4', 'need', "숨을 쉬기 위해서는 공기가 꼭 필요하고요.", None, 0.2),
    ('d5', 'need', "거미가 거미집에 사는 것처럼, 살 집이 필요한 동물도 있어요.", None, 0.5),
    ('d6', 'need', "두더지는 땅속에 굴을 파고 살아요.", None, 0.2),
    ('d7', 'need', "딱따구리는 나무에 구멍을 파서 그 안에 둥지를 만들어요.", None, 0.2),
    ('d8', 'need', "제비는 진흙과 지푸라기로 둥지를 만들고,", None, 0.1),
    ('d9', 'need', "청둥오리는 물가의 풀밭에 마른 풀을 모아 둥지를 만들어요.", None, 0.3),
    ('d10', 'need', "이렇게 동물마다 사는 집이 각각 달라요.", None, 0.4),

    ('z1', 'end', "오늘 쓴 관찰 일기를 다시 볼까요?", None, 0.2),
    ('z2', 'end', "보호색, 움직이는 방법, 빠르기, 그리고 먹이, 물, 공기, 집.", None, 0.3),
    ('z3', 'end', "스스로 관찰 끝! 참 잘했어요!", None, 1.6),
]

# ---------------------------------------------------------------- TTS
QWEN_SPEAKER = 'Sohee'      # Qwen3-TTS CustomVoice 의 한국어 여성 목소리
QWEN_INSTRUCT = '초등학생에게 과학을 설명하듯 다정하고 밝은 목소리로, 또박또박 천천히 말해 주세요.'

def load_tts():
    if os.environ.get('TTS_ENGINE') == 'jei':      # 회사 PC 에서 사내 TTS 로 만든 음성 (../tools/voicebank.py, ../tools/jei_tts.py)
        sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools')); import voicebank
        return voicebank.load(os.path.join(HERE, '..'), SR, trim, lang='ko')
    # 기본: Qwen3-TTS 1.7B CustomVoice (Apache 2.0). TTS_ENGINE=supertonic 이면 예전 Supertonic 3
    if os.environ.get('TTS_ENGINE', 'qwen') == 'qwen':
        return load_qwen()
    return load_supertonic()

def load_qwen():
    import hashlib, torch
    from qwen_tts import Qwen3TTSModel
    d = os.environ.get('QWEN_MODEL_DIR')
    if not d or not os.path.isdir(d):
        sys.exit('QWEN_MODEL_DIR 에 Qwen3-TTS-12Hz-1.7B-CustomVoice 모델 폴더를 지정하세요.')
    torch.set_num_threads(os.cpu_count() or 4)
    model = Qwen3TTSModel.from_pretrained(d, device_map='cuda' if torch.cuda.is_available() else 'cpu', dtype=torch.bfloat16)
    cache = os.path.join(ROOT, 'audio', 'tts_cache'); os.makedirs(cache, exist_ok=True)
    def say(text):
        # 같은 문장·목소리·말투면 다시 만들지 않음 (CPU 에서는 한 줄에 1분 남짓 걸림)
        key = hashlib.sha1(f'{QWEN_SPEAKER}|{QWEN_INSTRUCT}|{text}'.encode()).hexdigest()[:16]
        f = os.path.join(cache, key + '.wav')
        if not os.path.exists(f):
            torch.manual_seed(1234)
            w, sr = model.generate_custom_voice(text=text, language='Korean', speaker=QWEN_SPEAKER, instruct=QWEN_INSTRUCT)
            sf.write(f, w[0], sr)
        x, sr = sf.read(f, dtype='float32')
        n = int(len(x) * SR / sr)
        x = np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)
        return trim(x)
    return say

def load_supertonic():
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
    def say(text):
        g = s.GenerationConfig()
        g.sid, g.speed, g.num_steps, g.extra = VOICE_SID, SPEED, 8, {'lang': 'ko'}
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

# ---------------------------------------------------------------- 효과음 (종이 느낌)
t_ = lambda d: np.arange(int(d * SR)) / SR
rs = np.random.RandomState(7)
def lp(x, a):
    y = np.zeros_like(x); acc = 0.0
    for i in range(len(x)): acc += a * (x[i] - acc); y[i] = acc
    return y
def paper_swish(d=.5):      # 종이가 슥 밀려 지나가는 소리
    n = rs.randn(int(d * SR)); env = np.sin(np.pi * np.linspace(0, 1, len(n))) ** 1.5
    return (n - lp(n, .08)) * env * .22
def paper_tap():            # 종이 조각이 톡 붙는 소리
    d = .07; n = rs.randn(int(d * SR)); return lp(n, .35) * np.exp(-t_(d) * 60) * .8
def pop(f=600): d = .12; ff = np.geomspace(f * 1.7, f, int(d * SR)); return np.sin(2 * np.pi * np.cumsum(ff) / SR) * np.exp(-t_(d) * 34) * .7
def sparkle():
    out = np.zeros(int(.6 * SR))
    for k, f in enumerate([1318.5, 1760, 2093, 2637]):
        o = int(k * .06 * SR); tt = t_(.4); out[o:o + len(tt)] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 9) * .2
    return out
def marimba(f, d=.6): tt = t_(d); return (np.sin(2 * np.pi * f * tt) + .25 * np.sin(2 * np.pi * 4 * f * tt) * np.exp(-tt * 20)) * np.exp(-tt * 6) * .5
def drumroll(d):
    tt = t_(d); n = rs.randn(len(tt)); hits = (np.sin(2 * np.pi * 22 * tt) > .6).astype(float)
    return lp(n, .25) * hits * np.minimum(1, tt / .3) * .25
def whistle(): tt = t_(.35); return np.sin(2 * np.pi * (2400 + 300 * np.sin(2 * np.pi * 30 * tt)) * tt) * np.exp(-tt * 3) * .18 * np.minimum(1, tt / .02)
def chime_up():
    out = np.zeros(int(1.6 * SR))
    for k, f in enumerate([523.25, 659.25, 783.99, 1046.5]):
        o = int(k * .12 * SR); tt = t_(1.0); out[o:o + len(tt)] += marimba(f, 1.0)[:len(tt)] * .5
    return out

# ---------------------------------------------------------------- 배경음: 잔잔한 마림바 (C F G Am)
def bgm(dur):
    bpm = 92; beat = 60 / bpm
    chords = [[261.63, 329.63, 392.0], [174.61, 220.0, 261.63], [196.0, 246.94, 293.66], [220.0, 261.63, 329.63]]
    out = np.zeros(int(dur * SR) + SR * 2); cache = {}
    t, k = 0.0, 0
    while t < dur:
        ch = chords[(k // 8) % 4]; f = [ch[0], ch[2], ch[1], ch[2]][k % 4] * (2 if k % 8 >= 4 else 1)
        if f not in cache: cache[f] = marimba(f, .7)
        x = cache[f]; o = int(t * SR); out[o:o + len(x)] += x[:len(out) - o] * (.45 if k % 2 else .65)
        if k % 8 == 0:
            b = ch[0] / 2; key = ('b', b)
            if key not in cache: cache[key] = np.sin(2 * np.pi * b * t_(beat * 7.5)) * np.exp(-t_(beat * 7.5) * .6) * .5
            y = cache[key]; out[o:o + len(y)] += y[:len(out) - o]
        t += beat / 2; k += 1
    return out[:int(dur * SR)]

def place(buf, t, x, g=1.0):
    o = int(t * SR)
    if o >= len(buf) or o < 0: return
    n = min(len(x), len(buf) - o); buf[o:o + n] += x[:n] * g

def main():
    say = load_tts()
    voice, t, prev, lines, order, scene_t = {}, 1.2, None, {}, [], {}
    for lid, sc, speak, shown, extra in SCRIPT:
        if prev and sc != prev: t += SCENE_GAP
        if sc not in scene_t: scene_t[sc] = t
        print(f'  {lid}: {speak}'); x = say(speak); voice[lid] = (t, x)
        d = len(x) / SR
        lines[lid] = {'text': shown or speak, 'start': round(t, 3), 'end': round(t + d, 3), 'scene': sc}
        order.append(lid); t += d + GAP + extra; prev = sc
    dur = round(t + .6, 2)
    ids = [s for s, _ in SCENES]
    scenes = [{'id': s, 'label': lab, 'start': round(0 if i == 0 else scene_t[s] - SCENE_GAP * .5, 3),
               'end': round((scene_t[ids[i + 1]] - SCENE_GAP * .5) if i + 1 < len(ids) else dur, 3)} for i, (s, lab) in enumerate(SCENES)]
    TL = {'duration': dur, 'scenes': scenes, 'lines': lines, 'order': order}
    with open(os.path.join(ROOT, 'timeline.js'), 'w', encoding='utf-8') as f:
        f.write('// make_audio.py 가 만든 시각표 (내레이션 실제 길이 기준). 손으로 고치지 말고 make_audio.py 를 다시 실행하세요\n')
        f.write('window.TL = ' + json.dumps(TL, ensure_ascii=False, indent=1) + ';\n')

    N = int(dur * SR); nar = np.zeros(N); fx = np.zeros(N)
    for lid, (st, x) in voice.items(): place(nar, st, x)
    L = lambda k: lines[k]
    for s in scenes[1:]: place(fx, s['start'] - .1, paper_swish(), .9)          # 장면 전환 종이
    for k in ['a3', 'a5', 'a6', 'b2', 'b3', 'b4', 'b5', 'b6', 'd6', 'd7', 'd8', 'd9']: place(fx, L(k)['start'] - .1, paper_tap(), .8)
    place(fx, L('a2')['end'] + .5, sparkle(), .6)                                # 메뚜기 찾음
    place(fx, L('a7')['start'] + .3, chime_up(), .5)                             # 보호색
    place(fx, L('c1')['end'] + .05, whistle(), .8)                               # 출발
    place(fx, L('c1')['end'] + .2, drumroll(2.6), .6)
    place(fx, L('c1')['end'] + 2.9, sparkle(), .6)                               # 결승
    for i, k in enumerate(['먹이', '물', '공기', '집']): place(fx, L('d2')['start'] + .9 + i * .55, pop(560 + i * 90), .5)
    place(fx, L('z3')['start'] - .1, chime_up(), .7)
    music = bgm(dur)
    env = np.convolve(np.abs(nar), np.ones(int(.25 * SR)) / int(.25 * SR), 'same')
    duck = 1 - .45 * np.clip(env / (env.max() * .25 + 1e-9), 0, 1)
    mix = nar + fx * .8 + music * .08 * duck
    mix = np.tanh(mix * .9) / .9
    mix = mix / (np.abs(mix).max() + 1e-9) * .89
    out = os.path.join(ROOT, 'audio', 'mix.wav'); os.makedirs(os.path.dirname(out), exist_ok=True)
    sf.write(out, np.stack([mix, mix], 1).astype(np.float32), SR, subtype='PCM_16')
    print(f'완료: {out} ({dur}초, 줄 {len(order)}개)')

if __name__ == '__main__':
    main()
