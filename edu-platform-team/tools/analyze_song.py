"""배경음(audio/celebration.mp3)의 박자와 드롭을 찾아 song.js / tools/song.json 에 저장.

- 영상은 120BPM(한 박 0.5초) 격자로 짜여 있고, 페이지가 이 값을 읽어 곡의 실제 박 길이에 맞게 시간을 늘이거나 줄여요
- 영상 격자 2.0초(4박째) = 곡의 드롭, 영상 시작 = 드롭 4박 전
사용법: pip install librosa && python3 tools/analyze_song.py
"""
import os, json
import numpy as np
import librosa

HERE = os.path.dirname(os.path.abspath(__file__))
SONG = os.path.join(HERE, '..', 'audio', 'celebration.mp3')
DROP_GUESS = 33.5          # 드롭(킥이 크게 들어오는 순간) 대략 위치, 초
LEAD_BEATS = 4             # 드롭 전에 보여줄 박 수 (영상 격자 2.0초)
GRID_BEATS = 68            # 영상 전체 길이 (120BPM 격자 34초)

y, sr = librosa.load(SONG, sr=22050, mono=True)
_, beats = librosa.beat.beat_track(y=y, sr=sr, units='time')
beat, drop = 60 / 122, DROP_GUESS
sel = beats[(beats > drop - 3) & (beats < drop + 34)]
for _ in range(4):                          # 박자 격자에 맞는 박만 골라 직선 맞춤 (드롭 위치와 박 길이)
    n = np.round((sel - drop) / beat); ok = np.abs(drop + n * beat - sel) < .06
    (beat, drop), *_ = np.linalg.lstsq(np.vstack([n[ok], np.ones(ok.sum())]).T, sel[ok], rcond=None)
start = drop - LEAD_BEATS * beat
info = {'file': 'audio/celebration.mp3', 'bpm': round(60 / beat, 3), 'beat': round(float(beat), 6), 'drop': round(float(drop), 4),
        'start': round(float(start), 4), 'duration': round(float(GRID_BEATS * beat), 4)}
json.dump(info, open(os.path.join(HERE, 'song.json'), 'w'), indent=1)
open(os.path.join(HERE, '..', 'song.js'), 'w').write('// tools/analyze_song.py 가 생성: 배경음 박자 정보\nwindow.SONG = ' + json.dumps(info) + ';\n')
print(info)
