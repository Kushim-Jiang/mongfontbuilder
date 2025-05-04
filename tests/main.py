from os import environ
from os.path import relpath
from subprocess import run

from fontTools.ttLib import TTFont
from ufo2ft import OTFCompiler
from ufo2ft.constants import CFFOptimization
from ufoLib2 import Font
from utils import tempDir, testsDir

input = testsDir / "hudum.ufo"
intermediate = tempDir / "build.ufo"


def main() -> None:
    run(
        ["poetry", "run", "python", "-m", "mongfontbuilder"]
        + [input, intermediate, "--locales", "MNG"]
    )

    compiler = OTFCompiler(
        useProductionNames=False,
        optimizeCFF=CFFOptimization.NONE,
    )
    environ["FONTTOOLS_LOOKUP_DEBUGGING"] = "1"  # For feaLib.builder.Builder
    font: TTFont = compiler.compile(Font.open(intermediate))

    output = tempDir / makeFontFilename(font)
    font.save(output)
    print(relpath(output))


def makeFontFilename(font: TTFont) -> str:
    from fontTools.ttLib.tables._n_a_m_e import table__n_a_m_e

    table: table__n_a_m_e = font["name"]  # type: ignore
    postScriptName = table.getDebugName(6)
    assert postScriptName

    suffix = ".otf" if {"CFF ", "CFF2"}.intersection(font.keys()) else ".ttf"
    return postScriptName + suffix


if __name__ == "__main__":
    main()
