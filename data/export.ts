// Execute from this directory to export to and update mongfontbuilder:
//   npx vite-node --script export.ts

import { writeFile } from "node:fs/promises";

import { joiningPositions } from ".";
import { writtenUnits } from "./writtenUnits";
import { letters } from "./letters";
import { categories } from "./categories";

const data = { joiningPositions, writtenUnits, letters, categories };
await writeFile(
  "../lib/mongfontbuilder/data.json",
  JSON.stringify(data, undefined, 2),
);
