// 사용법: node tools/snap.mjs out/snaps 3.5 10 22.1 ...  → 지정한 시각의 프레임을 PNG로 (확인용)
import { chromium } from 'playwright-core';
import { mkdirSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';
const dir = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const [out, ...times] = process.argv.slice(2); mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
const errs = []; page.on('pageerror', e => errs.push(e.message)); page.on('console', m => m.type() === 'error' && errs.push(m.text()));
await page.goto(pathToFileURL(path.join(dir, 'index.html')).href + '?render'); await page.evaluate(() => window.ready);
for (const t of times) { await page.evaluate(t => window.draw(t), +t); await (await page.$('#c')).screenshot({ path: path.join(out, `t${(+t).toFixed(1).padStart(6, '0')}.png`) }); }
if (errs.length) console.log('ERR', errs.join('\n')); await browser.close();
