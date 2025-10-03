from fontTools import unicodedata

from .. import GlyphDescriptor, data, uNameFromCodePoint
from ..data.misc import joiningPositions
from . import MongFeaComposer


def compose(c: MongFeaComposer) -> None:
    """
    **Phase IIa.1: Initiation of cursive positions**
    """

    localeSet = {*c.locales}
    for position in joiningPositions:
        with c.Lookup(f"IIa.{position}", feature=position):
            for charName, positionToFVSToVariant in data.variants.items():
                if any(
                    localeSet.intersection(i.locales)
                    for i in positionToFVSToVariant[position].values()
                ):
                    c.sub(
                        uNameFromCodePoint(ord(unicodedata.lookup(charName))),
                        by=str(GlyphDescriptor.fromData(charName, position)),
                    )
