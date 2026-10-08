import sys, glob
from PIL import Image
files = sorted(glob.glob(sys.argv[1]))
out = sys.argv[2]; n = 4
for k in range(0, len(files), n):
    sheet = Image.new("RGB", (1920, 1080), "black")
    for i, f in enumerate(files[k:k+n]):
        im = Image.open(f).convert("RGB").resize((960, 540))
        sheet.paste(im, ((i % 2) * 960, (i // 2) * 540))
    sheet.save(f"{out}{k//n}.png")
