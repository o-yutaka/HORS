import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

const ROOT = path.resolve("service/public_data");
const REGISTRY = JSON.parse(fs.readFileSync(path.join(ROOT, "registry.json"), "utf8"));
const RAW = path.resolve(".public-data", "raw");
const OUT = path.resolve(".public-data", "manifests");

function sha256(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function writeManifest(source, files = []) {
  fs.mkdirSync(OUT, { recursive: true });
  const manifest = {
    source_id: source.id,
    source_name: source.name,
    official_url: source.official_url,
    generated_at: new Date().toISOString(),
    files: files.map((file) => ({
      path: path.relative(RAW, file),
      sha256: sha256(file),
      bytes: fs.statSync(file).size
    }))
  };
  const destination = path.join(OUT, `${source.id}.json`);
  fs.writeFileSync(destination, JSON.stringify(manifest, null, 2) + "\n");
  return destination;
}

function main() {
  const sourceId = process.argv[2];
  const sources = sourceId ? REGISTRY.sources.filter((source) => source.id === sourceId) : REGISTRY.sources;
  if (!sources.length) throw new Error(`Unknown public-data source: ${sourceId}`);
  for (const source of sources) {
    const dir = path.join(RAW, source.id);
    const files = fs.existsSync(dir)
      ? fs.readdirSync(dir, { withFileTypes: true }).filter((entry) => entry.isFile()).map((entry) => path.join(dir, entry.name))
      : [];
    const manifest = writeManifest(source, files);
    console.log(manifest);
  }
}

main();
