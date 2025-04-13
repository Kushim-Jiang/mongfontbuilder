from os.path import relpath
from subprocess import run

from fontTools.ttLib import TTFont
from ufo2ft import OTFCompiler
from ufoLib2 import Font
from utils import tempDir, testsDir


def main() -> None:
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
    print(relpath(output))


if __name__ == "__main__":
    main()
