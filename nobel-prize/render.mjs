// 사용법: node render.mjs [--fps 30] [--out out/nobel_prize.mp4] [--preview] [--project 편집기에서_저장한.json] [--workers 4]
// audio/mix.wav (또는 song.mp3/.wav/.m4a) 가 있으면 자동으로 합성합니다.
// --workers N: 브라우저 N개가 구간을 나눠 그린 뒤 이어 붙여요(빠름). 1이면 한 브라우저가 처음부터 끝까지 그려요.
import { chromium } from 'playwright-core';
import { spawn } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, writeFileSync, rmSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';

const dir = path.dirname(fileURLToPath(import.meta.url));
const arg = (k, d) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : d; };
const preview = process.argv.includes('--preview');
const FPS = +arg('--fps', preview ? 15 : 30);
const WORKERS = Math.max(1, +arg('--workers', 1));
const OUT = path.resolve(dir, arg('--out', preview ? `out/nobel_prize_preview.mp4` : `out/nobel_prize.mp4`));
const FFMPEG = process.env.FFMPEG || 'ffmpeg';
const AUDIO_START = process.env.AUDIO_START || '0'; // 노래의 시작 지점(초)
const audio = ["mix.wav", 'song.mp3', 'song.wav', 'song.m4a'].map(f => path.join(dir, 'audio', f)).find(existsSync);
const VIDEO_ARGS = ['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', preview ? 'veryfast' : 'medium', '-crf', preview ? '26' : '18', '-r', String(FPS)];

mkdirSync(path.dirname(OUT), { recursive: true });
async function openPage() {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  await page.goto(pathToFileURL(path.join(dir, 'index.html')).href + '?render');
  await page.evaluate(() => window.ready);
  const projectPath = arg('--project');                  // 영상 편집기에서 저장한 문구·색 (../editor/PROTOCOL.md)
  if (projectPath) await page.evaluate(p => window.VIDEO.apply(p.content), JSON.parse(readFileSync(path.resolve(projectPath), 'utf8')));
  return { browser, page, canvas: await page.$('#c') };
}
const run = (args, stdin) => new Promise((res, rej) => { const p = spawn(FFMPEG, args, { stdio: [stdin ? 'pipe' : 'ignore', 'inherit', 'inherit'] }); p.on('close', c => c === 0 ? res() : rej(new Error(`ffmpeg exit ${c}`))); if (stdin) stdin(p); });
// draw frames [from, to) and pipe them into an ffmpeg process
async function frames(w, from, to, ff, tag) {
  for (let i = from; i < to; i++) {
    await w.page.evaluate(t => window.draw(t), i / FPS);
    const buf = await w.canvas.screenshot({ type: 'png' });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if ((i - from) % (FPS * 10) === 0) process.stdout.write(`${tag}${((i - from) / FPS).toFixed(0)}s / ${((to - from) / FPS).toFixed(0)}s\n`);
  }
  ff.stdin.end();
}
const audioArgs = duration => audio ? ['-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '192k', '-af', `afade=t=in:d=0.3,afade=t=out:st=${duration - 2}:d=2`, '-t', String(duration)] : [];

const first = await openPage();
const duration = await first.page.evaluate(() => window.DURATION);
const total = Math.round(duration * FPS);

if (WORKERS === 1) {
  const args = ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-'];
  if (audio) args.push('-ss', AUDIO_START, '-i', audio);
  await run([...args, ...VIDEO_ARGS, ...audioArgs(duration), '-movflags', '+faststart', OUT], ff => frames(first, 0, total, ff, ''));
  await first.browser.close();
} else {
  await first.browser.close();
  const tmp = path.join(path.dirname(OUT), 'parts'); mkdirSync(tmp, { recursive: true });
  const per = Math.ceil(total / WORKERS), parts = [];
  await Promise.all(Array.from({ length: WORKERS }, async (_, k) => {
    const from = k * per, to = Math.min(total, from + per), part = path.join(tmp, `part${k}.mp4`); parts.push(part);
    const w = await openPage();
    await run(['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-', ...VIDEO_ARGS, part], ff => frames(w, from, to, ff, `[w${k}] `));
    await w.browser.close();
  }));
  const list = path.join(tmp, 'list.txt'); writeFileSync(list, parts.sort().map(p => `file '${p}'`).join('\n'));
  const args = ['-y', '-f', 'concat', '-safe', '0', '-i', list];
  if (audio) args.push('-ss', AUDIO_START, '-i', audio);
  await run([...args, '-c:v', 'copy', ...audioArgs(duration), '-movflags', '+faststart', OUT]);
  rmSync(tmp, { recursive: true, force: true });
}
console.log(`\n완료: ${OUT}${audio ? ` (오디오: ${path.basename(audio)})` : ' (오디오 없음 — audio/mix.wav 를 넣고 다시 렌더링하세요)'}`);
