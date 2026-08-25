import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';

const DEFAULT_PAGE = 'https://www.e-stat.go.jp/stat-search/files?stat_infid=000040475580';
const OUT = path.resolve('service/runtime/public_data/estat/2026-05');

function sha256(buffer) {
  return crypto.createHash('sha256').update(buffer).digest('hex');
}

function absolute(base, href) {
  return new URL(href, base).toString();
}

function discoverExcel(pageUrl, html) {
  const candidates = [...html.matchAll(/href=["']([^"']+)["'][^>]*>\s*(?:<[^>]+>\s*)*EXCEL/i)]
    .map((m) => absolute(pageUrl, m[1]));
  if (!candidates.length) {
    throw new Error('EXCEL_DOWNLOAD_LINK_NOT_FOUND');
  }
  return candidates[0];
}

const pageUrl = process.argv[2] || DEFAULT_PAGE;
const page = await fetch(pageUrl, { redirect: 'follow' });
if (!page.ok) throw new Error(`SOURCE_PAGE_HTTP_${page.status}`);
const html = await page.text();
const downloadUrl = discoverExcel(pageUrl, html);
const artifact = await fetch(downloadUrl, { redirect: 'follow' });
if (!artifact.ok) throw new Error(`ARTIFACT_HTTP_${artifact.status}`);
const bytes = Buffer.from(await artifact.arrayBuffer());

await fs.mkdir(OUT, { recursive: true });
const contentType = artifact.headers.get('content-type') || 'application/octet-stream';
const fileName = `estat-000040475580-${sha256(bytes).slice(0, 12)}.bin`;
const rawPath = path.join(OUT, fileName);
await fs.writeFile(rawPath, bytes);

const provenance = {
  dataset_id: 'estat-000040475580',
  source_id: 'estat_construction_orders',
  source_url: pageUrl,
  download_url: downloadUrl,
  retrieved_at: new Date().toISOString(),
  published_at: '2026-07-10T14:00:00+09:00',
  content_type: contentType,
  bytes: bytes.length,
  artifact_sha256: sha256(bytes),
  raw_path: rawPath.replaceAll(path.sep, '/')
};
await fs.writeFile(path.join(OUT, 'provenance.json'), JSON.stringify(provenance, null, 2));
console.log(JSON.stringify(provenance, null, 2));
