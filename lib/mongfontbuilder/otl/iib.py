from collections.abc import Iterator
from itertools import product

from fontTools import unicodedata

from .. import GlyphDescriptor, data, ligateParts, splitWrittens, writtenCombinations
from ..data.misc import JoiningPosition
from ..data.types import LocaleID
from ..spec import GlyphSpec
from ..utils import namespaceFromLocale
from . import MongFeaComposer


def compose(c: MongFeaComposer) -> None:
    iib1(c)
    iib2(c)
    iib3(c)


def iib1(c: MongFeaComposer) -> None:
    """
    **Phase IIb.1: Variation involving bowed written units**

    Ligatures.
    """

    with c.Lookup(f"IIb.ligature", feature="rclt"):
        inputToLigatureAndRequired = dict[
            tuple[GlyphDescriptor, ...], tuple[GlyphDescriptor, bool]
        ]()
        for locale in c.locales:
            namespace = namespaceFromLocale(locale)
            vowelAliases = data.locales[locale].categories["vowel"]
            for category, ligatureToPositions in data.ligatures.items():
                required = category == "required"
                for writtens, positions in ligatureToPositions.items():
                    for position in positions:
                        for input, ligature in iterLigatureSubstitutions(
                            c, writtens, position, locale
                        ):
                            if len(input) != 2:
                                continue
                            if required:
                                # Check the second glyph, ignoring LVS:
                                codePoint = input[1].codePoints[0]
                                alias = data.aliases[unicodedata.name(chr(codePoint))]
                                if isinstance(alias, dict):
                                    alias = alias[namespace]
                                if alias not in vowelAliases:
                                    continue
                            # Deduplicate inputs between locales:
                            if existing := inputToLigatureAndRequired.get(input):
                                assert existing == (ligature, required)
                            else:
                                inputToLigatureAndRequired[input] = ligature, required

        for input, (ligature, required) in inputToLigatureAndRequired.items():
            implementLigature(c, input, ligature, required)

        if "MNGx" in c.locales:
            c.sub("u18A6.Wp.medi", "u1820.A.fina", by="u18A6_u1820.WpA.fina")
            c.sub("u188A.NG.init", "u1820.Aa.fina", by="u188A_u1820.NGAa.isol")
            c.sub("u188A.NG.medi", "u1820.Aa.fina", by="u188A_u1820.NGAa.fina")
        if "TODx" in c.locales:
            # TODO
            ...
        if "MCH" in c.locales:
            c.sub("u186F.Zs.init", "u1873.I.fina", by="u186F_u1873.Zs.isol")
            c.sub("u186F.Zs.medi", "u1873.I.fina", by="u186F_u1873.Zs.fina")


def iterLigatureSubstitutions(
    c: MongFeaComposer,
    writtens: str,
    position: JoiningPosition,
    locale: LocaleID,
) -> Iterator[tuple[tuple[GlyphDescriptor, ...], GlyphDescriptor]]:
    for combination in writtenCombinations(splitWrittens(writtens), position):
        writtenLists = [
            [
                GlyphDescriptor.parse(glyph.glyph)
                for glyph in c.writtens(
                    locale,
                    *units.split("."),  # type: ignore
                ).glyphs
            ]
            for units in combination
        ]
        for parts in product(*writtenLists):
            yield parts, ligateParts([*parts])


def implementLigature(
    c: MongFeaComposer,
    input: tuple[GlyphDescriptor, ...],
    ligature: GlyphDescriptor,
    required: bool,
) -> None:
    inputNames = [str(i) for i in input]
    ligatureName = str(ligature)
    if c.glyphs and ligatureName not in c.glyphs:
        componentName = str(GlyphDescriptor([], ligature.units, ligature.position))
        if componentName not in c.glyphs:
            if required:
                raise KeyError(componentName)
            else:
                return
        c.spec.newGlyphs[c.glyphNameProcessor(ligatureName)] = GlyphSpec(
            [c.glyphNameProcessor(componentName)]
        )
    c.sub(*inputNames, by=ligatureName)


def iib2(c: MongFeaComposer) -> None:
    """
    **Phase IIb.2: Cleanup of format controls**

    Optional treatments.
    """
    pass


def iib3(c: MongFeaComposer) -> None:
    """
    **Phase IIb.3: Optional treatments**

    Optional treatments.
    """
    pass
