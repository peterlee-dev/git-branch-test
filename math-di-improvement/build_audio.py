"""문장별 TTS 생성(캐시) → 무음 다듬기 → 타임라인/큐 계산 → narration.wav, timeline.json, subtitles.srt."""
import array, hashlib, json, os, re, sys, wave
import urllib.request
from narration import SCENES

API = "http://192.168.51.8:8095/v1/tts/voices/guide"
HERE = os.path.dirname(os.path.abspath(__file__))
TTS_DIR = os.path.join(HERE, "tts")
SR = 24000

LEAD_IN = 0.8        # 영상 시작 후 첫 장면 전
SCENE_PRE = 1.0      # 장면 시작 → 첫 문장
SENT_GAP = 0.4       # 문장 사이
SCENE_TAIL = 0.9     # 마지막 문장 끝 → 다음 장면
CUE_LEAD = 0.15      # 말보다 살짝 먼저 보이게


# 발음 보정(TTS 입력에만 적용, 자막·화면은 원문 유지): JEI → J-E-I (글자 하나씩 읽게)
SAY = [(re.compile(r"\bJEI\b"), "J-E-I")]


def tts_path(text):
    for pat, rep in SAY:
        text = pat.sub(rep, text)
    return text, os.path.join(TTS_DIR, hashlib.sha1(text.encode()).hexdigest()[:16] + ".wav")


def tts(text):
    text, path = tts_path(text)
    if not os.path.exists(path):
        print("TTS:", text[:70], flush=True)
        req = urllib.request.Request(API, method="POST", headers={"Content-Type": "application/json"},
                                     data=json.dumps({"text": text, "language": "English", "format": "wav"}).encode())
        with urllib.request.urlopen(req, timeout=300) as r:
            open(path, "wb").write(r.read())
    with wave.open(path) as w:
        assert w.getframerate() == SR and w.getnchannels() == 1 and w.getsampwidth() == 2
        samples = array.array("h", w.readframes(w.getnframes()))
    return trim(samples)


def trim(s, thresh=300, pad=int(0.04 * SR)):
    win = int(0.01 * SR)
    def loud(i):
        return max(abs(x) for x in s[i:i + win]) > thresh
    a = 0
    while a < len(s) - win and not loud(a):
        a += win
    b = len(s) - win
    while b > a and not loud(b):
        b -= win
    return s[max(0, a - pad):min(len(s), b + win + pad)]


ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def spell(n):
    n = int(n)
    if n < 20:
        return ONES[n]
    if n < 100:
        return TENS[n // 10] + ("" if n % 10 == 0 else " " + ONES[n % 10])
    return ONES[n // 100] + " hundred" + ("" if n % 100 == 0 else " " + spell(n % 100))


def spoken(text):
    return re.sub(r"\d+", lambda m: spell(m.group()), text)


def ratio(sentence, phrase):
    """구절 시작이 문장에서 차지하는 발화 비율(숫자는 읽는 길이로 환산)."""
    i = sentence.find(phrase)
    if i < 0:
        sys.exit(f"구절 없음: {phrase!r} in {sentence!r}")
    return len(spoken(sentence[:i])) / len(spoken(sentence))


def srt_time(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def main():
    os.makedirs(TTS_DIR, exist_ok=True)
    out = array.array("h")
    def pad_to(t):
        n = int(round(t * SR))
        out.extend([0] * (n - len(out)))

    t = LEAD_IN
    scenes, subs = [], []
    for sc in SCENES:
        start = t
        t += SCENE_PRE
        sents = []
        for k, text in enumerate(sc["sentences"]):
            if k:
                t += SENT_GAP
            s = tts(text)
            pad_to(t)
            out.extend(s)
            d = len(s) / SR
            sents.append((t, d, text))
            subs.append((t, t + d, text))
            t += d
        cues = {}
        for name, k, phrase in sc["cues"]:
            st, d, text = sents[k]
            if phrase is None:
                cues[name] = st - 0.1
            elif phrase == "END":
                cues[name] = st + d
            else:
                cues[name] = st + d * ratio(text, phrase) - CUE_LEAD
        t += sc.get("tail", SCENE_TAIL)
        scenes.append({"id": sc["id"], "start": round(start, 3), "end": round(t, 3),
                       "cues": {k: round(v - start, 3) for k, v in cues.items()}})
    pad_to(t + 0.5)
    total = len(out) / SR

    with wave.open(os.path.join(HERE, "narration.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(out.tobytes())
    tl = json.dumps({"duration": round(total, 3), "scenes": scenes}, indent=1)
    open(os.path.join(HERE, "timeline.json"), "w").write(tl)
    open(os.path.join(HERE, "timeline.js"), "w").write("window.TIMELINE = " + tl + ";\n")
    with open(os.path.join(HERE, "subtitles.srt"), "w") as f:
        for i, (a, b, text) in enumerate(subs, 1):
            f.write(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{text}\n\n")
    print(f"total {total:.1f}s, {len(scenes)} scenes")


if __name__ == "__main__":
    main()
