from mongfontbuilder.data import locales
from mongfontbuilder.otl import MongFeaComposer
from ufoLib2 import Font
from utils import tempDir


def main() -> None:
    composer = MongFeaComposer(font=Font(), locales=[*locales.keys()], otlOnly=True)
    code = composer.asFeatureFile().asFea()
    (tempDir / "otl.fea").write_text(code)


if __name__ == "__main__":
    main()
