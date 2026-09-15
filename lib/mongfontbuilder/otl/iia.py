from fontTools import unicodedata

from .. import GlyphDescriptor, data, uNameFromCodePoint
from ..data import codePointToCmapVariant
from ..data.types import joiningPositions
from ..spec import GlyphSpec
from . import MongFeaComposer

# Letters that lie outside every writing system. Each is written with a written unit of
# its own, which no character of the data writes with, so nothing else reaches its joining
# forms, and its character glyph is built from that unit rather than stored in the source
# font.
OUTSIDE_WRITTEN_UNITS = {0x1878: "Cx", 0x1898: "Dz"}


def coversEveryWritingSystem(c: MongFeaComposer) -> bool:
    """Whether the font is composed for every writing system the data knows."""

    targeted = {i.removesuffix("x") for i in c.locales}
    return targeted == {i.removesuffix("x") for i in data.locales}


def initOutsideLetters(c: MongFeaComposer) -> dict[int, str]:
    """
    Register the character glyph of each letter outside every writing system.

    Such a letter draws its isolated form as the shape of the first form its written unit
    has, which is the initial one, and it is not a source glyph: the font builds it from
    that shape, which is also how it gets its cmap entry.
    """

    outside: dict[int, str] = {}
    for codePoint, unit in OUTSIDE_WRITTEN_UNITS.items():
        default = next(
            (
                member
                for position in ("isol", "init", "medi", "fina")
                if (member := f"_{unit}.{position}") in c.glyphs
            ),
            None,
        )
        if default is None:
            # A source font without the written unit draws no such letter.
            continue
        name = c.glyphNameProcessor(uNameFromCodePoint(codePoint))
        c.spec.cmap[codePoint] = name
        c.spec.newGlyphs.setdefault(name, GlyphSpec([c.glyphNameProcessor(default)]))
        outside[codePoint] = unit
    return outside


def compose(c: MongFeaComposer) -> None:
    """
    **Phase IIa.1: Initiation of cursive positions**

    The letters that lie outside every writing system take their joining forms here as
    well, but only where the font covers every writing system: they are written with
    written units no character of the data writes with.
    """

    localeSet = {*c.locales}
    outside = initOutsideLetters(c) if coversEveryWritingSystem(c) else {}
    for position in joiningPositions:
        with c.Lookup(f"IIa.{position}", feature=position):
            for charName, positionToFVSToVariant in data.variants.items():
                codePoint = ord(unicodedata.lookup(charName))
                # A character written differently in every writing system has no
                # cross-locale default, so no glyph of it exists to be mapped here.
                if codePoint not in codePointToCmapVariant:
                    continue
                writtenIn = any(
                    localeSet.intersection(i.locales)
                    for i in positionToFVSToVariant[position].values()
                )
                if not writtenIn:
                    continue
                default = c.defaultVariant(charName, position)
                c.sub(uNameFromCodePoint(codePoint), by=default)
            for codePoint, unit in outside.items():
                member = f"_{unit}.{position}"
                if member not in c.glyphs:
                    # A source font without the written unit draws no such form.
                    continue
                glyph = str(GlyphDescriptor([codePoint], [unit], position))
                c.spec.newGlyphs[c.glyphNameProcessor(glyph)] = GlyphSpec(
                    [c.glyphNameProcessor(member)]
                )
                c.sub(uNameFromCodePoint(codePoint), by=glyph)
