from pathlib import Path

from glyphsLib import GSFeaturePrefix, GSFont, GSFontMaster, GSGlyph, GSInstance, GSLayer
from glyphsLib.builder import GlyphsBuilder
from ufoLib2 import Font

from mongfontbuilder.otl import MongFeaComposer
from mongfontbuilder.spec import applySpecToFont

templatesDir = Path(__file__).parent
repo = templatesDir / ".."


def main() -> None:
    font = Font.open(repo / "tests" / "hudum.ufo")
    font._path = None  # glyphsLib expects str and may load from path

    composer = MongFeaComposer(
        cmap={j: i for i in font.keys() for j in font[i].unicodes},
        glyphs=[*font.keys()],
        locales=["MNG"],
    )
    composer.languageSystems["mong"] = {"dflt"}
    spec = composer.compose()
    composer.languageSystems["DFLT"] = {"dflt"}
    fea = composer.asFeatureFile().asFea()

    applySpecToFont(  # Padding disturbs automatic alignment in Glyphs
        spec, font, initPadding=0, finaPadding=0
    )
    font.glyphOrder = [
        i
        for i in font.glyphOrder
        if i
        not in [
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
    ]
    i = font.info
    assert i.copyright
    i.copyright = "Glyph outlines in this template: " + i.copyright
    i.familyName, i.styleName = "Hudum Template", "Regular"
    i.styleMapFamilyName, i.styleMapStyleName = None, None
    i.postscriptFontName = None
    i.ascender, i.capHeight, i.xHeight, i.descender = 800, 700, 500, -200
    i.openTypeVheaVertTypoAscender, i.openTypeVheaVertTypoDescender = None, None
    i.openTypeHeadFlags = None
    i.openTypeHeadLowestRecPPEM = None

    masterID = "E14AE757-7134-4DB9-897C-AD248BACE90D"  # Stable between updates
    gsFont: GSFont = GlyphsBuilder(ufos=[font]).font
    gsFont.axes.clear()
    master: GSFontMaster
    [master] = gsFont.masters
    master.id = masterID
    master.axes.clear()
    gsFont.instances.append(GSInstance())
    prefixes: list[GSFeaturePrefix] = gsFont.featurePrefixes
    prefixes.append(GSFeaturePrefix("mongfontbuilder", "include(hudum.fea);"))
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
        layer.layerId = layer.associatedMasterId = masterID
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

    (templatesDir / "hudum.fea").write_text(
        fea.replace(":", ".")  # Glyphs doesn't support ":" in lookup names
    )
    gsFont.save(templatesDir / "hudum.glyphs")


if __name__ == "__main__":
    main()
