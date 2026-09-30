// 편집본(작업 파일)을 최고 화질 MP4 로: node editor/render.mjs 작업파일.json [--out out.mp4] [--fps 30]
// 저장소 맨 위를 잠깐 로컬 서버로 열고, 편집기 페이지(?render)에서 한 장씩 그려 ffmpeg 로 묶음
// 필요: 각 영상 폴더의 npm install (playwright-core), audio/mix.wav, FFMPEG(없으면 ffmpeg), CHROMIUM(없으면 /opt/pw-browsers/chromium)
import { createServer } from 'node:http';
import { readFileSync, writeFileSync, existsSync, statSync, mkdirSync } from 'node:fs';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
import path from 'node:path';
import os from 'node:os';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const argv = process.argv.slice(2), arg = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d; };
const projectFile = argv.find(a => a.endsWith('.json'));
if (!projectFile) { console.error('사용법: node editor/render.mjs 작업파일.json [--out out.mp4]'); process.exit(1); }
const project = JSON.parse(readFileSync(projectFile, 'utf8'));
const OUT = path.resolve(arg('--out', 'out/edit.mp4')), FFMPEG = process.env.FFMPEG || 'ffmpeg';
const pwDir = ['ai-math-trailer', 'jei-promo', 'pythagoras'].map(d => path.join(root, d, 'node_modules', 'playwright-core')).find(existsSync);
if (!pwDir) { console.error('playwright-core 가 없어요. 영상 폴더 하나에서 npm install 을 먼저 하세요.'); process.exit(1); }
const { chromium } = createRequire(import.meta.url)(pwDir);

const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json', '.ttf': 'font/ttf', '.wav': 'audio/wav', '.mp3': 'audio/mpeg', '.png': 'image/png', '.jpg': 'image/jpeg' };
const server = createServer((req, res) => {
  const p = path.join(root, decodeURIComponent(new URL(req.url, 'http://x').pathname));
  if (!p.startsWith(root) || !existsSync(p) || statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'content-type': TYPES[path.extname(p)] || 'application/octet-stream' }); res.end(readFileSync(p));
}).listen(0);
const port = server.address().port;

const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } });
page.on('pageerror', e => console.error('페이지 오류:', e.message));
await page.goto(`http://127.0.0.1:${port}/video-editor.html?render`);
await page.waitForFunction(() => window.EDITOR);
await page.evaluate(p => EDITOR.loadProject(p), project);
await page.waitForFunction(() => EDITOR.ready, null, { timeout: 300000 });
const total = await page.evaluate(() => EDITOR.total), FPS = +arg('--fps', 30), frames = Math.round(total * FPS);

const wav = path.join(os.tmpdir(), `jei_edit_${process.pid}.wav`);
writeFileSync(wav, Buffer.from(await page.evaluate(() => EDITOR.wavBase64()), 'base64'));
mkdirSync(path.dirname(OUT), { recursive: true });
const ff = spawn(FFMPEG, ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-', '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'medium', '-crf', '18', '-r', String(FPS), '-c:a', 'aac', '-b:a', '192k', '-t', String(total), '-movflags', '+faststart', OUT], { stdio: ['pipe', 'inherit', 'inherit'] });
for (let i = 0; i < frames; i++) {
  const url = await page.evaluate(t => EDITOR.frame(t), i / FPS);
  if (!ff.stdin.write(Buffer.from(url.slice(url.indexOf(',') + 1), 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
  if (i % FPS === 0) process.stdout.write(`\r${(i / FPS).toFixed(0)}s / ${total.toFixed(1)}s`);
}
ff.stdin.end(); await new Promise(r => ff.on('close', r));
await browser.close(); server.close();
console.log(`\n완료: ${OUT} (${total.toFixed(1)}초, 장면 ${project.clips ? project.clips.length : 1}개)`);
