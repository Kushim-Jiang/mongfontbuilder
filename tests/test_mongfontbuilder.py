from mongfontbuilder.otl import MongFeaComposer
from utils import tempDir


def test_otl() -> None:
    composer = MongFeaComposer(font=None, locales=["MNG"])
    composer.compose()
    code = composer.asFeatureFile().asFea()
    (tempDir / "otl.fea").write_text(code)
