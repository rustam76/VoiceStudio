import { chromium } from 'playwright';
import { mkdir } from 'node:fs/promises';

const key = process.env.OMNIVOICE_API_KEY;
if (!key) throw new Error('OMNIVOICE_API_KEY required');
const base = process.env.VOICESTUDIO_TEST_URL || 'http://127.0.0.1:3900';
const output = process.env.ONLINE_TEST_RESULTS || '/private/tmp/voicestudio-online-results';
await mkdir(output, { recursive: true });
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_EXECUTABLE || undefined });
try {
  const page = await browser.newPage({ locale: 'id-ID', acceptDownloads: true });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('response', response => {
    if (new URL(response.url()).pathname === '/generate') console.log('Generation HTTP', response.status());
  });
  await page.goto(base);
  await page.locator('input[type=password]').fill(key);
  await page.locator('button[type=submit]').click();
  await page.locator('textarea').waitFor();
  await page.locator('textarea').fill('Uji browser: narasi bahasa Indonesia untuk video YouTube.');
  const before = await page.locator('audio').count();
  await page.locator('button[type=submit]').click();
  try {
    await page.waitForFunction(count => document.querySelectorAll('audio').length > count, before, { timeout: 120000 });
  } catch (error) {
    await page.screenshot({ path: output + '/web-ui-failure.png', fullPage: true });
    console.log('Browser errors:', errors);
    throw error;
  }
  const audio = page.locator('audio').first();
  await audio.evaluate(async element => {
    element.load();
    await element.play();
    await new Promise(resolve => setTimeout(resolve, 500));
    if (!(element.currentTime > 0 && element.duration > 0)) throw new Error('Audio playback did not advance');
    element.pause();
  });
  const downloading = page.waitForEvent('download');
  await page.locator('a[download]').first().click();
  await (await downloading).saveAs(output + '/browser-download.wav');
  if ((await page.evaluate(() => JSON.stringify(localStorage))).includes(key)) throw new Error('Master key leaked into localStorage');
  if (errors.length) throw new Error(errors.join('\n'));
  await page.screenshot({ path: output + '/web-ui.png', fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({ path: output + '/web-ui-mobile.png', fullPage: true });
  console.log('Browser login, generation, playback and audio download passed; no page errors.');
} finally {
  await browser.close();
}
