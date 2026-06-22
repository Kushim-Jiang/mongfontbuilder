from pathlib import Path

from glyphsLib import GSFeaturePrefix, GSFont, GSFontMaster, GSGlyph, GSInstance, GSLayer
from glyphsLib.builder import GlyphsBuilder
from ufoLib2 import Font

from mongfontbuilder.data.types import LocaleID
from mongfontbuilder.otl import MongFeaComposer
from mongfontbuilder.spec import applySpecToFont

templatesDir = Path(__file__).parent
repo = templatesDir / ".."

CONTROL_GLYPHS = [
    ".notdef",
    "mvs",
    "mvs.narrow",
    "mvs.wide",
    "fvs1",
    "fvs2",
    "fvs3",
    "fvs4",
    "zwj",
    "zwnj",
    "space",
    "nnbsp",
]

MASTER_ID = "E14AE757-7134-4DB9-897C-AD248BACE90D"  # Stable between updates


def _build_template(
    ufo_name: str,
    locales: list[LocaleID],
    fea_filename: str,
    glyphs_filename: str,
    family_name: str,
) -> None:
    font = Font.open(repo / "tests" / ufo_name)
    font._path = None  # glyphsLib expects str and may load from path

    composer = MongFeaComposer(
        cmap={j: i for i in font.keys() for j in font[i].unicodes},
        glyphs=[*font.keys()],
        locales=locales,
    )
    composer.languageSystems["mong"] = {"dflt"}
    spec = composer.compose()
    composer.languageSystems["DFLT"] = {"dflt"}
    fea = composer.asFeatureFile().asFea()

    applySpecToFont(  # Padding disturbs automatic alignment in Glyphs
        spec, font, initPadding=0, finaPadding=0
    )
    font.glyphOrder = [i for i in font.glyphOrder if i not in CONTROL_GLYPHS]
    i = font.info
    assert i.copyright
    i.copyright = "Glyph outlines in this template: " + i.copyright
    i.familyName, i.styleName = family_name, "Regular"
    i.styleMapFamilyName, i.styleMapStyleName = None, None
    i.postscriptFontName = None
    i.ascender, i.capHeight, i.xHeight, i.descender = 800, 700, 500, -200
    i.openTypeVheaVertTypoAscender, i.openTypeVheaVertTypoDescender = None, None
    i.openTypeHeadFlags = None
    i.openTypeHeadLowestRecPPEM = None

    gsFont: GSFont = GlyphsBuilder(ufos=[font]).font
    gsFont.axes.clear()
    gsFont.customParameters["Don't use Production Names"] = True  # type: ignore
    master: GSFontMaster
    [master] = gsFont.masters
    master.id = MASTER_ID
    master.axes.clear()
    gsFont.instances.append(GSInstance())
    prefixes: list[GSFeaturePrefix] = gsFont.featurePrefixes
    prefixes.append(GSFeaturePrefix("mongfontbuilder", f"include({fea_filename});"))
    gsFont.disablesNiceNames = True
    gsFont.format_version = 3
    glyph: GSGlyph
    for glyph in gsFont.glyphs:
        assert glyph.name
        name: str = glyph.name
        if name.startswith("_"):
            glyph.export = False
        glyph.note = None
        layer: GSLayer
        [layer] = glyph.layers
        layer.layerId = layer.associatedMasterId = MASTER_ID
        if not len(layer.paths):
            if layer.components:
                glyph.color = 10  # Light gray
            elif not layer.width:
                glyph.color = 11  # Dark gray
        layer.vertWidth = None
        if name in ["mvs.narrow", "mvs.wide", "fvs4"]:
            glyph.script = "mongolian"
        if spec.openTypeCategories.get(name) == "mark":
            glyph.category, glyph.subCategory = (
                "Mark",
                "Spacing Combining" if layer.width else "Nonspacing",
            )
        elif name in ["fvs1", "fvs2", "fvs3", "fvs4"]:
            glyph.category, glyph.subCategory = "Mark", "Other"
        elif name in ["mvs.narrow", "mvs.wide"]:
            glyph.category, glyph.subCategory = "Separator", "Space"

    (templatesDir / fea_filename).write_text(
        fea.replace(":", ".")  # Glyphs doesn't support ":" in lookup names
    )
    gsFont.save(templatesDir / glyphs_filename)


def update_hudum() -> None:
    """Generate Hudum (Mongolian) template from tests/hudum.ufo."""
    _build_template(
        ufo_name="hudum.ufo",
        locales=["MNG"],
        fea_filename="hudum.fea",
        glyphs_filename="hudum.glyphs",
        family_name="Hudum Template",
    )


def update_manchu() -> None:
    """Generate Manchu template from tests/manchu.ufo."""
    _build_template(
        ufo_name="manchu.ufo",
        locales=["MCH"],
        fea_filename="manchu.fea",
        glyphs_filename="manchu.glyphs",
        family_name="Manchu Template",
    )


def main() -> None:
    update_hudum()
    update_manchu()


if __name__ == "__main__":
    main()
