import { seedEvents } from "./data.js";
import { processEvents } from "./core.js";
import { writeFile, mkdir } from "node:fs/promises";
await mkdir("./service/runtime", { recursive: true });
const state = processEvents(seedEvents);
await writeFile("./service/runtime/seed-state.json", JSON.stringify(state, null, 2));
console.log(`seeded ${state.decisionDebts.length} Decision Debt records`);
