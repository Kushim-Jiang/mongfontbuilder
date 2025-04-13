from subprocess import run

from utils import tempDir, testsDir


def main() -> None:
    run(
        [
            "poetry",
            "run",
            "python",
            "-m",
            "mongfontbuilder",
            testsDir / "hudum.ufo",
            tempDir / "build.ufo",
            "--locales",
            "MNG",
        ]
    )


if __name__ == "__main__":
    main()
