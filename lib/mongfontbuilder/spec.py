from collections.abc import Iterator
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

    for name, glyphSpec in orderedNewGlyphs(spec, font):
        # A glyph the source font already carries keeps the drawing it came with: the
        # spec names the glyphs a variant is built from, and a drawn written form is a
        # drawing of the font maker's, not one the spec replaces. Only the components
        # the spec adds are appended, so a source glyph that is drawn stays drawn.
        glyph = font[name] if name in font else font.newGlyph(name)
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


def orderedNewGlyphs(spec: FontSpec, font: Font) -> Iterator[tuple[str, GlyphSpec]]:
    """The glyphs of the spec, each after the glyphs it is drawn from.

    The spec is written in the order the composition thinks in, which is not the order the
    glyphs can be drawn in: a variant is specified where the character it belongs to is
    resolved, and the written form it is drawn from may be specified later, by a phase that
    supplies what the source font lacks. A glyph is therefore drawn after every glyph of
    the spec it is a component of, and glyphs that are not drawn from one another keep the
    order the spec gives them.
    """

    drawn = set(font.keys())
    remaining = dict(spec.newGlyphs)
    while remaining:
        ready = [
            name
            for name, glyphSpec in remaining.items()
            if all(i in drawn or i not in spec.newGlyphs for i in glyphSpec.components)
        ]
        if not ready:
            # The components of what is left are missing from the spec and from the font,
            # so no order of the spec can draw them; they are left to the font's own error.
            yield from remaining.items()
            return
        for name in ready:
            yield name, remaining.pop(name)
            drawn.add(name)
