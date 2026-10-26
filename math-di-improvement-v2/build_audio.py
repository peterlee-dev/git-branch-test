"""TTS 내레이션(source/di_tts.wav, 한 파일)을 문장별로 잘라 → 장면 간격 규칙대로 다시 배치 → narration.wav, timeline.json/js, subtitles.srt.

문장 경계: 받아쓰기 단어 타임스탬프(source/di_tts_words.json)로 문장 첫·끝 단어를 찾고, 그 사이 무음 구간에서 자른다(앞뒤 여유 PAD_*).
큐 시각: 기준 구절 첫 단어가 말해지는 시각 - CUE_LEAD. 간격 규칙은 ../math-di-improvement/build_audio.py 와 같다.
실행: python3 build_audio.py   (numpy 필요. 음성 디코딩은 node_modules 의 ffmpeg-static)
"""
import difflib, json, os, re, subprocess, sys, wave
import numpy as np
from narration import SCENES

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "source", "di_tts.wav")
WORDS = os.path.join(HERE, "source", "di_tts_words.json")
SR = 44100

LEAD_IN = 0.8        # 영상 시작 후 첫 장면 전
SCENE_PRE = 1.0      # 장면 시작 → 첫 문장
SENT_GAP = 0.4       # 문장 사이
SCENE_TAIL = 0.9     # 마지막 문장 끝 → 다음 장면
CUE_LEAD = 0.15      # 말보다 살짝 먼저 보이게

PAD_START = 0.05     # 소리 시작 앞 여유
PAD_END = 0.10       # 소리 끝 뒤 여유(끝소리 잔향)
SIL_DB = -45         # 이보다 작으면 무음(녹음 바닥 소음은 약 -88 dB)
FADE = 0.008         # 자른 자리 딸깍 소리 방지

NUMWORDS = {"zero": "0", "one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10"}


def ffmpeg_exe():
    p = os.path.join(HERE, "node_modules", "ffmpeg-static", "ffmpeg")
    if os.path.exists(p):
        return p
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def load_audio():
    raw = subprocess.run([ffmpeg_exe(), "-v", "error", "-i", SRC, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def norm(w, spoken=False):
    w = re.sub(r"[^a-z0-9]", "", w.lower())
    return NUMWORDS.get(w, w) if spoken else w


def whisper_words():
    """받아쓰기 단어. 앞 공백 없는 조각(%, .S., -life …)은 앞 단어에 붙인다."""
    out = []
    for x in json.load(open(WORDS))["words"]:
        if out and not x["w"].startswith(" "):
            out[-1]["w"] += x["w"]; out[-1]["e"] = x["e"]
        else:
            out.append({"w": x["w"].strip(), "s": x["s"], "e": x["e"]})
    return [dict(x, n=norm(x["w"], True)) for x in out if norm(x["w"])]


def clean(text):
    return text.replace(" | ", " ")


def main():
    audio = load_audio()
    win = int(0.01 * SR)
    nfr = len(audio) // win
    db = 20 * np.log10(np.sqrt((audio[:nfr * win].reshape(nfr, win) ** 2).mean(1)) + 1e-9)
    silent = db < SIL_DB

    # 대본 단어 ↔ 받아쓰기 단어 맞추기
    sents = []   # (scene index, sentence index, text with |, tokens)
    for i, sc in enumerate(SCENES):
        for k, text in enumerate(sc["sentences"]):
            sents.append((i, k, text, clean(text).split()))
    script = [(si, ti) for si, s in enumerate(sents) for ti in range(len(s[3]))]
    a = [norm(sents[si][3][ti], True) for si, ti in script]
    ww = whisper_words()
    # 받아쓰기는 쉼(무음)을 다음 단어 시작에 붙이곤 한다("improve" 31.66–33.40 처럼).
    # 단어 구간 안에 0.15 s 넘는 무음이 있고 그 뒤에 소리가 남아 있으면, 단어 시작을 무음 끝으로 옮긴다
    moved = 0
    for x in ww:
        f, f1 = int(round(x["s"] * 100)), int(round(x["e"] * 100))
        run_end = None
        while f < f1:
            if silent[f]:
                g = f
                while g < nfr and silent[g]:
                    g += 1
                if g - f >= 15 and f1 - g >= 8:
                    run_end = g
                f = g
            else:
                f += 1
        if run_end is not None:
            x["s"] = run_end / 100; moved += 1
    print("무음 뒤로 시작을 옮긴 단어", moved)
    b = [x["n"] for x in ww]
    m = difflib.SequenceMatcher(None, a, b, autojunk=False)
    match = [None] * len(a)
    for blk in m.get_matching_blocks():
        for j in range(blk.size):
            match[blk.a + j] = blk.b + j
    unmatched = [sents[script[i][0]][3][script[i][1]] for i in range(len(a)) if match[i] is None]
    print("대본 단어", len(a), "받아쓰기 단어", len(b), "못 맞춘 대본 단어", len(unmatched), unmatched)

    # 대본 단어마다 시작·끝 시각(못 맞춘 단어는 앞뒤 맞춘 단어 사이로 보간)
    idx = np.arange(len(a))
    known = [i for i in idx if match[i] is not None]
    ts = np.interp(idx, known, [ww[match[i]]["s"] for i in known])
    te = np.interp(idx, known, [ww[match[i]]["e"] for i in known])
    flat = {}
    for g, (si, ti) in enumerate(script):
        flat[(si, ti)] = (float(ts[g]), float(te[g]))

    # 문장 경계를 무음 구간에서 정한다
    def frame(t):
        return int(np.clip(round(t * 100), 0, nfr - 1))

    def cut_between(t_end, t_next):
        # 받아쓰기 시각은 0.3 s 남짓 어긋날 수 있어 넓게 찾고, 그 안에서 가장 긴 무음을 고른다
        lo, hi = frame(min(t_end, t_next) - 0.3), frame(max(t_end, t_next) + 0.6)
        runs, f = [], lo
        while f <= hi:
            if silent[f]:
                g = f
                while g <= hi and silent[g]:
                    g += 1
                runs.append((f, g)); f = g
            else:
                f += 1
        if runs:
            f0, f1 = max(runs, key=lambda r: r[1] - r[0])
            while f0 > 0 and silent[f0 - 1]:          # 찾는 창 밖으로 이어진 무음까지
                f0 -= 1
            while f1 < nfr and silent[f1]:
                f1 += 1
            print(f"  경계 {t_end:7.2f}|{t_next:7.2f}  무음 {f0 / 100:7.2f}-{f1 / 100:7.2f} ({(f1 - f0) * 10} ms)")
            s0, s1 = f0 / 100 + PAD_END, f1 / 100 - PAD_START
            if s0 > s1:
                s0 = s1 = (f0 + f1) / 200
            return s0, s1
        f = lo + int(np.argmin(db[lo:hi + 1]))
        print(f"  무음 없음: {t_end:.2f}~{t_next:.2f}, 가장 조용한 {f / 100:.2f}s 에서 자름")
        return f / 100, f / 100

    first = int(np.argmax(~silent)) / 100 - PAD_START
    last = (nfr - int(np.argmax(~silent[::-1]))) / 100 + PAD_END
    bounds = []
    for si, s in enumerate(sents):
        st = flat[(si, 0)][0]
        en = flat[(si, len(s[3]) - 1)][1]
        bounds.append([st, en])
    clips = [[max(0, first), None] for _ in sents]
    for si in range(len(sents) - 1):
        e0, s1 = cut_between(bounds[si][1], bounds[si + 1][0])
        clips[si][1] = e0
        clips[si + 1][0] = s1
    clips[-1][1] = min(len(audio) / SR, last)

    def clip_audio(c0, c1):
        x = audio[int(round(c0 * SR)):int(round(c1 * SR))].copy()
        n = int(FADE * SR)
        if len(x) > 2 * n:
            x[:n] *= np.linspace(0, 1, n); x[-n:] *= np.linspace(1, 0, n)
        return x

    # 다시 배치
    out = []
    pos = [0]
    def put(t, x):
        n = int(round(t * SR))
        if n > pos[0]:
            out.append(np.zeros(n - pos[0], np.float32)); pos[0] = n
        out.append(x); pos[0] += len(x)

    t = LEAD_IN
    scenes, subs, report = [], [], []
    g = 0
    for i, sc in enumerate(SCENES):
        start = t
        t += SCENE_PRE
        placed = []
        for k, text in enumerate(sc["sentences"]):
            if k:
                t += SENT_GAP
            c0, c1 = clips[g]
            x = clip_audio(c0, c1)
            put(t, x)
            d = len(x) / SR
            shift = t - c0          # 원본 시각 → 새 시각
            toks = clean(text).split()
            word_t = [(max(t, flat[(g, j)][0] + shift), min(t + d, flat[(g, j)][1] + shift)) for j in range(len(toks))]
            placed.append((t, d, text, word_t))
            report.append(f"{sc['id']:9} {k}  src {c0:7.2f}-{c1:7.2f}  → {t:7.2f}-{t + d:7.2f}  {clean(text)[:60]}")
            # 자막: " | " 자리에서 나눔. 조각 시작 = 그 조각 첫 단어 시작, 끝 = 다음 조각 시작
            parts = [p.split() for p in text.split(" | ")]
            starts, j = [], 0
            for pi, p in enumerate(parts):
                starts.append(t if pi == 0 else word_t[j][0]); j += len(p)
            for pi, p in enumerate(parts):
                subs.append((starts[pi], starts[pi + 1] if pi + 1 < len(parts) else t + d, " ".join(p)))
            t += d
            g += 1
        cues = {}
        for name, k, phrase in sc["cues"]:
            st, d, text, word_t = placed[k]
            if phrase is None:
                cues[name] = st - 0.1
            elif phrase == "END":
                cues[name] = st + d
            else:
                ci = clean(text).find(phrase)
                if ci < 0:
                    sys.exit(f"구절 없음: {phrase!r} in {text!r}")
                cues[name] = word_t[len(clean(text)[:ci].split())][0] - CUE_LEAD
        t += sc.get("tail", SCENE_TAIL)
        scenes.append({"id": sc["id"], "start": round(start, 3), "end": round(t, 3),
                       "cues": {k: round(v - start, 3) for k, v in cues.items()}})
    put(t + 0.5, np.zeros(0, np.float32))
    pcm = np.concatenate(out)
    total = len(pcm) / SR

    with wave.open(os.path.join(HERE, "narration.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(pcm, -1, 1) * 32767).astype(np.int16).tobytes())
    tl = json.dumps({"duration": round(total, 3), "scenes": scenes}, indent=1)
    open(os.path.join(HERE, "timeline.json"), "w").write(tl)
    open(os.path.join(HERE, "timeline.js"), "w").write("window.TIMELINE = " + tl + ";\n")

    def srt_time(x):
        ms = int(round(x * 1000))
        return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"
    with open(os.path.join(HERE, "subtitles.srt"), "w") as f:
        for n, (s0, s1, text) in enumerate(subs, 1):
            f.write(f"{n}\n{srt_time(s0)} --> {srt_time(s1)}\n{text}\n\n")
    open(os.path.join(HERE, "source", "clips.txt"), "w").write("\n".join(report) + "\n")
    print("\n".join(report))
    print(f"total {total:.1f}s, {len(scenes)} scenes, {len(subs)} subtitles")


if __name__ == "__main__":
    main()
