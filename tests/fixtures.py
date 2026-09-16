import csv
from importlib.resources import files
from os import environ
from os.path import relpath
from pathlib import Path

import pytest
from _pytest.mark.structures import ParameterSet
from fontTools.ttLib import TTFont
from ufo2ft import OTFCompiler
from ufo2ft.constants import CFFOptimization
from ufoLib2 import Font

import data
from mongfontbuilder.data.types import LocaleID
from mongfontbuilder.otl import MongFeaComposer
from mongfontbuilder.spec import applySpecToFont
from utils import tempDir, testsDir

FONT_NAME = {
    "MNG": "hudum",
    "SIB": "sibe",
    "MCH": "manchu",
}

# The EAC cases the font answers differently from the EAC spec. The UTN model is taken as
# the correct one, so such a case is marked as an expected failure rather than being taken
# out of the suite; the reasoning of each is in the README, under "Tests".
FVS_LOCALE = (
    "The EAC spec expects the FVS to be invalid here, because the locale is not the one it "
    "expects, but the meeting held that the effect of an FVS does not depend on the locale, "
    "so the FVS stays valid and selects its variant."
)
NNBSP = (
    "The EAC spec assumes that every feature of NNBSP should be disabled. The UTN model "
    "holds that the old functionality of NNBSP should be retained."
)
MVS_FINA = (
    "The EAC spec takes an FVS after a letter to prevent the MVS shaping step, and the MVS "
    "then to be an NBSP, which leaves the FVS valid. The UTN model holds that a letter "
    "before an MVS is in the fina position, so the FVS after it selects the fina variant."
)

# The cases every font this project builds answers differently, marked where the suites are
# loaded. A font that writes with one writing system alone answers the cases below it as
# the EAC expects, which is why they are marked by `test_unified.py` instead.
EAC_XFAIL: dict[str, str] = {
    "XIM11-39": NNBSP,
    "XIM11-40": NNBSP,
    "XIM11-41": NNBSP,
    "XIM11-46": FVS_LOCALE,
    "XIM11-1012": MVS_FINA,
}

EAC_UNIFIED_XFAIL: dict[str, str] = {
    "eac-hud > MND11-2": FVS_LOCALE,
    "eac-hud > MNM10-2": FVS_LOCALE,
    "eac-hud > MNM11-2": FVS_LOCALE,
    "eac-hud > MNS11-26": FVS_LOCALE,
    "eac-hud > MNZ11-3": FVS_LOCALE,
    "eac-hud > MNZ21-5": FVS_LOCALE,
    "eac-hud > XIM11-11": FVS_LOCALE,
    "eac-hud > XIM11-675": FVS_LOCALE,
    "eac-hud > XIM11-678": FVS_LOCALE,
    "eac-hud > XIM11-681": FVS_LOCALE,
    "eac-hud > XIM11-684": FVS_LOCALE,
    "eac-hud > XIM11-687": FVS_LOCALE,
    "eac-hud > XIM11-690": FVS_LOCALE,
    "eac-hud > XIM11-694": FVS_LOCALE,
}


def buildFontForLocales(locales: list[LocaleID]) -> Path:
    fontName = FONT_NAME[locales[0].removesuffix("x")]
    output = tempDir / f"{fontName}.otf"

    if output.exists():
        return output

    font = Font.open(testsDir / f"{fontName}.ufo")
    c = MongFeaComposer(
        cmap={j: i for i in font.keys() for j in font[i].unicodes},
        glyphs=[*font.keys()],
        locales=locales,
    )
    spec = c.compose()
    applySpecToFont(spec, font)
    font.features.text = c.asFeatureFile().asFea()

    tempDir.mkdir(parents=True, exist_ok=True)
    intermediate = tempDir / f"{fontName}.ufo"
    font.save(intermediate, overwrite=True)

    compileOTF(font).save(output)
    print(relpath(output))
    return output


def compileOTF(font: Font) -> TTFont:
    compiler = OTFCompiler(
        useProductionNames=False,
        optimizeCFF=CFFOptimization.NONE,
    )
    environ["FONTTOOLS_LOOKUP_DEBUGGING"] = "1"  # For feaLib.builder.Builder
    return compiler.compile(font)


def loadRawTestCases(
    test_info: dict[str, list[str]],
    font_type: str,
) -> list[tuple[str, str, str, str] | ParameterSet]:
    test_cases = list[tuple[str, str, str, str] | ParameterSet]()
    for testSet, locales in test_info.items():
        for locale in locales:
            file_path = files(data) / f"{testSet}-{locale}.tsv"
            with open(file_path, encoding="utf-8") as f:  # type: ignore
                rules = [
                    tuple(i)
                    for i in csv.reader(f, delimiter="\t")
                    if i and not i[0].startswith("#")
                ]
            for index, letters, goal in rules:
                test_case = (f"{testSet}-{locale} > {index}", letters, locale, goal)
                if font_type == "MNG" and testSet == "eac" and locale == "hud":
                    reason = EAC_XFAIL.get(index)
                    if reason:
                        test_cases.append(
                            pytest.param(*test_case, marks=pytest.mark.xfail(reason=reason))
                        )
                        continue
                test_cases.append(test_case)
    return test_cases
