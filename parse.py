from pathlib import Path
from typing import Literal

from fontTools import unicodedata

from mongfontbuilder import dataDir, yaml

repoDir = Path(__file__).parent
tempDir = repoDir / "temp"
tempDir.mkdir(exist_ok=True)

with (dataDir / "characters.yaml").open() as f:
    data = yaml.safe_load(f)

JoiningPosition = Literal["isol", "init", "medi", "fina"]
FvsAssignment = int | None
WrittenUnits = list[str]

charToData = dict[str, dict[JoiningPosition, dict[FvsAssignment, WrittenUnits]]]()
for cp, cpData in sorted(data.items()):
    charName = unicodedata.name(chr(cp))
    variantsData = cpData.pop("variants")
    for position in "isol", "init", "medi", "fina":
        fvsToWrittenUnits = charToData.setdefault(charName, {}).setdefault(position, {})
        for variantData in variantsData.pop(position):
            fvs: int | None = variantData.pop("fvs", None)
            writtenUnits: list[str] = [
                i.removeprefix(".") for i in variantData.pop("written_units")
            ]
            if existing := fvsToWrittenUnits.get(fvs):
                print(
                    "conflicting FVS assignment:",
                    charName,
                    position,
                    fvs,
                    writtenUnits,
                    "vs existing",
                    existing,
                )
            else:
                fvsToWrittenUnits[fvs] = writtenUnits
            _localesWithFabrication = variantData.pop("fabricated", [])
            if _isRepresentativeGlyph := "nominal" in variantData:
                del variantData["nominal"]
            assert not variantData, variantData

    assert not variantsData
    assert not cpData

with (tempDir / "output.yaml").open("w") as f:
    yaml.dump(charToData, f, allow_unicode=True, sort_keys=False)
