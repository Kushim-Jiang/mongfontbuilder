from mongfontbuilder.otl import MongFeaComposer
from utils import tempDir


def test_fea() -> None:
    composer = MongFeaComposer(cmap={}, glyphs=[], locales=["MNG"])
    composer.compose()
    code = composer.asFeatureFile().asFea()
    (tempDir / "otl.fea").write_text(code)
