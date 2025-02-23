from mongfontbuilder.data import locales
from mongfontbuilder.otl import compose

from utils import tempDir


def main() -> None:
    composer = compose(locales=[*locales.keys()])
    code = composer.asFeatureFile().asFea()
    (tempDir / "otl.fea").write_text(code)


if __name__ == "__main__":
    main()
