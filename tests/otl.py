from mongfontbuilder.data import locales
from mongfontbuilder.otl import MongFeaComposer
from utils import tempDir


def main() -> None:
    composer = MongFeaComposer(locales=[*locales.keys()])
    code = composer.asFeatureFile().asFea()
    (tempDir / "otl.fea").write_text(code)


if __name__ == "__main__":
    main()
