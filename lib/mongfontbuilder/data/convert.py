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
                newVariant["written"] = variant.pop("written_units")
                fvs = None
                try:
                    fvs = variant.pop("fvs")
                except KeyError:
                    pass
                else:
                    newVariant["fvs"] = fvs
                _ = variant.pop("nominal", None)
                _ = variant.pop("fabricated", None)
                assert not variant, variant
                newVariants.setdefault(position, []).append(newVariant)
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
                    newVariantsOnPosition = newVariants.get(position, [])
                    written = variant.pop("written_units")
                    try:
                        newVariant = next(
                            i for i in newVariantsOnPosition if i["written"] == written
                        )
                    except StopIteration:
                        localizingTarget = variant.pop("localizing", 0)
                        newVariant = next(
                            i for i in newVariantsOnPosition if i.get("fvs", 0) == localizingTarget
                        )
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


def normalizeWritten(written: list[str]) -> list[str]:
    written = [i.removeprefix(".") for i in written]
    if "." in written[0]:
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
        written.append(position)
    return written


filenameToNormalizedData = {
    "aliases.json": {unicodedata.name(chr(k)): v for k, v in sorted(cpToAliases.items())},
    "variants.json": {},
}
for cp, variants in sorted(cpToVariants.items()):
    for position in joiningPositions:
        fvsToVariant = dict[str, dict]()
        for variant in variants[position]:
            key = str(variant.pop("fvs", 0))
            assert key not in fvsToVariant
            fvsToVariant[key] = variant
            variant["written"] = normalizeWritten(variant["written"])
            for locale, localeData in variant["locales"].items():
                if written := localeData.get("written"):
                    localeData["written"] = normalizeWritten(written)
        variants[position] = dict(sorted(fvsToVariant.items()))
    filenameToNormalizedData["variants.json"][unicodedata.name(chr(cp))] = variants

for filename, normalizedData in filenameToNormalizedData.items():
    (dir / filename).write_text(json.dumps(normalizedData, indent=2))
