// Update data of mongfontbuilder: npx vite-node --script data/export.ts

import { writeFile } from "node:fs/promises";

import { locales } from "./locales";
import { aliases } from "./aliases";
import { writtenUnits } from "./writtenUnits";
import { variants } from "./variants";

for (const [name, data] of Object.entries({
  locales,
  aliases,
  writtenUnits,
  variants,
})) {
  await writeFile(
    `lib/mongfontbuilder/data/${name}.json`,
    JSON.stringify(data, undefined, 2),
  );
}
