import csv
from importlib.resources import files
from pathlib import Path

import pytest

import data
from tests.utils import parseAliases, parseLetter, parseWrittenUnits, tempDir


def loadTestCases(font: Path, test_info: dict[str, list[str]]):
    test_cases = []
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
                        parseWrittenUnits(parsedText, Path(font)),
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


@pytest.mark.parametrize(
    ("codes", "index", "result", "goal"),
    loadTestCases(
        tempDir / "build.otf",
        {"eac": ["hud"], "core": ["hud"]},
    ),
)
def test_MNG(index: str, codes: str, result: str, goal: str) -> None:
    assert result == goal, f"ind:  {index}\ncode: {codes}\nres:  {result}\ngoal: {goal}"
