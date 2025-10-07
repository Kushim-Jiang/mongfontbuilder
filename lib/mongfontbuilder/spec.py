from dataclasses import dataclass
from typing import Literal

from fontTools.misc.transform import Transform
from ufoLib2.objects import Component, Font


@dataclass
class GlyphSpec:
    components: list[str]
    initPadding: bool = False
    finaPadding: bool = False


@dataclass
class FontSpec:
    cmap: dict[int, str]
    newGlyphs: dict[str, GlyphSpec]
    openTypeCategories: dict[str, Literal["unassigned", "base", "mark", "ligature", "component"]]


def applySpecToFont(
    spec: FontSpec,
    font: Font,
    initPadding: float = 40,
    finaPadding: float = 100,
) -> None:
    """Default implementation for ufoLib2 Font."""

    skipExportGlyphs: list[str] = font.lib.get("public.skipExportGlyphs", [])
    existingCmap = {
        j: i for i in font.keys() if i not in skipExportGlyphs for j in font[i].unicodes
    }

    for name, glyphSpec in spec.newGlyphs.items():
        glyph = font.newGlyph(name)
        if glyphSpec.initPadding:
            glyph.width += initPadding
        for baseGlyph in glyphSpec.components:
            glyph.components.append(Component(baseGlyph, Transform(dx=glyph.width)))
            glyph.width += font[baseGlyph].width
        if glyphSpec.finaPadding:
            glyph.width += finaPadding

    for codePoint, glyphName in spec.cmap.items():
        if existingGlyphName := existingCmap.get(codePoint):
            font[existingGlyphName].unicodes.remove(codePoint)
        font[glyphName].unicode = codePoint

    font.lib.setdefault("public.openTypeCategories", {}).update(spec.openTypeCategories)
