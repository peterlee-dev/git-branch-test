// 사용법: node render.mjs [--fps 30] [--out out/edu_platform_team.mp4] [--preview]
// audio/song.mp3 (또는 .wav/.m4a) 가 있으면 자동으로 합성합니다.
import { chromium } from 'playwright-core';
import { spawn } from 'node:child_process';
import { existsSync, mkdirSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';

const dir = path.dirname(fileURLToPath(import.meta.url));
const arg = (k, d) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : d; };
const preview = process.argv.includes('--preview');
const FPS = +arg('--fps', preview ? 15 : 30);
const OUT = path.resolve(dir, arg('--out', preview ? 'out/edu_platform_team_preview.mp4' : 'out/edu_platform_team.mp4'));
const FFMPEG = process.env.FFMPEG || 'ffmpeg';
const AUDIO_START = process.env.AUDIO_START || '0'; // 노래의 시작 지점(초)
const audio = ['mix.wav', 'song.mp3', 'song.wav', 'song.m4a'].map(f => path.join(dir, 'audio', f)).find(existsSync);

mkdirSync(path.dirname(OUT), { recursive: true });
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium' });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
await page.goto(pathToFileURL(path.join(dir, 'index.html')).href + '?render');
await page.evaluate(() => window.ready);
const duration = await page.evaluate(() => window.DURATION);
const frames = Math.round(duration * FPS);

const args = ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-'];
if (audio) args.push('-ss', AUDIO_START, '-i', audio);
args.push('-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', preview ? 'veryfast' : 'medium', '-crf', preview ? '26' : '18', '-r', String(FPS));
if (audio) args.push('-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '192k',
  '-af', `afade=t=in:d=0.3,afade=t=out:st=${duration - 2}:d=2`, '-t', String(duration));
args.push('-movflags', '+faststart', OUT);
const ff = spawn(FFMPEG, args, { stdio: ['pipe', 'inherit', 'inherit'] });

const canvas = await page.$('#c');
for (let i = 0; i < frames; i++) {
  await page.evaluate(t => window.draw(t), i / FPS);
  const buf = await canvas.screenshot({ type: 'png' });
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  if (i % FPS === 0) process.stdout.write(`\r${(i / FPS).toFixed(0)}s / ${duration}s`);
}
ff.stdin.end();
await new Promise(r => ff.on('close', r));
await browser.close();
console.log(`\n완료: ${OUT}${audio ? ` (오디오: ${path.basename(audio)})` : ' (오디오 없음 — audio/song.mp3 를 넣고 다시 렌더링하세요)'}`);
