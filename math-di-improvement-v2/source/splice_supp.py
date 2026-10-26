"""수정 2(2026-10-22): supp 장면 둘째 문장만 새로 만든 음성으로 바꿔 끼운다.

새 문장 음성은 DGX 에서 처음 TTS 와 같은 방식(같은 참조 음성, 후보 → Whisper 검수 → 화자 유사도 선택, 1.05배속)으로 만들었다.
  source/supp_new.wav  : 고른 후보(24 kHz, 1.05배속 적용)
  source/supp_new.json : 후보 목록과 고른 후보의 단어 타임스탬프
di_tts.wav 의 옛 문장("…download, print, and provide the appropriate materials.") 소리 구간을 새 음성으로 바꾸고,
di_tts_words.json 의 단어도 바꾼 뒤 뒤쪽 단어 시각을 길이 차만큼 민다. 원본은 *_orig 로 한 번만 남긴다.
실행: python3 source/splice_supp.py && python3 build_audio.py
"""
import json, os, shutil, subprocess, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WAV, WORDS = os.path.join(HERE, "di_tts.wav"), os.path.join(HERE, "di_tts_words.json")
NEW, NEW_JSON = os.path.join(HERE, "supp_new.wav"), os.path.join(HERE, "supp_new.json")
SR = 48000
OLD_FIRST, OLD_LAST = 150.18, 157.48   # 옛 문장 "When" 시작, "materials." 시작(받아쓰기)
SIL_DB = -45

ff = os.path.join(HERE, "..", "node_modules", "ffmpeg-static", "ffmpeg")
for p in (WAV, WORDS):
    root, ext = os.path.splitext(p)
    if not os.path.exists(root + "_orig" + ext):
        shutil.copy(p, root + "_orig" + ext)
WAV_SRC, WORDS_SRC = os.path.join(HERE, "di_tts_orig.wav"), os.path.join(HERE, "di_tts_words_orig.json")

def load(path):
    raw = subprocess.run([ff, "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()

audio, clip = load(WAV_SRC), load(NEW)
win = SR // 100
db = lambda x: 20 * np.log10(np.sqrt((x[:len(x) // win * win].reshape(-1, win) ** 2).mean(1)) + 1e-9)
d = db(audio)
f = int(OLD_FIRST * 100) - 30                      # 앞 문장 "set." 끝 → 그 뒤 쉼(0.15 s 넘는 무음) → 옛 문장 첫 소리
while not (d[f:f + 15] < SIL_DB).all(): f += 1
while d[f] < SIL_DB: f += 1
g = int(OLD_LAST * 100)                            # "materials." 시작에서 다음 쉼까지(단어 속 짧은 무음은 건너뜀)
while not (d[g:g + 15] < SIL_DB).all(): g += 1
a, b = f * win, g * win

def speech_rms(x):
    e = 10 ** (db(x) / 20)
    return np.sqrt(np.mean(e[e > np.percentile(e, 50)] ** 2))
clip *= speech_rms(audio[a:b]) / speech_rms(clip)
dc = db(clip)                                      # 고른 후보는 이미 trim 됐지만 앞뒤 무음이 조금 남을 수 있다
c0 = int(np.argmax(dc >= SIL_DB)) * win
c1 = (len(dc) - int(np.argmax(dc[::-1] >= SIL_DB))) * win
clip = clip[c0:c1]
n = int(.008 * SR); clip[:n] *= np.linspace(0, 1, n); clip[-n:] *= np.linspace(1, 0, n)
out = np.concatenate([audio[:a], clip, audio[b:]])
delta = (len(clip) - (b - a)) / SR
print(f"옛 구간 {a / SR:.2f}-{b / SR:.2f} ({(b - a) / SR:.2f}s) → 새 음성 {len(clip) / SR:.2f}s, 뒤쪽 {delta:+.2f}s")

with wave.open(WAV, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())

src = json.load(open(WORDS_SRC))
new = json.load(open(NEW_JSON))["words"]
words = [x for x in src["words"] if x["s"] < OLD_FIRST - .01]
words += [{"w": x["w"], "s": round(x["s"] - c0 / SR + a / SR, 2), "e": round(x["e"] - c0 / SR + a / SR, 2)} for x in new]
words += [dict(x, s=round(x["s"] + delta, 2), e=round(x["e"] + delta, 2)) for x in src["words"] if x["s"] > OLD_LAST + .01]
text = src["text"].replace("download, print, and provide the appropriate materials.", "use these materials flexibly according to individual learning needs.")
json.dump(dict(src, text=text, words=words),open(WORDS, "w"), ensure_ascii=False, indent=1)
print("단어", len(src["words"]), "→", len(words))
