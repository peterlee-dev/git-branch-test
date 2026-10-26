// 사용: node render.js stills 3,12.5,40        → stills/*.png
//       node render.js video out.mp4 [workers]  → 병렬 렌더 후 오디오 합성
//       node render.js patch base.mp4 out.mp4 44-60,84-91.6  → 그 구간(초)만 다시 렌더해 base 에 끼움
const puppeteer = require("puppeteer-core");
const ffmpeg = require("ffmpeg-static");
const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const URL = "file://" + path.join(__dirname, "index.html");
const FPS = 30;

async function openPage(browser) {
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });
  page.on("pageerror", e => console.error("PAGE ERROR:", e.message));
  page.on("console", m => m.type() === "error" && console.error("CONSOLE:", m.text()));
  await page.goto(URL, { waitUntil: "load" });
  await page.waitForFunction("window.READY === true");
  await page.evaluate(() => document.fonts.ready);
  return page;
}

const launch = () => puppeteer.launch({ executablePath: CHROME, headless: true, args: ["--allow-file-access-from-files", "--force-color-profile=srgb", "--hide-scrollbars"] });

function run(cmd, args, opts = {}) {
  return new Promise((res, rej) => {
    const p = spawn(cmd, args, { stdio: ["pipe", "ignore", "pipe"], ...opts });
    let err = "";
    p.stderr?.on("data", d => (err += d));
    p.on("close", code => (code === 0 ? res() : rej(new Error(err.slice(-2000) || `${cmd} exit ${code}`))));
    if (opts.feed) opts.feed(p.stdin);
  });
}

// 캡처 결과가 1920×1080 PNG인지 확인(IHDR의 가로·세로)
function pngSize(buf) { return [buf.readUInt32BE(16), buf.readUInt32BE(20)]; }

async function capture(page, t) {
  await page.evaluate(t => window.seek(t), t);
  // 변경된 DOM이 실제로 그려진 뒤 캡처
  await page.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));
  for (let k = 0; k < 3; k++) {
    const buf = await page.screenshot({ type: "png", captureBeyondViewport: false });
    const [w, h] = pngSize(buf);
    if (w === 1920 && h === 1080) return buf;
    console.error(`frame ${t.toFixed(3)}s: ${w}x${h} — 다시 캡처`);
  }
  throw new Error(`frame ${t}: 캡처 크기 이상`);
}

// 작업마다 브라우저를 따로 띄운다(한 브라우저에서 여러 탭을 동시에 캡처하면 가끔 깨진 프레임이 나온다)
async function renderChunk(from, to, out, id) {
  const browser = await launch();
  const page = await openPage(browser);
  const ff = spawn(ffmpeg, ["-y", "-f", "image2pipe", "-framerate", String(FPS), "-c:v", "png", "-i", "-",
    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", String(FPS), out], { stdio: ["pipe", "ignore", "pipe"] });
  let err = ""; ff.stderr.on("data", d => (err += d));
  const done = new Promise((res, rej) => ff.on("close", c => (c === 0 ? res() : rej(new Error(err.slice(-1500))))));
  const t0 = Date.now();
  for (let f = from; f < to; f++) {
    const buf = await capture(page, f / FPS);
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
    if ((f - from) % 300 === 0) console.log(`[w${id}] ${f - from}/${to - from} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
  }
  ff.stdin.end();
  await done;
  await browser.close();
}

(async () => {
  const [mode, a1, a2] = process.argv.slice(2);
  const browser = await launch();
  if (mode === "stills") {
    fs.mkdirSync(path.join(__dirname, "stills"), { recursive: true });
    const page = await openPage(browser);
    for (const t of a1.split(",").map(Number)) {
      await page.evaluate(t => window.seek(t), t);
      await page.screenshot({ path: path.join(__dirname, "stills", `t${t.toFixed(1).padStart(6, "0")}.png`) });
    }
  } else if (mode === "video") {
    const page = await openPage(browser);
    const dur = await page.evaluate(() => window.DURATION);
    await page.close();
    const total = Math.ceil(dur * FPS);
    const W = parseInt(a2 || "6", 10);
    const tmp = path.join(__dirname, "chunks"); fs.mkdirSync(tmp, { recursive: true });
    const per = Math.ceil(total / W);
    const parts = [];
    await Promise.all(Array.from({ length: W }, (_, i) => {
      const from = i * per, to = Math.min(total, from + per);
      const out = path.join(tmp, `part${i}.mp4`); parts.push(out);
      return renderChunk(from, to, out, i);
    }));
    const list = path.join(tmp, "list.txt");
    fs.writeFileSync(list, parts.map(p => `file '${p}'`).join("\n"));
    await run(ffmpeg, ["-y", "-f", "concat", "-safe", "0", "-i", list, "-i", path.join(__dirname, "narration.wav"),
      "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000", "-shortest", "-movflags", "+faststart", a1]);
    console.log("done:", a1, `${total} frames`);
    // 전 프레임 검사: 앞뒤 프레임과 동떨어진 프레임(깨진 캡처)을 찾는다
    await run("python3", [path.join(__dirname, "check_frames.py"), a1], { stdio: ["ignore", "inherit", "inherit"] });
  } else if (mode === "patch") {
    // 바뀐 구간만 다시 렌더해 기존 영상에 끼운다(오디오는 기존 영상 것을 그대로 씀)
    // node render.js patch base.mp4 out.mp4 44-60,84-91.6
    const [base, out, spans] = [a1, a2, process.argv[5]];
    const page = await openPage(browser);
    const total = Math.ceil((await page.evaluate(() => window.DURATION)) * FPS);
    await page.close();
    const R = spans.split(",").map(s => s.split("-").map(t => Math.round(Number(t) * FPS))).map(([a, b]) => [Math.max(0, a), Math.min(total, b)]).sort((x, y) => x[0] - y[0]);
    const tmp = path.join(__dirname, "chunks"); fs.mkdirSync(tmp, { recursive: true });
    const parts = R.map((_, i) => path.join(tmp, `patch${i}.mp4`));
    await Promise.all(R.map(([a, b], i) => renderChunk(a, b, parts[i], i)));
    // 원본 [0,a0) + patch0 + 원본 [b0,a1) + patch1 + … + 원본 [bN,total)
    const segs = [], inputs = ["-i", base]; let cur = 0;
    R.forEach(([a, b], i) => {
      if (a > cur) segs.push(`[0:v]trim=start_frame=${cur}:end_frame=${a},setpts=PTS-STARTPTS[s${segs.length}]`);
      inputs.push("-i", parts[i]); segs.push(`[${i + 1}:v]setpts=PTS-STARTPTS[s${segs.length}]`); cur = b;
    });
    if (cur < total) segs.push(`[0:v]trim=start_frame=${cur}:end_frame=${total},setpts=PTS-STARTPTS[s${segs.length}]`);
    const fc = segs.join(";") + ";" + segs.map((_, i) => `[s${i}]`).join("") + `concat=n=${segs.length}:v=1:a=0[v]`;
    await run(ffmpeg, ["-y", ...inputs, "-filter_complex", fc, "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", String(FPS), "-c:a", "copy", "-movflags", "+faststart", out]);
    console.log("done:", out, R.map(([a, b]) => `${(a / FPS).toFixed(2)}–${(b / FPS).toFixed(2)}s`).join(", "));
    await run("python3", [path.join(__dirname, "check_frames.py"), out], { stdio: ["ignore", "inherit", "inherit"] });
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
