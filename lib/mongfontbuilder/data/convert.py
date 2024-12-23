import json
from pathlib import Path

import yaml
from fontTools import unicodedata

dir = Path(__file__).parent

joiningPositions = ["isol", "init", "medi", "fina"]

with (dir / "characters.yaml").open(encoding="utf-8") as f:
    data = yaml.safe_load(f)

cpToAliases = {}
cpToVariants = {}
for cp, value in data.items():
    id = value.pop("id", None)
    variants = value.pop("variants", None)
    assert not value, value

    aliases = {}
    cpToAliases[cp] = aliases
    if id:
        aliases[""] = id.removeprefix(".")

    if variants:
        newVariants = {}
        for position in joiningPositions:
            for variant in variants.pop(position):
                newVariant = {}
                newVariant["written"] = [i.removeprefix(".") for i in variant.pop("written_units")]
                fvsKey = str(variant.pop("fvs", 0))
                _ = variant.pop("nominal", None)
                _ = variant.pop("fabricated", None)
                assert not variant, variant
                fvsToVariant = newVariants.setdefault(position, {})
                assert fvsKey not in fvsToVariant
                fvsToVariant[fvsKey] = newVariant
        assert not variants, variants
        cpToVariants[cp] = newVariants

folderToGBNumber = {
    "hudum": "GB/T 25914-2023",
    "todo": "GB/T 36649-2018",
    "manchu": "GB/T 36645-2018",
    "sibe": "GB/T 36641-2018",
}

for folder, locale in {
    "hudum": "MNG",
    "hudum-ag": "MNGx",
    "todo": "TOD",
    "todo-ag": "TODx",
    "sibe": "SIB",
    "manchu": "MCH",
    "manchu-ag": "MCHx",
}.items():
    with (dir / "locales" / folder / "characters.yaml").open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    for cp, value in data.items():
        id = value.pop("id", None)
        variants = value.pop("variants", None)
        _ = value.pop("transcription", None)
        assert not value, value

        aliases = cpToAliases[cp]
        alias = id.removeprefix(".")
        if locale.endswith("x"):  # Ali Gali
            parentLocale = locale.removesuffix("x")
            if existing := aliases.get(parentLocale):
                assert alias == existing
            else:
                aliases[parentLocale] = alias
        else:
            aliases[locale] = alias

        if variants:
            newVariants = cpToVariants[cp]
            for position in joiningPositions:
                for variant in variants.pop(position):
                    localeData = {}
                    fvsToVariant = newVariants[position]
                    written = [i.removeprefix(".") for i in variant.pop("written_units")]
                    try:
                        newVariant = next(
                            i for i in fvsToVariant.values() if i["written"] == written
                        )
                    except StopIteration:
                        fvsKey = str(variant.pop("localization_source", 0))
                        newVariant = fvsToVariant[fvsKey]
                        localeData["written"] = written
                    newVariant.setdefault("locales", {}).setdefault(locale, localeData)
                    if conditions := variant.pop("conditions", None):
                        localeData["conditions"] = [i.removeprefix(".") for i in conditions]
                    if gb := variant.pop("gb_index", None):
                        assert gb.pop(0) == folderToGBNumber[folder]
                        cp, name = gb
                        localeData["gb"] = f"{cp:04X} {name}"
                    if eac := variant.pop("eac_index", None):
                        localeData["eac"] = eac
                    _ = variant.pop("fabricated", None)
                    assert not variant, variant
            assert not variants, variants


def makeFallbackReference(
    written: list[str], variants: dict, locale: str | None
) -> tuple[str, int, str | None]:
    [*written], [position, *trailingPositions] = zip(*[i.split(".") for i in written])
    for trailingPosition in trailingPositions:
        position = {
            "init": {
                "medi": "init",
                "fina": "isol",
            },
            "medi": {
                "medi": "medi",
                "fina": "fina",
            },
        }[position][trailingPosition]
    for fvs, variant in variants[position].items():
        if variant["written"] == written:
            return position, int(fvs), None
        if locale:
            if variant["locales"].get(locale, {}).get("written") == written:
                return position, int(fvs), locale
    else:
        raise StopIteration(written, position, variants[position])


filenameToNormalizedData = {
    "aliases.json": {unicodedata.name(chr(k)): v for k, v in sorted(cpToAliases.items())},
    "variants.json": {},
}
for cp, variants in sorted(cpToVariants.items()):
    for position in joiningPositions:
        for variant in variants[position].values():
            written = variant["written"]
            if "." in written[0]:
                variant["written"] = makeFallbackReference(written, variants, None)
            for locale, localeData in variant["locales"].items():
                if written := localeData.get("written"):
                    if "." in written[0]:
                        localeData["written"] = makeFallbackReference(written, variants, locale)
        variants[position] = dict(sorted(variants[position].items()))
    filenameToNormalizedData["variants.json"][unicodedata.name(chr(cp))] = variants

for filename, normalizedData in filenameToNormalizedData.items():
    (dir / filename).write_text(json.dumps(normalizedData, indent=2))
