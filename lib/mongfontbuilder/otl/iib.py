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

    with c.Lookup(
        f"IIb.ligature",
        feature="rclt",
        flags={  # Prevent ligation
            "UseMarkFilteringSet": c.glyphClass(["nirugu.ignored", c.classes["fvs.ignored"]])
        },
    ):
        inputToLigatureAndRequired = dict[
            tuple[GlyphDescriptor, ...], tuple[GlyphDescriptor, bool]
        ]()
        for locale in c.locales:
            namespace = namespaceFromLocale(locale)
            vowelAliases = data.locales[locale].categories["vowel"]
            for category, ligatureToPositions in data.ligatures.items():
                for writtens, positions in ligatureToPositions.items():
                    for position in positions:
                        for input, ligature in iterLigatureSubstitutions(
                            c, writtens, position, locale
                        ):
                            if len(input) != 2:
                                continue
                            if required := category == "required":
                                # Check the second glyph, ignoring LVS:
                                codePoint = input[1].codePoints[0]
                                alias = data.aliases[unicodedata.name(chr(codePoint))]
                                if isinstance(alias, dict):
                                    alias = alias[namespace]
                                if alias not in vowelAliases:
                                    continue
                            # Deduplicate inputs:
                            inputToLigatureAndRequired[input] = ligature, required

        for input, (ligature, required) in inputToLigatureAndRequired.items():
            input = [str(i) for i in input]
            ligatureName = str(ligature)
            ligate = True
            if c.glyphs:
                if ligatureName in c.glyphs:
                    pass
                elif required:
                    componentName = str(GlyphDescriptor([], ligature.units, ligature.position))
                    c.spec.newGlyphs[c.glyphNameProcessor(ligatureName)] = GlyphSpec(
                        [c.glyphNameProcessor(componentName)]
                    )
                else:
                    ligate = False
            if ligate:
                c.sub(*input, by=ligatureName)

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


def iib2(c: MongFeaComposer) -> None:
    """
    **Phase IIb.2: Cleanup of format controls**

    Controls postprocessing.
    """

    with c.Lookup("IIb.controls.postprocessing", feature="rclt"):
        c.sub(
            c.input(
                c.glyphClass(["nirugu.ignored", c.classes["fvs.ignored"]]),
                c.conditions["_.reset"],
            ),
            by=None,
        )


def iib3(c: MongFeaComposer) -> None:
    """
    **Phase IIb.3: Optional treatments**

    Optional treatments.
    """
    pass


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
