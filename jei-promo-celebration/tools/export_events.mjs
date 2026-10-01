// 영상 페이지에서 등장·착지 시각을 모아 tools/events.json 으로 저장 → make_audio.py 가 이 시각에 효과음을 놓음
import { chromium } from 'playwright-core';
import { writeFileSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';
const dir = path.dirname(fileURLToPath(import.meta.url));
const b = await chromium.launch({ executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium' });
const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
await pg.goto(pathToFileURL(path.join(dir, '..', 'index.html')).href + '?render');
await pg.evaluate(() => window.ready);
const ev = await pg.evaluate(() => window.collectEvents());
writeFileSync(path.join(dir, 'events.json'), JSON.stringify(ev, null, 1));
console.log(`이벤트 ${ev.length}개 저장`);
await b.close();
