import csv
from importlib.resources import files
from os import environ
from os.path import relpath
from pathlib import Path
from subprocess import run

import pytest
from _pytest.mark.structures import ParameterSet
from fontTools.ttLib import TTFont
from ufo2ft import OTFCompiler
from ufo2ft.constants import CFFOptimization
from ufoLib2 import Font

import data
from utils import parseAliases, parseLetter, parseWrittenUnits, tempDir, testsDir

input = testsDir / "hudum.ufo"
intermediate = tempDir / input.name
output = intermediate.with_suffix(".otf")

run(
    [
        "uv",
        "run",
        "--locked",
        "python",
        "-m",
        "mongfontbuilder",
        input,
        intermediate,
        "--locales",
        "MNG",
    ]
)

compiler = OTFCompiler(
    useProductionNames=False,
    optimizeCFF=CFFOptimization.NONE,
)
environ["FONTTOOLS_LOOKUP_DEBUGGING"] = "1"  # For feaLib.builder.Builder
font: TTFont = compiler.compile(Font.open(intermediate))

font.save(output)
print(relpath(output))


def loadTestCases(
    font: Path,
    test_info: dict[str, list[str]],
) -> list[tuple[str, str, str, str] | ParameterSet]:
    test_cases = list[tuple[str, str, str, str] | ParameterSet]()
    for testSet, locales in test_info.items():
        for locale in locales:
            file_path = files(data) / f"{testSet}-{locale}.tsv"
            with open(file_path, "r", encoding="utf-8") as f:  # type: ignore
                rules = [
                    tuple(i)
                    for i in csv.reader(f, delimiter="\t")
                    if i and not i[0].startswith("#")
                ]
            for index, letters, goal in rules:
                try:
                    parsedText = parseLetter(letters, locale)
                    test_case = (
                        f"{testSet}-{locale} > {index}",
                        parseAliases(parsedText, locale),
                        parseWrittenUnits(parsedText, font),
                        goal,
                    )

                    if index == "XIM11-46" and testSet == "eac" and locale == "hud":
                        test_cases.append(
                            pytest.param(
                                *test_case,
                                marks=pytest.mark.xfail(
                                    reason="The EAC spec expects an invalid FVS after a letter to prevent the MVS shaping step. The UTN model disagrees."
                                ),
                            )
                        )
                    elif index == "XIM11-1012" and testSet == "eac" and locale == "hud":
                        test_cases.append(
                            pytest.param(
                                *test_case,
                                marks=pytest.mark.xfail(
                                    reason="When an FVS after a letter prevents the MVS shaping step, the MVS is treated as an NBSP. In this case, the FVS remains valid. The UTN model considers this test case incorrect."
                                ),
                            )
                        )
                    elif (
                        index in ["XIM11-39", "XIM11-40", "XIM11-41"]
                        and testSet == "eac"
                        and locale == "hud"
                    ):
                        test_cases.append(
                            pytest.param(
                                *test_case,
                                marks=pytest.mark.xfail(
                                    reason="The EAC spec assumes that all features of NNBSP should be disabled. The UTN model considers this test case incorrect. The UTN model considers that the old functionality of NNBSP should be retained."
                                ),
                            )
                        )
                    else:
                        test_cases.append(test_case)
                except AssertionError as e:
                    pytest.fail(
                        f"ind:  {testSet}-{locale} > {index}\n"
                        f"code: {letters}\n"
                        f"parsedText: {parsedText}\n"
                        f"err:  \n  {e}"
                    )
    return test_cases
