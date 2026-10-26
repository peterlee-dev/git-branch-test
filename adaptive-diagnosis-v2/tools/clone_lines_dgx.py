# Adaptive v2 3차 수정: 최종 대본에서 바뀐 문장만 이 영상 녹음(여성 화자)의 목소리를 복제해 새로 만든다
# DGX 의 ~/dev/qwen3-tts-api 에서 실행: out/clone-adaptive/ 에 ref.wav(녹음 14.1–28.7 s), narration.mp3, lines.json
# ([{id, text(화면·자막 표기), tts(읽는 표기), wps(녹음 속 원래 문장의 초당 단어 수)}])을 두고
#   .venv/bin/python out/clone-adaptive/redo_lines.py [id ...]   → out/clone-adaptive/<id>/pick.wav, pick.json → audio/clone_<id>.wav, .json
# 참조 = narration.mp3 의 l3~l4 (14.1–28.7 s), 화자 유사도 기준 = narration.mp3 전체
# 후보 N_CAND 개 → Whisper 받아쓰기 일치(CER 0) → 화자 유사도 최고 → 원래 문장 말 빠르기에 맞춰 atempo → 단어 시각
import json, os, re, subprocess, sys, urllib.request, uuid
import librosa, numpy as np, soundfile as sf, torch
sys.path.insert(0, "out/tools/sb")
from speechbrain.inference.speaker import EncoderClassifier
from transformers import pipeline

D = "out/clone-adaptive"
REF = f"{D}/ref.wav"
REF_TEXT = ("A diagnostic assessment is designed to identify a learner's current level before the learner begins studying "
            "and to prescribe a personalized learning program. Currently, accurate diagnosis requires every learner to answer the same set of questions.")
LINES = [x for x in json.load(open(f"{D}/lines.json")) if not sys.argv[1:] or x["id"] in sys.argv[1:]]
N_CAND, SR = 8, 24000

asr = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3-turbo", torch_dtype=torch.float16, device="cuda:0")
enc = EncoderClassifier.from_hparams("speechbrain/spkrec-ecapa-voxceleb", savedir="models/spkrec-ecapa", run_opts={"device": "cuda:0"})
def emb(y16):
    with torch.no_grad():
        e = enc.encode_batch(torch.tensor(y16).unsqueeze(0)).squeeze()
    return (e / e.norm()).cpu().numpy()
src, _ = librosa.load(f"{D}/narration.mp3", sr=16000)
target = np.mean([emb(src[s * 16000:(s + 10) * 16000]) for s in range(0, int(len(src) / 16000) - 10, 10)], 0)
target /= np.linalg.norm(target)
print("ref sim to whole take:", float(emb(librosa.load(REF, sr=16000)[0]) @ target), flush=True)

NUM = {"1": "one", "3": "three", "7": "seven", "9": "nine"}
def norm(s):   # Whisper writes "number 3" / "No. 3" / "JEI" where the text says "number three" / "J.E.I."
    s = re.sub(r"\bno\.?\s+(?=\d)", "number ", s.lower())
    return re.sub(r"[^\w]", "", re.sub(r"\d", lambda m: NUM.get(m.group(), m.group()), s))
def cer(a, b):
    d = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        p, d[0] = d[0], i
        for j, cb in enumerate(b, 1):
            p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (ca != cb))
    return d[-1] / max(len(a), 1)
def tts(text):
    b = uuid.uuid4().hex
    parts = [("text", text), ("ref_text", REF_TEXT), ("language", "English"), ("format", "wav")]
    body = b"".join(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode() for k, v in parts)
    body += f'--{b}\r\nContent-Disposition: form-data; name="ref_audio"; filename="ref.wav"\r\nContent-Type: audio/wav\r\n\r\n'.encode()
    body += open(REF, "rb").read() + f"\r\n--{b}--\r\n".encode()
    req = urllib.request.Request("http://127.0.0.1:8095/v1/tts/clone", data=body, headers={"Content-Type": f"multipart/form-data; boundary={b}"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return r.read()
def words_of(y):
    r = asr(librosa.resample(y, orig_sr=SR, target_sr=16000), return_timestamps="word", generate_kwargs={"language": "english"})
    return [{"w": " " + c["text"].strip(), "s": round(c["timestamp"][0], 2), "e": round(c["timestamp"][1], 2)} for c in r["chunks"]]

for L in LINES:
    lid, text, wps = L["id"], L["tts"], L["wps"]
    out = f"{D}/{lid}"; os.makedirs(out, exist_ok=True)
    nw = len(text.split())
    cands = []
    for t in range(N_CAND):
        path = f"{out}/cand_{t}.wav"
        open(path, "wb").write(tts(text))
        y, _ = librosa.load(path, sr=SR)
        y, _ = librosa.effects.trim(y, top_db=40)
        y16 = librosa.resample(y, orig_sr=SR, target_sr=16000)
        hyp = asr(y16, generate_kwargs={"language": "english"})["text"].strip()
        c = {"try": t, "cer": cer(norm(text), norm(hyp)), "sim": float(emb(y16) @ target), "dur": len(y) / SR, "wps": nw / (len(y) / SR), "hyp": hyp}
        cands.append(c); print(lid, json.dumps(c), flush=True)
    ok = [x for x in cands if x["cer"] == 0] or sorted(cands, key=lambda x: x["cer"])[:1]
    best = max(ok, key=lambda x: x["sim"])
    tempo = float(np.clip(wps / best["wps"], .9, 1.15))
    print(lid, "pick", best, "tempo", round(tempo, 3), flush=True)
    y, _ = librosa.load(f"{out}/cand_{best['try']}.wav", sr=SR)
    y, _ = librosa.effects.trim(y, top_db=40)
    if abs(tempo - 1) > .01:
        p = subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", f"atempo={tempo:.4f}", "-f", "f32le", "-"],
                           input=y.astype(np.float32).tobytes(), capture_output=True, check=True)
        y = np.frombuffer(p.stdout, dtype=np.float32)
    sf.write(f"{out}/pick.wav", y, SR)
    json.dump({"text": L["text"], "tts": text, "pick": best, "tempo": round(tempo, 4), "cands": cands, "words": words_of(y)}, open(f"{out}/pick.json", "w"), indent=1)
    print(lid, "done", round(len(y) / SR, 2), flush=True)
