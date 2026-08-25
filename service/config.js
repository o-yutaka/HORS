import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const here = path.dirname(fileURLToPath(import.meta.url));
const configPath = path.join(here, "..", "config", "pressure_weights.json");
export const PRESSURE_WEIGHTS = Object.freeze(JSON.parse(readFileSync(configPath, "utf8")));
