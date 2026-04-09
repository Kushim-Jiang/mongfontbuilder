from os import environ
from os.path import relpath
from subprocess import run

from fontTools.ttLib import TTFont
from ufo2ft import OTFCompiler
from ufo2ft.constants import CFFOptimization
from ufoLib2 import Font

from utils import tempDir, testsDir

FONT_NAME = {
    "MNG": "hudum",
    "SIB": "sibe",
    "MCH": "manchu",
}


def run_font(locale: str):
    font_name = FONT_NAME[locale]
    input = testsDir / f"{font_name}.ufo"
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
            locale,
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

    return output
