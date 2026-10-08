"""영상에서 앞뒤 프레임과 동떨어진 프레임(깨진 캡처·깜빡임)을 찾는다. 있으면 종료 코드 1."""
import subprocess, sys
import numpy as np

FF = __import__("os").path.join(__import__("os").path.dirname(__file__), "node_modules/ffmpeg-static/ffmpeg")
W, H, FPS = 320, 180, 30
raw = subprocess.run([FF, "-loglevel", "error", "-i", sys.argv[1], "-vf", f"scale={W}:{H},format=gray", "-f", "rawvideo", "-"],
                     capture_output=True, check=True).stdout
a = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.int16)
bad = []
for i in range(1, len(a) - 1):
    e = (np.abs(a[i] - (a[i - 1] + a[i + 1]) // 2) > 20).sum()
    base = (np.abs(a[i + 1] - a[i - 1]) > 20).sum()
    if e > 200 and e > 3 * base + 100:
        bad.append(i)
print(f"검사 {len(a)}프레임, 이상 프레임 {len(bad)}개", [f"{i / FPS:.2f}s" for i in bad])
sys.exit(1 if bad else 0)
