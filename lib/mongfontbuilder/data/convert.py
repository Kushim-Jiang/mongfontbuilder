import json
from pathlib import Path

import yaml
from fontTools import unicodedata

dir = Path(__file__).parent

joiningPositions = ["isol", "init", "medi", "fina"]

with (dir / "characters.yaml").open(encoding="utf-8") as f:
    data = yaml.safe_load(f)

newData = {}
for cp, value in data.items():
    id = value.pop("id", None)
    variants = value.pop("variants", None)
    assert not value, value

    newValue = {"alias": {"": id}}
    newData[cp] = newValue

    if variants:
        newVariants = {}
        newVariants["representative"] = None
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
                try:
                    nominal = variant.pop("nominal")
                except KeyError:
                    pass
                else:
                    assert nominal is None
                    newVariants["representative"] = [position]
                    if fvs:
                        newVariants["representative"].append(fvs)
                _ = variant.pop("fabricated", None)
                assert not variant, variant
                newVariants.setdefault(position, []).append(newVariant)
        assert not variants, variants
        newValue["variants"] = newVariants

for locale, gbNumber in {
    "hudum": "GB/T 25914-2023",
    "hudum-ag": None,
    "todo": "GB/T 36649-2018",
    "todo-ag": None,
    "manchu": "GB/T 36645-2018",
    "manchu-ag": None,
    "sibe": "GB/T 36641-2018",
}.items():
    with (dir / "locales" / locale / "characters.yaml").open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    for cp, value in data.items():
        id = value.pop("id", None)
        variants = value.pop("variants", None)
        _ = value.pop("transcription", None)
        assert not value, value

        newValue = newData.get(cp)
        if not newValue:
            newValue = {"alias": {}}
            newData[cp] = newValue
        newValue["alias"][locale] = id

        if variants:
            newVariants = newValue.setdefault("variants", {"representative": None})
            for position in joiningPositions:
                for variant in variants.pop(position):
                    written = variant.pop("written_units")
                    try:
                        newVariant = next(
                            i for i in newVariants.get(position, []) if i["written"] == written
                        )
                    except StopIteration:
                        newVariant = {"written": written}
                        newVariants.setdefault(position, []).append(newVariant)

                    localeData = {}
                    newVariant.setdefault("locales", {}).setdefault(locale, localeData)
                    if conditions := variant.pop("conditions", None):
                        localeData["conditions"] = [i.removeprefix(".") for i in conditions]
                    if gb := variant.pop("gb_index", None):
                        assert gb.pop(0) == gbNumber
                        cp, name = gb
                        localeData["gb"] = f"{cp:04X} {name}"
                    if eac := variant.pop("eac_index", None):
                        localeData["eac"] = eac
                    _ = variant.pop("fabricated", None)
                    assert not variant, variant
            assert not variants, variants

normalizedData = {}
for cp, value in sorted(newData.items()):
    normalizedData[unicodedata.name(chr(cp))] = value
    alias = {k: v.removeprefix(".") for k, v in value["alias"].items() if v}
    if len({*alias.values()}) == 1:
        alias, *_ = alias.values()
    value["alias"] = alias
    if variants := value.get("variants"):
        assert variants["representative"]
        for position in joiningPositions:
            for variant in variants[position]:
                written = [i.removeprefix(".") for i in variant["written"]]
                if "." in written[0]:
                    [*written], [position, *trailingPositions] = zip(
                        *[i.split(".") for i in written]
                    )
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
                variant["written"] = written

(dir / "characters.json").write_text(json.dumps(normalizedData, indent=2))
