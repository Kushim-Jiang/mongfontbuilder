from os import environ, path
from subprocess import run

from fontTools.ttLib import TTFont
from ufo2ft import OTFCompiler
from ufoLib2 import Font
from utils import tempDir, testsDir


def main(debug: bool = False) -> None:
    if debug:
        environ["FONTTOOLS_LOOKUP_DEBUGGING"] = "1"

    output = tempDir / "build.ufo"
    run(
        [
            "poetry",
            "run",
            "python",
            "-m",
            "mongfontbuilder",
            testsDir / "hudum.ufo",
            output,
            "--locales",
            "MNG",
        ]
    )

    font: TTFont = OTFCompiler().compile(Font.open(output))

    output = output.with_suffix(".otf")
    font.save(output)
    print(path.relpath(output))


if __name__ == "__main__":
    main(debug=True)
