from os import environ
from os.path import relpath
from subprocess import run

from fontTools.ttLib import TTFont
from mongfontbuilder.otl import MongFeaComposer
from ufo2ft import OTFCompiler
from ufo2ft.constants import CFFOptimization
from ufoLib2 import Font

from tests.utils import makeFontFilename, tempDir, testsDir

input = testsDir / "hudum.ufo"
intermediate = tempDir / "build.ufo"


def test_main() -> None:
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


def test_otl() -> None:
    composer = MongFeaComposer(font=None, locales=["MNG"])
    composer.compose()
    code = composer.asFeatureFile().asFea()
    (tempDir / "otl.fea").write_text(code)
