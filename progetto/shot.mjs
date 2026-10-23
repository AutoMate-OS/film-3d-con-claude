// Fotografa l'interfaccia (spenta + ritagli dei pannelli accesi) e le icone dei tasti -> tex/
// Uso: npm install && npx playwright install chromium && node shot.mjs
import { chromium } from 'playwright';
import { mkdirSync } from 'fs';
import { pathToFileURL } from 'url';

const dir = new URL('.', import.meta.url).pathname;
mkdirSync(dir + 'tex', { recursive: true });
const ui = pathToFileURL(dir + 'ui.html').href;
const ic = pathToFileURL(dir + 'icons.html').href;

// Pannelli che si accendono (stesso ordine di PANNELLI in timeline.py), in px dell'interfaccia
const PANNELLI = {
  progetto: { x: 20, y: 170, width: 500, height: 730 },
  anteprima: { x: 540, y: 170, width: 1320, height: 730 },
  effetti: { x: 1880, y: 170, width: 500, height: 730 },
  timeline: { x: 20, y: 920, width: 2360, height: 560 },
};
const TASTI = ['Selezione', 'Mano', 'Testo', 'Rettangolo', 'Penna', 'Bagliore', 'Posizione', 'Zoom'];

const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 2400, height: 1500 } });
await p.goto(ui + '#off'); await p.waitForTimeout(300);
await p.screenshot({ path: dir + 'tex/ui_off.png' });
await p.goto(ui + '#on'); await p.reload(); await p.waitForTimeout(300);
await p.screenshot({ path: dir + 'tex/ui_on.png' });
for (const [n, clip] of Object.entries(PANNELLI)) await p.screenshot({ path: `${dir}tex/p_${n}.png`, clip });

const q = await b.newPage({ viewport: { width: 256, height: 256 } });
for (const t of TASTI) {
  await q.goto(ic + '#' + t); await q.reload(); await q.waitForTimeout(100);
  await q.screenshot({ path: `${dir}tex/i_${t}.png`, omitBackground: true });
}
await b.close();
console.log('ok tex');
