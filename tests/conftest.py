import pytest

from fixtures import buildFontForLocales


@pytest.fixture(scope="session")
def hudum_font():
    return buildFontForLocales(["MNG"])


@pytest.fixture(scope="session")
def manchu_font():
    return buildFontForLocales(["MCH"])


@pytest.fixture(scope="session")
def sibe_font():
    return buildFontForLocales(["SIB"])
