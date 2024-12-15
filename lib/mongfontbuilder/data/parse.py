import json
from pathlib import Path

import yaml
from fontTools import unicodedata

dir = Path(__file__).parent

joiningPositions = ["isol", "init", "medi", "fina"]

with (dir / "characters.yaml").open() as f:
    data = yaml.safe_load(f)

newData = {}
for cp, value in data.items():
    id = value.pop("id", None)
    variants = value.pop("variants", {})
    assert not value, value

    newValue = {
        "alias": {"": id},
        "representativeGlyph": None,
    }
    newData[cp] = newValue

    newVariants = {}
    for position in joiningPositions:
        for variant in variants.pop(position, []):
            newVariant = {}
            newVariants.setdefault(position, []).append(newVariant)
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
                newValue["representativeGlyph"] = [position]
                if fvs:
                    newValue["representativeGlyph"].append(fvs)
            _ = variant.pop("fabricated", None)
            assert not variant, variant
    assert not variants, variants
    if newVariants:
        newValue["variants"] = newVariants

for path in (dir / "locales").iterdir():
    if path.is_dir:
        locale = path.name
        print(locale)
        with (path / "characters.yaml").open() as f:
            data = yaml.safe_load(f)

normalizedData = {}
for cp, value in newData.items():
    normalizedData[unicodedata.name(chr(cp))] = value
    value["alias"] = {k: v.removeprefix(".") for k, v in value["alias"].items() if v}
    if variants := value.get("variants"):
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

(dir / "output.json").write_text(json.dumps(normalizedData, indent=2))
