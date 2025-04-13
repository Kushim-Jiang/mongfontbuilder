// Update data of mongfontbuilder: npx vite-node --script data/export.ts

import { writeFile } from "node:fs/promises";

import { locales, type ConditionalMappingType, type LocaleID } from "./locales";
import { aliases, type LocaleNamespace } from "./aliases";
import { writtenUnits } from "./writtenUnits";
import { ligatures } from "./ligatures";
import { variants } from "./variants";
import { particles } from "./particles";

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
      (i) => i.default,
    );
    if (defaultVariants.length != 1) {
      throw Error("unique default variant undefined for location", {
        cause: { charName, position, defaultVariants },
      });
    }
  }

  for (const [locale, { conditions }] of Object.entries(locales)) {
    const localeNamespace = (
      locale.endsWith("x") ? locale.slice(0, -1) : locale
    ) as LocaleNamespace;

    for (const fvsToVariant of Object.values(positionToFVSToVariant)) {
      for (const variant of Object.values(fvsToVariant)) {
        const variantLocaleData = variant.locales[locale as LocaleID];
        if (variantLocaleData) {
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
          for (const condition of variantLocaleData.conditions ?? []) {
            if (!(conditions as ConditionalMappingType[]).includes(condition)) {
              throw Error("condition not defined for locale", {
                cause: { locale, conditions, condition },
              });
            }
          }
        }
      }
    }
  }
}

for (const [name, data] of Object.entries({
  locales,
  aliases,
  writtenUnits,
  ligatures,
  variants,
  particles,
})) {
  await writeFile(
    `lib/mongfontbuilder/data/${name}.json`,
    JSON.stringify(data, undefined, 2).replace(/\n/g, "\r\n"),
  );
}
