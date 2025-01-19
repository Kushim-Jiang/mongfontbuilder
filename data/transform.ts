// npx vite-node --script data/transform.ts

import { writeFile } from "node:fs/promises";

import { variants } from "./variants";

for (const [charName, positionToFVSToVariant] of Object.entries(variants)) {
  for (const [position, fvsToVariant] of Object.entries(
    positionToFVSToVariant,
  )) {
    for (const [fvs, variant] of Object.entries(fvsToVariant)) {
      let default_ = false;
      for (const [localeID, localeData] of Object.entries(variant.locales)) {
        if (
          localeData.conditions &&
          localeData.conditions.includes("default")
        ) {
          default_ = true;
          const conditions = localeData.conditions.filter(
            (i) => i != "default",
          );
          if (conditions.length) {
            localeData.conditions = conditions;
          } else {
            localeData.conditions = undefined;
          }
        }
      }
      if (default_) {
        fvsToVariant[fvs] = {
          written: variant.written,
          default: true,
          locales: variant.locales,
        };
      }
    }
  }
}

await writeFile(`new.json`, JSON.stringify(variants, undefined, 2));
