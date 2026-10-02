"""회사 PC 에서 사내 TTS API(/editor/sound/tts)로 영상 내레이션 음성을 만드는 스크립트 (파이썬 기본 기능만 사용)

  python3 tools/jei_tts.py --test "안녕하세요, 재능교육입니다."   # 설정 확인용 한 문장 → tools/jei_tts_test.mp3
  python3 tools/jei_tts.py science-animals                       # <영상>/voice/script.json 의 빠진 문장만 만듦
  python3 tools/jei_tts.py science-animals --force               # 목소리를 바꿨을 때: 전부 다시 만듦

설정: tools/jei_tts.local.json (저장소에 올리지 않음, jei_tts.example.json 을 복사해서 채움). 같은 이름의 환경변수가 있으면 그 값을 씀
  url            JEI_TTS_URL            예: https://<사내 서버>/editor/sound/tts
  headers        JEI_TTS_HEADERS        인증 헤더 (JSON). 키·토큰은 이 파일이나 환경변수에만 두세요
  type           JEI_TTS_TYPE           입력 타입 (텍스트 / SSML 중 텍스트 값)
  voice          JEI_TTS_VOICE          음성 번호 (예: 10)
  modeldivision  JEI_TTS_MODEL_KO / JEI_TTS_MODEL_EN   모델 언어 값 (영상 언어가 ko/en 일 때 각각)

만든 음성은 <영상>/voice/<문장키>.mp3, 어떤 설정으로 만들었는지는 <영상>/voice/index.json 에 남음 → git 커밋·푸시하면 영상 조립 쪽에서 씀
"""
import os, sys, json, base64, hashlib, argparse, time, subprocess
from xml.sax.saxutils import escape as xml_escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

def key(text):   # tools/voicebank.py 의 key() 와 같아야 함
    return hashlib.sha1(text.strip().encode('utf-8')).hexdigest()[:16]

def config():
    c = {}
    f = os.path.join(HERE, 'jei_tts.local.json')
    if os.path.exists(f): c = json.load(open(f, encoding='utf-8'))
    env = os.environ.get
    if env('JEI_TTS_URL'): c['url'] = env('JEI_TTS_URL')
    if env('JEI_TTS_HEADERS'): c['headers'] = json.loads(env('JEI_TTS_HEADERS'))
    if env('JEI_TTS_TYPE'): c['type'] = env('JEI_TTS_TYPE')
    if env('JEI_TTS_VOICE'): c['voice'] = int(env('JEI_TTS_VOICE'))
    md = dict(c.get('modeldivision') or {})
    if env('JEI_TTS_MODEL_KO'): md['ko'] = env('JEI_TTS_MODEL_KO')
    if env('JEI_TTS_MODEL_EN'): md['en'] = env('JEI_TTS_MODEL_EN')
    c['modeldivision'] = md
    if not c.get('url'): sys.exit('설정이 없어요: tools/jei_tts.example.json 을 tools/jei_tts.local.json 으로 복사해서 url 등을 채우세요.')
    return c

def tts(c, text, lang, voice=None):
    md = c['modeldivision'].get(lang)
    if not md: sys.exit(f'modeldivision 에 "{lang}" 값이 없어요 (jei_tts.local.json 의 modeldivision.{lang}).')
    v = voice if voice is not None else c.get('voice')
    typ = c.get('type', 'text')
    if typ == 'ssml':   # 목소리 번호는 voice 필드가 아니라 SSML 안에 들어감 (rate·volume·pitch·break 는 설정 파일 'ssml' 로 바꿈)
        s = {'rate': 1, 'volume': 1, 'pitch': 0, 'break': 1, **(c.get('ssml') or {})}
        speech = (f'<speak><voice name="{v}"><prosody rate="{s["rate"]}" volume="{s["volume"]}" pitch="{s["pitch"]}">'
                  f'{xml_escape(text)}</prosody><break time="{s["break"]}"></break></voice></speak>')
        sent = {'type': 'ssml', 'speech': speech, 'modeldivision': md}
    else:
        sent = {'type': typ, 'speech': text, 'modeldivision': md}
        if v is not None: sent['voice'] = v
    body = {**sent, 'voice': v}   # 기록용 (index.json)
    # 파이썬 urllib 대신 curl 을 씀: 이 서버는 중간 인증서를 안 보내 줘서 파이썬은 인증서 검증에 실패함 (curl 은 통과)
    # 헤더(토큰)는 명령줄이 아니라 stdin 설정(-K -)으로 넘겨서 프로세스 목록에 안 보이게 함
    esc = lambda s: str(s).replace('\\', '\\\\').replace('"', '\\"')
    headers = {'Content-Type': 'application/json', **(c.get('headers') or {})}
    conf = ''.join(f'header = "{esc(k)}: {esc(v)}"\n' for k, v in headers.items())
    payload = json.dumps(sent, ensure_ascii=False)
    for attempt in range(4):
        p = subprocess.run(['curl', '-sS', '-m', '60', '-X', 'POST', '-K', '-', '--data-binary', payload,
                            '-w', '\n%{http_code}', c['url']], input=conf, capture_output=True, text=True, encoding='utf-8')
        if p.returncode != 0:
            err = p.stderr.strip()[:300]
        else:
            resp, _, code = p.stdout.rpartition('\n'); code = int(code)
            if code == 200:
                try:
                    audio = json.loads(resp)['audio']                  # "data:audio/mp3;base64,...."
                    b64 = audio.split(',', 1)[1] if audio.startswith('data:') else audio
                    return base64.b64decode(b64), body
                except (KeyError, ValueError) as e:
                    err = f'응답을 읽지 못했어요: {resp[:200]!r}'
            elif code < 500: sys.exit(f'TTS 요청 실패 {code}: {resp[:300]}')
            else: err = f'{code} {resp[:300]}'
        time.sleep(2 ** attempt)
    sys.exit(f'TTS 요청이 계속 실패했어요: {err}')

def main():
    ap = argparse.ArgumentParser(description='사내 TTS 로 영상 내레이션 음성 만들기')
    ap.add_argument('video', nargs='?', help='영상 폴더 이름 (예: science-animals)')
    ap.add_argument('--test', metavar='문장', help='한 문장만 만들어 tools/jei_tts_test.mp3 로 저장')
    ap.add_argument('--lang', default=None, help='ko / en (기본: script.json 의 언어)')
    ap.add_argument('--voice', type=int, default=None, help='음성 번호 (설정 파일 값 대신)')
    ap.add_argument('--force', action='store_true', help='이미 있는 음성도 다시 만듦')
    a = ap.parse_args()
    c = config()
    if a.test:
        mp3, body = tts(c, a.test, a.lang or 'ko', a.voice)
        out = os.path.join(HERE, 'jei_tts_test.mp3'); open(out, 'wb').write(mp3)
        print(f'저장: {out} ({len(mp3) // 1024} KB) · 요청 {json.dumps({k: v for k, v in body.items() if k != "speech"}, ensure_ascii=False)}')
        return
    if not a.video: ap.error('영상 폴더 이름이나 --test 를 주세요')
    vdir = os.path.join(ROOT, a.video, 'voice')
    sp = os.path.join(vdir, 'script.json')
    if not os.path.exists(sp): sys.exit(f'{sp} 가 없어요. 먼저 TTS_ENGINE=jei python3 {a.video}/tools/make_audio.py 로 만들거나, 받아 온 브랜치에 있는지 확인하세요.')
    script = json.load(open(sp, encoding='utf-8'))
    idx_path = os.path.join(vdir, 'index.json')
    idx = json.load(open(idx_path, encoding='utf-8')) if os.path.exists(idx_path) else {}
    lines = script['lines']; made = 0
    for i, ln in enumerate(lines, 1):
        k, text = ln['key'], ln['text']
        assert k == key(text), f'문장키가 맞지 않아요: {text}'
        out = os.path.join(vdir, k + '.mp3')
        if os.path.exists(out) and not a.force: continue
        mp3, body = tts(c, text, a.lang or ln.get('lang') or script.get('lang', 'ko'), a.voice)
        open(out, 'wb').write(mp3)
        idx[k] = {'text': text, 'voice': body.get('voice'), 'modeldivision': body['modeldivision'], 'type': body['type']}
        made += 1
        print(f'  [{i}/{len(lines)}] {text}')
    json.dump(idx, open(idx_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'완료: 새로 {made}줄, 전체 {len(lines)}줄 → {os.path.relpath(vdir, ROOT)}/  (git add {a.video}/voice && git commit && git push)')

if __name__ == '__main__':
    main()
