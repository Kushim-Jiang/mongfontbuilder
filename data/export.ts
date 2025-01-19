// Update data of mongfontbuilder: npx vite-node --script data/export.ts

import { writeFile } from "node:fs/promises";

import { locales, type LocaleID, type Condition } from "./locales";
import { aliases, type LocaleNamespace } from "./aliases";
import { writtenUnits } from "./writtenUnits";
import { variants } from "./variants";

const localeToCategorizedAliases = new Map(
  Object.entries(locales).map(([k, { categories }]) => [
    k,
    Object.values(categories).flatMap((i) => i),
  ]),
);

for (const [charName, positionToFVSToVariant] of Object.entries(variants)) {
  const localeToAlias = aliases[charName];
  if (typeof localeToAlias == "string") {
    continue;
  }

  for (const [position, fvsToVariant] of Object.entries(
    positionToFVSToVariant,
  )) {
    const defaultVariants = Object.values(fvsToVariant).filter(
      ({ default: default_ }) => default_,
    );
    if (defaultVariants.length != 1) {
      throw Error("unique default variant undefined for location", {
        cause: { charName, position, defaultVariants },
      });
    }
  }

  for (const locale of Object.keys(locales) as LocaleID[]) {
    const localeNamespace = (
      locale.endsWith("x") ? locale.slice(0, -1) : locale
    ) as LocaleNamespace;

    for (const fvsToVariant of Object.values(positionToFVSToVariant)) {
      for (const variant of Object.values(fvsToVariant)) {
        if (locale in variant.locales) {
          const alias = localeToAlias[localeNamespace];
          if (!alias) {
            throw Error("locale-specific alias not defined", {
              cause: { charName, locale },
            });
          }
          if (!localeToCategorizedAliases.get(locale)!.includes(alias)) {
            throw Error(
              "character not included in locale-specific categories",
              {
                cause: { charName, locale, alias },
              },
            );
          }
          break;
        }
      }
    }
  }
}

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
