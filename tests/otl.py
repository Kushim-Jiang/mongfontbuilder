from pathlib import Path

from mongfontbuilder.data import locales
from mongfontbuilder.otl import compose


def main() -> None:
    composer = compose(locales=[*locales.keys()])
    with open(Path(__file__).parent / "build.fea", "w") as file:
        file.write(composer.asFeatureFile().asFea())


if __name__ == "__main__":
    main()
