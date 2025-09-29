from utils import tempDir

from mongfontbuilder.otl import MongFeaComposer


def test_otl() -> None:
    composer = MongFeaComposer(font=None, locales=["MNG"])
    composer.compose()
    code = composer.asFeatureFile().asFea()
    (tempDir / "otl.fea").write_text(code)
