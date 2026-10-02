"""사내 TTS 로 미리 만든 내레이션 음성을 영상의 make_audio.py 에 넣어 주는 연결 모듈

사내 TTS API 는 회사 PC 에서만 닿으므로 음성은 PC 에서 만들고(tools/jei_tts.py), 영상 조립·렌더는 어디서든 함:

  1) TTS_ENGINE=jei python3 <영상>/tools/make_audio.py
       → 음성이 없는 문장을 <영상>/voice/script.json 에 적고 멈춤 (timeline.js·mix.wav 는 그대로 둠)
  2) (회사 PC) python3 tools/jei_tts.py <영상>
       → script.json 의 문장을 사내 TTS 로 만들어 <영상>/voice/<문장키>.mp3 로 저장 → 커밋·푸시
  3) TTS_ENGINE=jei python3 <영상>/tools/make_audio.py
       → 그 음성 길이로 timeline.js 와 audio/mix.wav 를 만듦 → node render.mjs

문장키는 문장 글자의 해시라서, 문장을 고치면 그 줄만 다시 만들면 됨. 말 빠르기(speed) 인자는 쓰지 않음 (사내 TTS 기본 빠르기)
"""
import os, sys, json, atexit, hashlib, subprocess
import numpy as np

def key(text):
    return hashlib.sha1(text.strip().encode('utf-8')).hexdigest()[:16]

def _ffmpeg():
    exe = os.environ.get('FFMPEG')
    if exe: return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return 'ffmpeg'

def _decode(path, sr):
    raw = subprocess.run([_ffmpeg(), '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(sr), '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()

def load(video_dir, sr, trim, lang='ko'):
    """make_audio.py 의 load_tts() 대신 쓰는 say(text, ...) 를 돌려줌"""
    video_dir = os.path.abspath(video_dir)
    vdir = os.path.join(video_dir, 'voice')
    os.makedirs(vdir, exist_ok=True)
    asked, missing = [], []
    # 음성이 빠진 채로 돌면 make_audio.py 가 가짜 길이로 시각표·소리 파일을 덮어쓰므로, 끝날 때 되돌려 놓음
    keep = {}
    adir = os.path.join(video_dir, 'audio')
    for f in [os.path.join(video_dir, n) for n in os.listdir(video_dir) if n.endswith('.js')] + \
             ([os.path.join(adir, n) for n in os.listdir(adir) if n.endswith('.wav')] if os.path.isdir(adir) else []):
        keep[f] = open(f, 'rb').read()                 # timeline.js · warp.js 같은 시각표와 audio/*.wav

    def say(text, *args, **kw):
        k = key(text)
        if k not in [a['key'] for a in asked]: asked.append({'key': k, 'text': text.strip(), 'lang': lang})
        f = os.path.join(vdir, k + '.mp3')
        if not os.path.exists(f):
            missing.append(k)
            return np.zeros(int(sr * max(.6, len(text) * .09)), np.float32)   # 자리만 잡아 두는 무음
        return trim(_decode(f, sr))

    def finish():
        script = {'video': os.path.basename(video_dir), 'lang': lang, 'lines': asked}
        with open(os.path.join(vdir, 'script.json'), 'w', encoding='utf-8') as fp:
            json.dump(script, fp, ensure_ascii=False, indent=1)
        if missing:
            for f, b in keep.items(): open(f, 'wb').write(b)
            n = len(set(missing))
            print(f'\n[voicebank] 사내 TTS 음성이 없는 문장 {n}개 → {os.path.relpath(vdir)}/script.json 에 적었어요.'
                  f'\n            시각표(.js)·소리(.wav) 파일은 바꾸지 않았어요. 회사 PC 에서 python3 tools/jei_tts.py {script["video"]} 실행 후 다시 돌리세요.')
            os._exit(3)
        print(f'[voicebank] 사내 TTS 음성 {len(asked)}줄 사용')
    atexit.register(finish)
    return say
