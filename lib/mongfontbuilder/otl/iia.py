from fontTools import unicodedata

from .. import data, uNameFromCodePoint
from ..data import codePointToCmapVariant
from ..data.types import joiningPositions
from . import MongFeaComposer


def compose(c: MongFeaComposer) -> None:
    """
    **Phase IIa.1: Initiation of cursive positions**
    """

    localeSet = {*c.locales}
    for position in joiningPositions:
        with c.Lookup(f"IIa.{position}", feature=position):
            for charName, positionToFVSToVariant in data.variants.items():
                codePoint = ord(unicodedata.lookup(charName))
                # A character written differently in every writing system has no
                # cross-locale default, so no glyph of it exists to be mapped here.
                if codePoint not in codePointToCmapVariant:
                    continue
                if any(
                    localeSet.intersection(i.locales)
                    for i in positionToFVSToVariant[position].values()
                ):
                    c.sub(
                        uNameFromCodePoint(codePoint),
                        by=c.defaultVariant(charName, position),
                    )
