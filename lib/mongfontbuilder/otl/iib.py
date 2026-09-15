from collections.abc import Iterator
from itertools import product
from typing import Literal

from fontTools import unicodedata

from .. import GlyphDescriptor, data, ligateParts, splitWrittens, writtenCombinations
from ..data.types import JoiningPosition, LocaleID
from ..spec import GlyphSpec
from ..utils import namespaceFromLocale
from . import MongFeaComposer


def compose(c: MongFeaComposer) -> None:
    iib1(c)
    iib2(c)
    iib3(c)


def constructWpA(c: MongFeaComposer) -> None:
    """Draw the `‹C›WpA` written form of Hudum Ali Gali from the two it is written with.

    Hudum Ali Gali writes a bowed written unit with a `Wp` and an `_a_` after it as one
    written form: the `‹C›O` ligature that the bow forms with the `Wp`, and the `_a_` in
    the shape it takes after a `Wp`.
    """

    if "MCHx" not in c.locales:
        return
    for consonant in WP_A_CONSONANTS:
        for position, basePosition in WP_A_POSITIONS:
            members = [f"_{consonant}O.{basePosition}", "_A.fina.Wp_"]
            if all(i in c.glyphs for i in members):
                c.spec.newGlyphs[f"_{consonant}WpA.{position}"] = GlyphSpec(members)


# The bowed written units of Hudum Ali Gali that take a `Wp` and an `_a_`.
WP_A_CONSONANTS = ["G", "K", "K2", "Bg", "Pg", "B"]

# The position of the `‹C›WpA` written form, and the position of the `‹C›O` ligature it is
# drawn from: the `_a_` of the written form is the one drawn after a `Wp`.
WP_A_POSITIONS = [("isol", "init"), ("fina", "medi")]


class LigatureCollector:
    """The ligatures of the ligature table, in the order they have to be written.

    A ligature may be written with the written form that a shorter ligature produces — the
    `‹C›WpA` of a bowed written unit with the `WpA` of the `Wp` and the `_a_` — so the
    written forms are taken from the shortest to the longest, and what a ligature produces
    is offered to the longer ones as an input. Inputs are deduplicated between writing
    systems, because they are written once for the font.
    """

    def __init__(self, c: MongFeaComposer) -> None:
        self.c = c
        self.substitutions = dict[tuple[GlyphDescriptor, ...], tuple[GlyphDescriptor, bool]]()
        self.writtenForms = dict[str, list[str]]()

    def collect(self) -> dict[tuple[GlyphDescriptor, ...], tuple[GlyphDescriptor, bool]]:
        for locale in self.c.locales:
            for category, ligatureToPositions in data.ligatures.items():
                self.collectCategory(locale, category, ligatureToPositions)
        return self.substitutions

    def collectCategory(
        self,
        locale: LocaleID,
        category: Literal["required", "optional"],
        ligatureToPositions: dict[str, list[JoiningPosition]],
    ) -> None:
        """Add the substitutions that the ligatures of one category have in *locale*.

        The written forms are taken from the shortest to the longest, because a longer
        written form may be written with what a shorter one produces.
        """

        for writtens, positions in sorted(
            ligatureToPositions.items(),
            key=lambda i: len(splitWrittens(i[0])),
        ):
            for position in positions:
                self.collectWrittenForm(locale, category, writtens, position)

    def collectWrittenForm(
        self,
        locale: LocaleID,
        category: str,
        writtens: str,
        position: JoiningPosition,
    ) -> None:
        """Add the substitutions that one written form has at one joining position."""

        required = category == "required"
        substitutions = iterLigatureSubstitutions(
            self.c, writtens, position, locale, self.writtenForms
        )
        for input, ligature in substitutions:
            if required and not isVowelFollower(locale, input):
                continue
            if existing := self.substitutions.get(input):
                assert existing == (ligature, required)
                continue
            self.substitutions[input] = ligature, required
            self.writtenForms[f"{''.join(ligature.units)}.{ligature.position}"] = [str(ligature)]


def isVowelFollower(locale: LocaleID, input: tuple[GlyphDescriptor, ...]) -> bool:
    """Whether the second glyph of *input* is a vowel, ignoring LVS.

    A glyph that is no character of its own — the written form that a shorter ligature
    produced — carries no alias of the writing system, and counts as one.
    """

    codePoint = input[1].codePoints[0]
    alias = data.aliases[unicodedata.name(chr(codePoint))]
    if isinstance(alias, dict):
        alias = alias.get(namespaceFromLocale(locale))
    return not isinstance(alias, str) or alias in data.locales[locale].categories["vowel"]


def iib1(c: MongFeaComposer) -> None:
    """
    **Phase IIb.1: Variation involving bowed written units**

    Ligatures.
    """

    constructWpA(c)

    with c.Lookup("IIb.ligature", feature="rclt"):
        for input, (ligature, _) in LigatureCollector(c).collect().items():
            implementLigature(c, input, ligature)

        if "MNGx" in c.locales:
            c.sub("u18A6.Wp.medi", "u1820.A.fina", by="u18A6_u1820.WpA.fina")
            c.sub("u188A.NG.init", "u1820.Aa.fina", by="u188A_u1820.NGAa.isol")
            c.sub("u188A.NG.medi", "u1820.Aa.fina", by="u188A_u1820.NGAa.fina")
        if "TODx" in c.locales:
            # TODO
            ...
        if "MCH" in c.locales:
            # TODO
            ...


def iterLigatureSubstitutions(
    c: MongFeaComposer,
    writtens: str,
    position: JoiningPosition,
    locale: LocaleID,
    writtenForms: dict[str, list[str]],
) -> Iterator[tuple[tuple[GlyphDescriptor, ...], GlyphDescriptor]]:
    for combination in writtenCombinations(splitWrittens(writtens), position):
        if len(combination) != 2:
            continue
        writtenLists = [
            [
                GlyphDescriptor.parse(glyph.glyph)
                for glyph in c.writtens(
                    locale,
                    *units.split("."),  # type: ignore
                ).glyphs
            ]
            or [GlyphDescriptor.parse(i) for i in writtenForms.get(units, [])]
            for units in combination
        ]
        for parts in product(*writtenLists):
            try:
                ligature = ligateParts([*parts])
            except KeyError:
                # The positions of these parts do not join — two final forms, for
                # example — so they form no ligature.
                continue
            yield parts, ligature


def implementLigature(
    c: MongFeaComposer,
    input: tuple[GlyphDescriptor, ...],
    ligature: GlyphDescriptor,
) -> None:
    inputNames = [str(i) for i in input]
    ligatureName = str(ligature)
    if c.glyphs and ligatureName not in c.glyphs:
        componentName = str(GlyphDescriptor([], ligature.units, ligature.position))
        if componentName not in c.glyphs and componentName not in c.spec.newGlyphs:
            # we don't check ligatures when generating, only generate OTL for existing glyphs,
            # so it's possible for the component to be missing.
            return
        c.spec.newGlyphs[c.glyphNameProcessor(ligatureName)] = GlyphSpec(
            [c.glyphNameProcessor(componentName)]
        )
    c.sub(*inputNames, by=ligatureName)


def iib2(c: MongFeaComposer) -> None:
    """
    **Phase IIb.2: Cleanup of format controls**

    A wide MVS renders as a plain space-like separator. At this final stage it is
    split into a non-breaking space followed by an ignored zero-width MVS. The
    `nbspace` and `mvs.ignored` glyphs themselves are created up front in
    `initControls`; only the split substitution happens here.

    - `nbspace` -- identical to `space`, carrying NO-BREAK SPACE U+00A0. Using a
      non-breaking space here keeps the MVS separator from allowing a line break,
      just as the space set before a punctuation mark.
    - `mvs.ignored` -- an ignored, zero-width glyph that preserves the MVS.

    The pair `nbspace` + `mvs.ignored` therefore takes the place of `mvs.wide`.
    """

    with c.Lookup("IIb.cleanup.mvs.wide", feature="rclt"):
        c.sub("mvs.wide", by=["nbspace", "mvs.ignored"])


def iib3(c: MongFeaComposer) -> None:
    """
    **Phase IIb.3: Optional treatments**

    Optional treatments.
    """
    pass
